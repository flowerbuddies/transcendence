from .ball import Ball
from .paddle import Paddle


class Player:
    def __init__(self, side):
        self.side = side
        self.score = 0
        self.paddle = Paddle(side)


class GameState:
    def __init__(self, isFourPlayer):
        self.ball = Ball()
        self.left = Player("left")
        self.right = Player("right")
        self.isFourPlayer = isFourPlayer
        if isFourPlayer:
            self.top = Player("top")
            self.bottom = Player("bottom")
        else:
            self.top = Player("wall_top")
            self.bottom = Player("wall_bottom")

    def update(self, dt):
        # check if goal scored, update score, reset ball
        self.handle_goal()

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
