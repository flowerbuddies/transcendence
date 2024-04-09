import json
from urllib.parse import unquote

from channels.generic.websocket import AsyncWebsocketConsumer


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]

        await self.channel_layer.group_add(self.lobby_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.lobby_name, self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send(self.lobby_name, json.loads(text_data))

    async def key(self, event):
        # for now just send back the key pressed
        # but later we'll process this and send players and ball positions instead
        await self.send(text_data=json.dumps(event))
