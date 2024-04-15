import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Lobby
from django.core.serializers import serialize


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

    # link the `AsyncWebsocketConsumer`'s channel_name with the db player
    @database_sync_to_async
    def set_channel_name(self, player_name):
        player = self.lobby.players.filter(name=player_name).first()
        player.channel_name = self.channel_name
        player.save()

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

    async def disconnect(self, _):
        await self.eliminate_player()
        await self.channel_layer.group_discard(self.lobby_name, self.channel_name)
        await self.send_players_list()

    async def receive(self, text_data):
        await self.channel_layer.group_send(self.lobby_name, json.loads(text_data))

    # type-based methods
    async def key(self, event):
        # for now just send back the key pressed
        # but later we'll process this and send players and ball positions instead
        await self.send(text_data=json.dumps(event))

    async def players(self, event):
        await self.send(text_data=json.dumps(event))

    async def init(self, event):
        await self.set_channel_name(event["player"])
