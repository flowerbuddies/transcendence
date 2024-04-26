import asyncio
from .ball import Ball
from .paddle import Paddle


class Player:
    def __init__(self, side, score):
        self.side = side
        self.score = score
        self.paddle = Paddle(side)


class GameState:
    def __init__(self, isFourPlayer, lobby):
        self.lobby = lobby
        self.is_started = False

        self.ball = Ball()

        self.left = Player("left", 0)
        self.right = Player("right", 0)
        self.isFourPlayer = isFourPlayer
        if isFourPlayer:
            self.top = Player("top", 0)
            self.bottom = Player("bottom", 0)
        else:
            self.top = Player("wall_top", 0)
            self.bottom = Player("wall_bottom", 0)

        self.players = {}

    def players_alive(self):
        alive_count = 0
        if self.left.score < 3:
            alive_count += 1
        if self.right.score < 3:
            alive_count += 1
        if not self.isFourPlayer:
            return alive_count != 1
        if self.top.score < 3:
            alive_count += 1
        if self.bottom.score < 3:
            alive_count += 1
        return alive_count != 1

    def get_winner(self):
        if self.left.score < 3:
            return self.left.side
        if self.right.score < 3:
            return self.right.side
        if self.top.score < 3:
            return self.top.side
        return self.bottom.side

    async def game_loop(self):
        server_frame_time = 0.0
        target_frame_time = 1.0 / 60.0
        while self.players_alive():
            start_time = asyncio.get_event_loop().time()

            # update and send state
            self.update(target_frame_time)
            await self.lobby.channel_layer.group_send(
                self.lobby.lobby_name, {"type": "scene", "scene": self.get_scene()}
            )

            # sleep to maintain client refresh rate
            server_frame_time = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, target_frame_time - server_frame_time)
            await asyncio.sleep(sleep_time)
            # self.fps_monitor.tick()

        #TODO connect side and player name so win screen can show the name of the player
        await self.lobby.channel_layer.group_send(
            self.lobby.lobby_name, {"type": "end", "winner": self.get_winner()}
        )

    def update(self, dt):
        # check if goal scored, update score, reset ball
        self.handle_goal()

        # check if players have died and make them into walls
        if self.isFourPlayer:
            self.transform_dead_players()

        # move paddles
        self.left.paddle.update(dt, self.isFourPlayer)
        self.right.paddle.update(dt, self.isFourPlayer)
        self.top.paddle.update(dt, self.isFourPlayer)
        self.bottom.paddle.update(dt, self.isFourPlayer)

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

    def transform_dead_players(self):
        #TODO mark dead players as eliminated
        if self.left.score == 3 and self.left.side != "wall_left":
            self.left = Player("wall_left", 3)
        if self.right.score == 3 and self.right.side != "wall_right":
            self.right = Player("wall_right", 3)
        if self.top.score == 3 and self.top.side != "wall_top":
            self.top = Player("wall_top", 3)
        if self.bottom.score == 3 and self.bottom.side != "wall_bottom":
            self.bottom = Player("wall_bottom", 3)

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
                self.ball.apply_accel = self.isFourPlayer
        else:
            if ortho_intersects(
                next.get_edge("left"), paddle.get_edge("top")
            ) or ortho_intersects(next.get_edge("right"), paddle.get_edge("top")):
                self.ball.dy *= -1
                self.ball.apply_accel = self.isFourPlayer

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
