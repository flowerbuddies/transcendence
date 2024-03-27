import json

from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("game", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("game", self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send("game", json.loads(text_data))

    async def key(self, event):
        # for now just send back the key pressed
        # but later we'll process this and send players and ball positions instead
        await self.send(text_data=json.dumps(event))
