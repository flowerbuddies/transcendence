import asyncio
from django.utils.translation import gettext as _
import math
from .ball import Ball
from .paddle import Paddle
from .ai import BehaviorTree



class Player:
    def __init__(self, side):
        self.side = side
        self.ready = False
        self.score = 0
        self.name = None
        self.ai = None
        self.paddle = Paddle(side)

    def change_side(self, side):
        self.side = side
        self.paddle = Paddle(side)

    def reset(self, is_four_player):
        self.score = 0
        self.name = None
        self.ai = None
        if self.side == "wall_right":
            self.change_side("right")
        if self.side == "wall_left":
            self.change_side("left")
        if self.side == "wall_top" and is_four_player:
            self.change_side("top")
        if self.side == "wall_bottom" and is_four_player:
            self.change_side("bottom")


class GameState:
    def __init__(self, is_four_player, is_tournament, lobby):
        self.lobby = lobby
        self.is_started = False

        self.ball = Ball()

        self.left = Player("left")
        self.right = Player("right")
        self.is_four_player = is_four_player
        self.is_tournament = is_tournament
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

    def mark_ai(self, names):
        for name in names:
            if self.left.name == name:
                self.left.ai = BehaviorTree(self, self.left)
            elif self.right.name == name:
                self.right.ai = BehaviorTree(self, self.right)
            elif self.top.name == name:
                self.top.ai = BehaviorTree(self, self.top)
            elif self.bottom.name == name:
                self.bottom.ai = BehaviorTree(self, self.bottom)

    def update_ai_players(self):
        if self.left.ai:
            self.left.ai.update()
        if self.right.ai:
            self.right.ai.update()
        if self.top.ai:
            self.top.ai.update()
        if self.bottom.ai:
            self.bottom.ai.update()

    async def set_up_match(self):
        self.assign_player_names()
        await self.lobby.channel_layer.group_send(
            self.lobby.lobby_name,
            {
                "type": "scene",
                "scene": self.get_start_scene(),
                "is_tournament": self.is_tournament,
            },
        )

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
        while self.players_alive():
            start_time = asyncio.get_event_loop().time()

            # update and send state
            self.update_ai_players()
            await self.update(target_frame_time)
            await self.lobby.channel_layer.group_send(
                self.lobby.lobby_name,
                {
                    "type": "scene",
                    "scene": self.get_scene(),
                    "is_tournament": self.is_tournament,
                },
            )

            # sleep to maintain client refresh rate
            server_frame_time = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, target_frame_time - server_frame_time)
            await asyncio.sleep(sleep_time)

        await self.lobby.channel_layer.group_send(
            self.lobby.lobby_name,
            {
                "type": "end",
                "winner": _("%(player)s won the match woo!")
                % {"player": self.get_winner()},
            },
        )
        return self.get_winner()

    def reset_game(self):
        self.left.reset(self.is_four_player)
        self.right.reset(self.is_four_player)
        self.top.reset(self.is_four_player)
        self.bottom.reset(self.is_four_player)
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
        if (
            self.bottom.score == self.score_to_lose
            and self.bottom.side != "wall_bottom"
        ):
            await self.lobby.channel_layer.send(
                self.lobby.channel_name, {"type": "kill", "target": self.bottom.name}
            )
            self.bottom.change_side("wall_bottom")

    def handle_collisions(self, dt):
        next = self.ball.next_position(self.ball.dx, self.ball.dy, dt)
        if self.was_collision(next):
            return
        intermediate_dx = lerp(self.ball.x, next.x, 0.5)
        intermediate_dy = lerp(self.ball.y, next.y, 0.5)
        intermediate = self.ball.next_position(intermediate_dx, intermediate_dy, dt)
        if self.was_collision(intermediate):
            return

    def was_collision(self, next):
        return (
            self.handle_paddle_collision(next, self.left.paddle)
            or self.handle_paddle_collision(next, self.right.paddle)
            or self.handle_paddle_collision(next, self.top.paddle)
            or self.handle_paddle_collision(next, self.bottom.paddle)
        )

    def handle_paddle_collision(self, next, paddle):
        # depending on the direction of the ball, check the paddle's ball-facing edge
        # check one edge of the paddle against both orthogonal edges of the ball
        # if a collision occurs, invert the orthogonal velocity and set next update to apply acceleration
        # return True if a collision occurs, else False
        if self.ball.dx < 0.0:
            if ortho_intersects(
                paddle.get_edge("right"), next.get_edge("top")
            ) or ortho_intersects(paddle.get_edge("right"), next.get_edge("bottom")):
                self.ball.dx *= -1
                self.ball.apply_accel = True
                return True
        else:
            if ortho_intersects(
                paddle.get_edge("left"), next.get_edge("top")
            ) or ortho_intersects(paddle.get_edge("left"), next.get_edge("bottom")):
                self.ball.dx *= -1
                self.ball.apply_accel = True
                return True
        if self.ball.dy < 0.0:
            if ortho_intersects(
                next.get_edge("left"), paddle.get_edge("bottom")
            ) or ortho_intersects(next.get_edge("right"), paddle.get_edge("bottom")):
                self.ball.dy *= -1
                self.ball.apply_accel = self.is_four_player
                return True
        else:
            if ortho_intersects(
                next.get_edge("left"), paddle.get_edge("top")
            ) or ortho_intersects(next.get_edge("right"), paddle.get_edge("top")):
                self.ball.dy *= -1
                self.ball.apply_accel = self.is_four_player
                return True
        return False

    def get_scene(self):
        # returns an array of clientside-supported objects for displaying the gamestate
        scene = []

        self.ball_to_scene(scene)

        self.player_to_scene(self.left, scene, True)
        self.player_to_scene(self.right, scene, True)
        self.player_to_scene(self.top, scene, True)
        self.player_to_scene(self.bottom, scene, True)
        return scene

    def get_start_scene(self):
        scene = []

        self.player_to_scene(self.left, scene, False)
        self.player_to_scene(self.right, scene, False)
        self.player_to_scene(self.top, scene, False)
        self.player_to_scene(self.bottom, scene, False)
        return scene

    def ball_to_scene(self, scene):
        speed = self.ball.get_speed()
        diminished = 255 - 255 * speed / self.ball.max_speed
        # add ball trail to scene
        for index, segment in enumerate(self.ball.trail):
            segment["type"] = "trail"
            segment["width"] = 2 * self.ball.radius
            segment["height"] = 2 * self.ball.radius
            alpha = 1 - index / self.ball.max_trail_len
            segment["color"] = f"rgba(255, {diminished}, {diminished}, {alpha})"
            scene.append(segment)

        # add ball to scene
        scene.append(
            {
                "type": "ball",
                "x": self.ball.x,
                "y": self.ball.y,
                "width": 2 * self.ball.radius,
                "height": 2 * self.ball.radius,
            }
        )

    def player_to_scene(self, player, scene, with_paddle):
        scene.append(
            {
                "type": "score",
                "name": player.name,
                "elimination_msg": _("eliminated"),
                "ball_msg": _("balls missed %(score)s/3") % {"score": player.score},
                "side": player.side,
                "score": player.score,
            }
        )
        if with_paddle:
            self.paddle_to_scene(player.paddle, scene)

    def paddle_to_scene(self, paddle, scene):
        is_vertical_paddle = (
            paddle.side == "left"
            or paddle.side == "right"
            or paddle.side == "wall_left"
            or paddle.side == "wall_right"
        )
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


# linearly interpolate by an amount between start and end
def lerp(start, end, amount):
    return start + amount * (end - start)
