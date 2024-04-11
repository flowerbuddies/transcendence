import asyncio
import json
from urllib.parse import unquote
from .game.game import GameState

from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.gs = GameState(False)
        self.gs = GameState(True)

    async def connect(self):
        self.game_name = self.scope["url_route"]["kwargs"]["game_name"]

        await self.channel_layer.group_add(self.game_name, self.channel_name)
        await self.accept()
        self.loop_task = asyncio.create_task(self.loop())

    async def disconnect(self, close_code):
        if self.loop_task:
            self.loop_task.cancel()
        await self.channel_layer.group_discard(self.game_name, self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send(self.game_name, json.loads(text_data))

    async def key(self, event):
        if event["side"] == "left":
            if event["key"] == 1:
                self.gs.left.paddle.is_up_pressed = (
                    not self.gs.left.paddle.is_up_pressed
                )
            elif event["key"] == 2:
                self.gs.left.paddle.is_down_pressed = (
                    not self.gs.left.paddle.is_down_pressed
                )

    async def loop(self):
        target_fps = 60
        frame_time = 1 / target_fps
        delta_time = 0
        while True:
            start_time = asyncio.get_event_loop().time()

            # update and send state
            self.gs.update(delta_time)
            await self.send(text_data=json.dumps(self.gs.getScene()))

            delta_time = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, frame_time - delta_time)
            await asyncio.sleep(sleep_time)
