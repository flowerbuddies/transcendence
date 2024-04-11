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

    def update(self, dt):
        # check if goal scored, update score, reset ball
        self.handle_goal()

        # move paddles
        self.left.paddle.update(dt)
        self.right.paddle.update(dt)
        if self.isFourPlayer:
            self.top.paddle.update(dt)
            self.bottom.paddle.update(dt)

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
        elif self.isFourPlayer and self.ball.y < 0.0:
            self.top.score += 1
            self.ball.reset()
        elif self.isFourPlayer and self.ball.y + 2 * self.ball.radius > 1.0:
            self.bottom.score += 1
            self.ball.reset()

    def handle_collisions(self, dt):
        next = self.ball.next_position(dt)

        # if walls exist, check if wall bounce
        if not self.isFourPlayer:
            self.check_wall_collision(next)

        # check paddle collisions
        # TODO: increase acceleration when paddle collision occurs
        self.handle_paddle_collision(next)

    def check_wall_collision(self, next):
        top_wall = (0, 0, 1, 0)
        bottom_wall = (0, 1, 1, 1)
        if (
            ortho_intersects(next.get_edge("left"), top_wall)
            or ortho_intersects(next.get_edge("right"), top_wall)
            or ortho_intersects(next.get_edge("left"), bottom_wall)
            or ortho_intersects(next.get_edge("right"), bottom_wall)
        ):
            self.ball.dy *= -1

    def handle_paddle_collision(self, next):
        if self.ball.dx < 0.0:
            if (
                ortho_intersects(
                    self.left.paddle.get_edge("right"), next.get_edge("top")
                )
                or ortho_intersects(
                    self.left.paddle.get_edge("right"), next.get_edge("bottom")
                )
                or ortho_intersects(
                    self.left.paddle.get_edge("left"), next.get_edge("top")
                )
                or ortho_intersects(
                    self.left.paddle.get_edge("left"), next.get_edge("bottom")
                )
            ):
                self.ball.dx *= -1
        else:
            if (
                ortho_intersects(
                    self.right.paddle.get_edge("left"), next.get_edge("top")
                )
                or ortho_intersects(
                    self.right.paddle.get_edge("left"), next.get_edge("bottom")
                )
                or ortho_intersects(
                    self.right.paddle.get_edge("right"), next.get_edge("top")
                )
                or ortho_intersects(
                    self.right.paddle.get_edge("right"), next.get_edge("bottom")
                )
            ):
                self.ball.dx *= -1
        if self.isFourPlayer:
            if self.ball.dy < 0.0:
                if (
                    ortho_intersects(
                        next.get_edge("left"), self.top.paddle.get_edge("bottom")
                    )
                    or ortho_intersects(
                        next.get_edge("right"), self.top.paddle.get_edge("bottom")
                    )
                    or ortho_intersects(
                        next.get_edge("left"), self.top.paddle.get_edge("top")
                    )
                    or ortho_intersects(
                        next.get_edge("right"), self.top.paddle.get_edge("top")
                    )
                ):
                    self.ball.dy *= -1
            else:
                if (
                    ortho_intersects(
                        next.get_edge("left"),
                        self.bottom.paddle.get_edge("top"),
                    )
                    or ortho_intersects(
                        next.get_edge("right"),
                        self.bottom.paddle.get_edge("top"),
                    )
                    or ortho_intersects(
                        next.get_edge("left"),
                        self.bottom.paddle.get_edge("bottom"),
                    )
                    or ortho_intersects(
                        next.get_edge("right"),
                        self.bottom.paddle.get_edge("bottom"),
                    )
                ):
                    self.ball.dy *= -1

    def getScene(self):
        scene = []
        scene.append(
            {
                "type": "ball",
                "x": self.ball.x,
                "y": self.ball.y,
                "width": self.ball.radius * 2,
                "height": self.ball.radius * 2,
            }
        )

        scene.append(
            {
                "type": "left",
                "x": self.left.paddle.x,
                "y": self.left.paddle.y,
                "width": self.left.paddle.depth,
                "height": self.left.paddle.length,
            }
        )
        scene.append(
            {
                "type": "right",
                "x": self.right.paddle.x,
                "y": self.right.paddle.y,
                "width": self.right.paddle.depth,
                "height": self.right.paddle.length,
            }
        )

        if hasattr(self, "top"):
            scene.append(
                {
                    "type": "top",
                    "x": self.top.paddle.x,
                    "y": self.top.paddle.y,
                    "width": self.top.paddle.length,
                    "height": self.top.paddle.depth,
                }
            )
        if hasattr(self, "bottom"):
            scene.append(
                {
                    "type": "bottom",
                    "x": self.bottom.paddle.x,
                    "y": self.bottom.paddle.y,
                    "width": self.bottom.paddle.length,
                    "height": self.bottom.paddle.depth,
                }
            )
        return scene


# check if a vertical and horizontal line intersect
def ortho_intersects(vertical, horizontal):
    vx, vy1, _, vy2 = vertical
    hx1, hy, hx2, _ = horizontal
    return hx1 <= vx <= hx2 and vy1 <= hy <= vy2
