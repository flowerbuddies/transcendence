import asyncio
import json
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

    # link the `AsyncWebsocketConsumer`'s channel_name with the db player and the game state
    @database_sync_to_async
    def init_player(self, player_name):
        player = self.lobby.players.filter(name=player_name).first()
        player.channel_name = self.channel_name
        player.save()
        channel_to_lobby[self.channel_name] = player.lobby.name
        if player.lobby.name not in lobby_to_gs:
            lobby_to_gs[player.lobby.name] = GameState(False, self)

            # lobby_to_gs[player.lobby.name].loop.create_task(
            #     lobby_to_gs[player.lobby.name].game_loop()
            # )
            # print(player.lobby.name)
            # print(lobby_to_gs[player.lobby.name])
            # asyncio.run(lobby_to_gs[player.lobby.name].game_loop())

            # async def tmp():
            #     # await task

            # tmp()

            # asyncio.run(tmp())

    # async def start_game_if_full(self):

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

    # WS base methods
    async def connect(self):
        self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]
        if not self.lobby:
            self.lobby = await self.get_lobby()

        await self.channel_layer.group_add(self.lobby_name, self.channel_name)
        await self.accept()

        # when a player connect to a lobby, send the list players to all connected players
        await self.send_players_list()
        # if len(self.lobby.players.all()) == self.lobby.max_players:

    async def disconnect(self, _):
        await self.eliminate_player()
        await self.channel_layer.group_discard(self.lobby_name, self.channel_name)
        await self.send_players_list()

    async def receive(self, text_data):
        data = json.loads(text_data)
        match data["type"]:
            case "init":
                await self.init_player(data["player"])
                # await self.start_game_if_full()
            case "key":
                await self.key(data["key"])
            case "ready":
                await self.start_game()

    async def key(self, key):
        gs = self.get_game_state()
        if key == 1:
            gs.left.paddle.is_up_pressed = not gs.left.paddle.is_up_pressed
        elif key == 2:
            gs.left.paddle.is_down_pressed = not gs.left.paddle.is_down_pressed

    async def players(self, event):
        await self.send(text_data=json.dumps(event))

    async def scene(self, event):
        await self.send(text_data=json.dumps(event))

    async def start_game(self):
        if not self.get_game_state().is_started:
            asyncio.create_task(lobby_to_gs[self.lobby.name].game_loop())
            self.get_game_state().is_started = True

    def get_game_state(self):
        return lobby_to_gs[channel_to_lobby[self.channel_name]]


# TODO: when the game is finished, remove the gs
