import asyncio
import json
from channels.db import database_sync_to_async
from .game.game import GameState
from .tournament import Tournament

from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Lobby
from django.core.serializers import serialize

channel_to_lobby = {}
lobby_to_gs = {}  # gs stands for game state


class LobbyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lobby = None

    @database_sync_to_async
    def get_lobby(self):
        return Lobby.objects.filter(name=self.lobby_name).first()

    @database_sync_to_async
    def get_players(self):
        # serilize the Player models into a json string, than a dict
        json_players = json.loads(serialize("json", self.lobby.players.all()))
        return (
            # we only care about the model's fields
            list(map(lambda player: player["fields"], json_players)),
            self.lobby.max_players,
        )

    @database_sync_to_async
    def get_alive_players(self):
        return list(self.lobby.players.filter(is_eliminated=False))

    @database_sync_to_async
    def is_match_four(self):
        return self.lobby.is_match_four
    
    @database_sync_to_async
    def is_tournament(self):
        return self.lobby.is_tournament

    # link the `AsyncWebsocketConsumer`'s channel_name with the db player and the game state
    @database_sync_to_async
    def init_player(self, player_name):
        player = self.lobby.players.filter(name=player_name).first()
        player.channel_name = self.channel_name
        player.save()
        channel_to_lobby[self.channel_name] = player.lobby.name

    @database_sync_to_async
    def is_ready_to_start(self):
        return len(self.lobby.players.all()) == self.lobby.max_players

    # mark player as disconnected
    @database_sync_to_async
    def disconnect_player(self):
        player = self.lobby.players.filter(channel_name=self.channel_name).first()
        if not player or player.is_disconnected:
            return
        player.is_disconnected = True
        player.is_eliminated = True
        player.save()

    @database_sync_to_async
    def kill_by_name(self, player_name):
        player = self.lobby.players.filter(name=player_name).first()
        if not player or player.is_eliminated:
            return
        player.is_eliminated = True
        player.save()

    @database_sync_to_async
    def is_lobby_empty(self):
       return len(self.lobby.players.filter(is_disconnected=False)) == 0

    @database_sync_to_async
    def delete_lobby(self):
       self.lobby.delete()

    async def send_players_list(self):
        players, max_players = await self.get_players()
        await self.channel_layer.group_send(
            self.lobby_name, {"type": "players", "players": sorted(players, key=lambda item: item["is_eliminated"]), "max": max_players}
        )

    async def connect(self):
        self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]
        if not self.lobby:
            self.lobby = await self.get_lobby()

        await self.channel_layer.group_add(self.lobby_name, self.channel_name)
        await self.accept()

        # when a player connect to a lobby, send the list players to all connected players
        await self.send_players_list()

    async def disconnect(self, _):
        await self.disconnect_player()
        await self.channel_layer.group_discard(self.lobby_name, self.channel_name)
        if await self.is_lobby_empty():
           await self.delete_lobby()
        else:
            await self.send_players_list()

    async def receive(self, text_data):
        data = json.loads(text_data)

        match data["type"]:
            case "init":
                await self.init_player(data["player"])
                if await self.is_ready_to_start():
                    await self.start_game()
            case "key":
                await self.key(data)

    async def key(self, data):
        gs = self.get_game_state()
        if not gs:
            return
        if data["player"] not in gs.players:
            return
        player = gs.players[data["player"]]

        if data["key"] == 1:
            player.paddle.is_up_pressed = not player.paddle.is_up_pressed
        elif data["key"] == 2:
            player.paddle.is_down_pressed = not player.paddle.is_down_pressed

    async def players(self, event):
        await self.send(text_data=json.dumps(event))

    async def time(self, event):
        await self.send(text_data=json.dumps(event))

    async def scene(self, event):
        await self.send(text_data=json.dumps(event))

    async def end(self, event):
        await self.send(text_data=json.dumps(event))

    async def winner(self, event):
        await self.send(text_data=json.dumps(event))

    async def next_match(self, event):
        await self.send(text_data=json.dumps(event))

    async def kill(self, event):
        await self.kill_by_name(event["target"])
        await self.send_players_list()

    async def send_tournament_winner(self, name):
        await self.channel_layer.group_send(
            self.lobby_name, {"type": "winner", "winner": name}
        )

    async def update_next_match_info(self, index):
        amount = 2
        if await self.is_match_four():
            amount = 4
        players = []
        match = self.tournament.get_match(index)
        if match:
            for player in match.players:
                players.append(player)
        await self.channel_layer.group_send(
            self.lobby_name, {"type": "next_match", "players": players, "amount": amount}
        )

    def end_game(self, _):
        pass

    async def match_timer(self):
        seconds = 3
        while seconds != -1:
            await self.channel_layer.group_send(
                self.lobby_name, {"type": "time", "seconds": seconds}
            )
            if seconds != 0:
                await asyncio.sleep(1)
            seconds -= 1

    async def run_matches(self):
        match_index = 0
        while match_index != self.tournament.get_match_count():
            self.tournament.assign_player_positions(self.get_game_state(), match_index)
            await self.update_next_match_info(match_index + 1)
            await lobby_to_gs[self.lobby.name].set_up_match()
            await self.match_timer()
            match_winner = await lobby_to_gs[self.lobby.name].game_loop()
            self.tournament.set_match_winner(match_index, match_winner)
            await self.update_next_match_info(match_index + 1)
            lobby_to_gs[self.lobby.name].reset_game()
            match_index += 1
            
        if await self.is_tournament():
            await self.send_tournament_winner(match_winner)

    async def start_game(self):
        if not self.get_game_state():
            lobby_to_gs[self.lobby.name] = GameState(await self.is_match_four(), await self.is_tournament(), self)

        gs = self.get_game_state()
        if not gs.is_started:
            gs.is_started = True
            alive_players = await self.get_alive_players()
            alive_player_names = list(map(lambda player: player.name, alive_players))
            self.tournament = Tournament(gs, alive_player_names, gs.is_four_player)
            self.tournament.get_match_count()
            self.tournament.start_tournament()
            task = asyncio.create_task(self.run_matches())
            task.add_done_callback(self.end_game)

    def get_game_state(self):
        try:
            return lobby_to_gs[channel_to_lobby[self.channel_name]]
        except:
            return None


# TODO: when the game is finished, remove the gs, cancel the task
