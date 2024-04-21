import asyncio
import json
import random
from channels.db import database_sync_to_async
from .game.game import GameState

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

    # eliminate a player
    @database_sync_to_async
    def eliminate_player(self):
        player = self.lobby.players.filter(channel_name=self.channel_name).first()
        player.is_eliminated = True
        player.save()

    async def send_players_list(self):
        players, max_players = await self.get_players()
        await self.channel_layer.group_send(
            self.lobby_name, {"type": "players", "players": players, "max": max_players}
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
        await self.eliminate_player()
        await self.channel_layer.group_discard(self.lobby_name, self.channel_name)
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
        if not data["player"] in gs.players:
            return
        player = gs.players[data["player"]]

        if data["key"] == 1:
            player.paddle.is_up_pressed = not player.paddle.is_up_pressed
        elif data["key"] == 2:
            player.paddle.is_down_pressed = not player.paddle.is_down_pressed

    async def players(self, event):
        await self.send(text_data=json.dumps(event))

    async def scene(self, event):
        await self.send(text_data=json.dumps(event))

    async def start_game(self):
        if not self.get_game_state():
            lobby_to_gs[self.lobby.name] = GameState(await self.is_match_four(), self)

        gs = self.get_game_state()
        if not gs.is_started:
            # TODO: this needs to run for every match
            alive_players = await self.get_alive_players()
            alive_player_names = list(map(lambda player: player.name, alive_players))
            match_type = 4 if await self.is_match_four() else 2
            selected_players = random.sample(alive_player_names, match_type)

            gs.players[selected_players[0]] = gs.left
            gs.players[selected_players[1]] = gs.right
            if match_type == 4:
                gs.players[selected_players[2]] = gs.top
                gs.players[selected_players[3]] = gs.bottom

            asyncio.create_task(lobby_to_gs[self.lobby.name].game_loop())
            gs.is_started = True

    def get_game_state(self):
        try:
            return lobby_to_gs[channel_to_lobby[self.channel_name]]
        except:
            return None


# TODO: when the game is finished, remove the gs, cancel the task
