import asyncio
import json
from urllib.parse import unquote
from .game.game import GameState
from .game.performance import FPSMonitor

from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gs = GameState(False)
        # self.gs = GameState(True)
        self.fps_monitor = FPSMonitor()
        self.client_frame_time = 1.0 / 60.0

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
        data = json.loads(text_data)
        if data["type"] == "frame_time":
            # set client_frame_time to actual or sensible value. Avoids long "load" time when game starts
            self.client_frame_time = clamp(data["time"] / 1000.0, 0.0, 1.0 / 30.0)
        else:
            await self.channel_layer.group_send(self.game_name, data)

    # TODO: refactor with keymap; (request from client on game start)
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
        if event["side"] == "right":
            if event["key"] == 3:
                self.gs.right.paddle.is_up_pressed = (
                    not self.gs.right.paddle.is_up_pressed
                )
            elif event["key"] == 4:
                self.gs.right.paddle.is_down_pressed = (
                    not self.gs.right.paddle.is_down_pressed
                )
        if event["side"] == "top":
            if event["key"] == 5:
                self.gs.top.paddle.is_up_pressed = not self.gs.top.paddle.is_up_pressed
            elif event["key"] == 6:
                self.gs.top.paddle.is_down_pressed = (
                    not self.gs.top.paddle.is_down_pressed
                )
        if event["side"] == "bottom":
            if event["key"] == 7:
                self.gs.bottom.paddle.is_up_pressed = (
                    not self.gs.bottom.paddle.is_up_pressed
                )
            elif event["key"] == 8:
                self.gs.bottom.paddle.is_down_pressed = (
                    not self.gs.bottom.paddle.is_down_pressed
                )

    async def loop(self):
        server_frame_time = 0
        while True:
            start_time = asyncio.get_event_loop().time()

            # update and send state
            self.gs.update(self.client_frame_time)
            await self.send(text_data=json.dumps(self.gs.get_scene()))

            # sleep to maintain client refresh rate
            server_frame_time = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, self.client_frame_time - server_frame_time)
            await asyncio.sleep(sleep_time)
            # print(f"client: {self.client_frame_time}, server: {server_frame_time}")
            # self.fps_monitor.tick()


# constrain 'value' to between 'min_value' and 'max_value'
clamp = lambda value, min_value, max_value: max(min(value, max_value), min_value)
