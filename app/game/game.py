import asyncio
from .ball import Ball
from .paddle import Paddle


class Player:
    def __init__(self, side):
        self.side = side
        self.score = 0
        self.name = None
        self.paddle = Paddle(side)

    def change_side(self, side):
        self.side = side
        self.paddle = Paddle(side)

    def reset(self):
        self.score = 0
        self.name = None


class GameState:
    def __init__(self, is_four_player, is_tournament, lobby):
        self.lobby = lobby
        self.is_started = False

        self.ball = Ball()

        self.left = Player("left")
        self.right = Player("right")
        self.is_four_player = is_four_player
        self.score_to_lose = 3
        if is_tournament:
            self.score_to_lose = 1
        if is_four_player:
            self.top = Player("top")
            self.bottom = Player("bottom")
        else:
            self.top = Player("wall_top")
            self.bottom = Player("wall_bottom")

        self.players = {}

    def assign_player_names(self):
        for player in self.players:
            self.players[player].name = player

    def players_alive(self):
        alive_count = 0
        if self.left.score < self.score_to_lose:
            alive_count += 1
        if self.right.score < self.score_to_lose:
            alive_count += 1
        if not self.is_four_player:
            return alive_count != 1
        if self.top.score < self.score_to_lose:
            alive_count += 1
        if self.bottom.score < self.score_to_lose:
            alive_count += 1
        return alive_count != 1

    def get_winner(self):
        if self.left.score < self.score_to_lose:
            return self.left.name
        if self.right.score < self.score_to_lose:
            return self.right.name
        if self.top.score < self.score_to_lose:
            return self.top.name
        return self.bottom.name

    async def game_loop(self):
        server_frame_time = 0.0
        target_frame_time = 1.0 / 60.0
        self.assign_player_names()
        while self.players_alive():
            start_time = asyncio.get_event_loop().time()

            # update and send state
            await self.update(target_frame_time)
            await self.lobby.channel_layer.group_send(
                self.lobby.lobby_name, {"type": "scene", "scene": self.get_scene()}
            )

            # sleep to maintain client refresh rate
            server_frame_time = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, target_frame_time - server_frame_time)
            await asyncio.sleep(sleep_time)
            # self.fps_monitor.tick()

        await self.lobby.channel_layer.group_send(
            self.lobby.lobby_name, {"type": "end", "winner": self.get_winner()}
        )
        return self.get_winner()

    def reset_game(self):
        self.left.reset()
        self.right.reset()
        self.top.reset()
        self.bottom.reset()
        self.players = {}

    async def update(self, dt):
        # check if goal scored, update score, reset ball
        self.handle_goal()

        # check if players have died and make them into walls
        await self.transform_dead_players()

        # move paddles
        self.left.paddle.update(dt, self.is_four_player)
        self.right.paddle.update(dt, self.is_four_player)
        self.top.paddle.update(dt, self.is_four_player)
        self.bottom.paddle.update(dt, self.is_four_player)

        # set ball dx, dy according to collisions occuring next dt
        self.handle_collisions(dt)

        # move ball
        self.ball.update(dt)

    def handle_goal(self):
        if self.ball.x < 0.0:
            self.left.score += 1
            self.ball.reset()
        elif self.ball.x + 2 * self.ball.radius > 1.0:
            self.right.score += 1
            self.ball.reset()
        elif self.ball.y < 0.0:
            self.top.score += 1
            self.ball.reset()
        elif self.ball.y + 2 * self.ball.radius > 1.0:
            self.bottom.score += 1
            self.ball.reset()

    async def transform_dead_players(self):
        #TODO potentially refactor into two functions, where the async part is it's separate function
        if self.left.score == self.score_to_lose and self.left.side != "wall_left":
            await self.lobby.channel_layer.send(
                self.lobby.channel_name, {"type": "kill", "target": self.left.name}
            )
            if self.is_four_player:
                self.left.change_side("wall_left")
        if self.right.score == self.score_to_lose and self.right.side != "wall_right":
            await self.lobby.channel_layer.send(
                self.lobby.channel_name, {"type": "kill", "target": self.right.name}
            )
            if self.is_four_player:
                self.right.change_side("wall_right")
        if not self.is_four_player:
            return
        if self.top.score == self.score_to_lose and self.top.side != "wall_top":
            await self.lobby.channel_layer.send(
                self.lobby.channel_name, {"type": "kill", "target": self.top.name}
            )
            self.top.change_side("wall_top")
        if self.bottom.score == self.score_to_lose and self.bottom.side != "wall_bottom":
            await self.lobby.channel_layer.send(
                self.lobby.channel_name, {"type": "kill", "target": self.bottom.name}
            )
            self.bottom.change_side("wall_bottom")

    def handle_collisions(self, dt):
        # check the next ball's position for collision with paddles
        next = self.ball.next_position(dt)
        self.handle_paddle_collision(next, self.left.paddle)
        self.handle_paddle_collision(next, self.right.paddle)
        self.handle_paddle_collision(next, self.top.paddle)
        self.handle_paddle_collision(next, self.bottom.paddle)

    def handle_paddle_collision(self, next, paddle):
        # depending on the direction of the ball, check the paddle's ball-facing edge
        # check one edge of the paddle against both orthogonal edges of the ball
        # if a collision occurs, invert the orthogonal velocity and set next update to apply acceleration
        if self.ball.dx < 0.0:
            if ortho_intersects(
                paddle.get_edge("right"), next.get_edge("top")
            ) or ortho_intersects(paddle.get_edge("right"), next.get_edge("bottom")):
                self.ball.dx *= -1
                self.ball.apply_accel = True
        else:
            if ortho_intersects(
                paddle.get_edge("left"), next.get_edge("top")
            ) or ortho_intersects(paddle.get_edge("left"), next.get_edge("bottom")):
                self.ball.dx *= -1
                self.ball.apply_accel = True
        if self.ball.dy < 0.0:
            if ortho_intersects(
                next.get_edge("left"), paddle.get_edge("bottom")
            ) or ortho_intersects(next.get_edge("right"), paddle.get_edge("bottom")):
                self.ball.dy *= -1
                self.ball.apply_accel = self.is_four_player
        else:
            if ortho_intersects(
                next.get_edge("left"), paddle.get_edge("top")
            ) or ortho_intersects(next.get_edge("right"), paddle.get_edge("top")):
                self.ball.dy *= -1
                self.ball.apply_accel = self.is_four_player

    def get_scene(self):
        # returns an array of clientside-supported objects for displaying the gamestate
        scene = []

        self.ball_to_scene(scene)

        self.player_to_scene(self.left, scene)
        self.player_to_scene(self.right, scene)
        self.player_to_scene(self.top, scene)
        self.player_to_scene(self.bottom, scene)
        return scene

    def ball_to_scene(self, scene):
        for index, segment in enumerate(self.ball.trail):
            segment["type"] = "trail"
            segment["width"] = 2 * self.ball.radius
            segment["height"] = 2 * self.ball.radius
            alpha = 1 - index / self.ball.max_trail_len
            segment["color"] = f"rgba(255, 255, 255, {alpha})"
            scene.append(segment)

        scene.append(
            {
                "type": "ball",
                "x": self.ball.x,
                "y": self.ball.y,
                "width": self.ball.radius * 2,
                "height": self.ball.radius * 2,
            }
        )

    def player_to_scene(self, player, scene):
        scene.append(
            {
                "type": "score",
                "name": player.name,
                "side": player.side,
                "score": player.score,
            }
        )
        self.paddle_to_scene(player.paddle, scene)

    def paddle_to_scene(self, paddle, scene):
        is_vertical_paddle = paddle.side == "left" or paddle.side == "right"
        scene.append(
            {
                "type": "paddle",
                "side": paddle.side,
                "x": paddle.x,
                "y": paddle.y,
                "width": (paddle.depth if is_vertical_paddle else paddle.length),
                "height": (paddle.length if is_vertical_paddle else paddle.depth),
            }
        )


# check if a vertical and horizontal line intersect
def ortho_intersects(vertical, horizontal):
    vx, vy1, _, vy2 = vertical
    hx1, hy, hx2, _ = horizontal
    return hx1 <= vx <= hx2 and vy1 <= hy <= vy2
