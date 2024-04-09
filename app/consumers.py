import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import Lobby
from django.core.serializers import serialize


class LobbyConsumer(AsyncWebsocketConsumer):
    # utility methods
    @database_sync_to_async
    def get_players(self):
        lobby = Lobby.objects.filter(name=self.lobby_name).first()
        lobby_players = lobby.players.all()
        json_players = json.loads(serialize("json", lobby_players))
        return (
            list(map(lambda player: player["fields"], json_players)),
            lobby.max_players,
        )

    # WS base methods
    async def connect(self):
        self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]

        await self.channel_layer.group_add(self.lobby_name, self.channel_name)
        await self.accept()

        # when a player connect to a lobby, send the list players to all connected players
        players, max_players = await self.get_players()
        await self.channel_layer.group_send(
            self.lobby_name, {"type": "players", "players": players, "max": max_players}
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.lobby_name, self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send(self.lobby_name, json.loads(text_data))

    # type-based methods
    async def key(self, event):
        # for now just send back the key pressed
        # but later we'll process this and send players and ball positions instead
        await self.send(text_data=json.dumps(event))

    async def players(self, event):
        await self.send(text_data=json.dumps(event))
