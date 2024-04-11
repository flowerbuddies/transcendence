import random


class Player:
    def __init__(self, side):
        self.side = side
        self.score = 0
        self.paddle = Paddle(side)


class Paddle:
    def __init__(self, side):
        self.side = side
        self.margin = 0.1
        if side == "left":
            self.x = self.margin
            self.y = 0.5
        elif side == "right":
            self.x = 1 - self.margin
            self.y = 0.5
        elif side == "top":
            self.x = 0.5
            self.y = self.margin
        elif side == "bottom":
            self.x = 0.5
            self.y = 1 - self.margin
        self.width = 0.07
        self.height = 0.2
        self.speed = 42
        self.is_down_pressed = False
        self.is_up_pressed = False

    def update(self, dt):
        if self.side == "left" or self.side == "right":
            self.move(dt, True)
        else:
            self.move(dt, False)

    def move(self, dt, is_vertical):
        direction = 1 if self.is_down_pressed else -1 if self.is_up_pressed else 0
        if is_vertical:
            self.y += direction * self.speed * dt
        else:
            self.x += direction * self.speed * dt
        self.y = clamp(self.y, self.height * 0.5, 1 - self.height * 0.5)
        self.x = clamp(self.x, self.width * 0.5, 1 - self.width * 0.5)

    def get_edge(self, edge):
        if edge == "left":
            return (
                self.x - 0.5 * self.width,
                self.y - 0.5 * self.height,
                self.x - 0.5 * self.width,
                self.y + 0.5 * self.height,
            )
        elif edge == "right":
            return (
                self.x + 0.5 * self.width,
                self.y - 0.5 * self.height,
                self.x + 0.5 * self.width,
                self.y + 0.5 * self.height,
            )
        elif edge == "top":
            return (
                self.x - 0.5 * self.width,
                self.y - 0.5 * self.height,
                self.x + 0.5 * self.width,
                self.y - 0.5 * self.height,
            )
        elif edge == "bottom":
            return (
                self.x - 0.5 * self.width,
                self.y + 0.5 * self.height,
                self.x + 0.5 * self.width,
                self.y + 0.5 * self.height,
            )


class Ball:
    def __init__(self):
        self.radius = 2e-2
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.reset()

    def reset(self):
        self.x = 0.5
        self.y = 0.5
        # self.dx = bipolar_between(10, 25)
        self.dx = -5
        self.dy = bipolar_between(5, 25)

    def update(self, dt):
        # self.accelerate(1, dt)
        self.x += self.dx * dt
        self.y += self.dy * dt
        clamp(self.y, 0, 1)

    def accelerate(self, a, dt):
        self.dx += a * dt * (1 if self.dx > 0 else -1)
        self.dy += a * dt * (1 if self.dy > 0 else -1)

    def get_trajectory(self, dt):
        next = Ball()
        next.x = self.x
        next.y = self.y
        next.dx = self.dx
        next.dy = self.dy
        next.update(dt)
        return (self.x, self.y, next.x, next.y)

    def get_corner_trajectory(self, corner, dt):
        cx, cy, nx, ny = self.get_trajectory(dt)
        if corner == "topleft":
            return (
                cx - self.radius,
                cy - self.radius,
                nx - self.radius,
                ny - self.radius,
            )
        if corner == "topright":
            return (
                cx + self.radius,
                cy - self.radius,
                nx + self.radius,
                ny - self.radius,
            )
        if corner == "bottomleft":
            return (
                cx - self.radius,
                cy + self.radius,
                nx - self.radius,
                ny + self.radius,
            )
        if corner == "bottomright":
            return (
                cx + self.radius,
                cy + self.radius,
                nx + self.radius,
                ny + self.radius,
            )

    # // continue with
    # get ball corners, use 2 paddle-facing corners in paddle intercepting check
    # improve move ball, it should return future position which you can check if it will intercept
    # update loop should be: move paddles, check future ball position, move ball
    # rewrite accelerate function, less complex


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
        self.left.paddle.update(dt)
        self.right.paddle.update(dt)
        if hasattr(self, "top"):
            self.top.paddle.update(dt)
        if hasattr(self, "bottom"):
            self.bottom.paddle.update(dt)
        self.ball.update(dt)
        self.handle_collisions(dt)

    def handle_collisions(self, dt):
        self.handle_goal()
        if not self.isFourPlayer:
            self.handle_wall_collision(dt)
        self.handle_paddle_collision(dt)
        # increase acceleration when paddle collision occurs

    def handle_goal(self):
        if self.ball.x < 0.0:
            self.left.score += 1
            self.ball.reset()
        elif self.ball.x > 1.0:
            self.right.score += 1
            self.ball.reset()
        elif self.ball.y < 0.0:
            self.top.score += 1
            self.ball.reset()
        elif self.ball.y > 1.0:
            self.bottom.score += 1
            self.ball.reset()

    def handle_wall_collision(self, dt):
        top_wall = (0, 0, 1, 0)
        bottom_wall = (0, 1, 1, 1)
        if does_intersect(top_wall, self.ball.get_trajectory(dt)) or does_intersect(
            bottom_wall, self.ball.get_trajectory(dt)
        ):
            self.ball.dy *= -1

    def handle_paddle_collision(self, dt):
        if self.ball.dx < 0:
            defending_paddle = self.left.paddle
            inward_edge = "right"
            ball_trajectory_top_corner = self.ball.get_corner_trajectory("topleft", dt)
            ball_trajectory_bottom_corner = self.ball.get_corner_trajectory(
                "bottomleft", dt
            )
        else:
            defending_paddle = self.right.paddle
            inward_edge = "left"
            ball_trajectory_top_corner = self.ball.get_corner_trajectory("topright", dt)
            ball_trajectory_bottom_corner = self.ball.get_corner_trajectory(
                "bottomright", dt
            )

        # check inward facing paddle edge
        if does_intersect(
            defending_paddle.get_edge(inward_edge), ball_trajectory_top_corner
        ) or does_intersect(
            defending_paddle.get_edge(inward_edge), ball_trajectory_bottom_corner
        ):
            self.ball.dx *= -1
        # check top and bottom paddle edges
        if does_intersect(
            defending_paddle.get_edge("top"), ball_trajectory_bottom_corner
        ) or does_intersect(
            defending_paddle.get_edge("bottom"), ball_trajectory_top_corner
        ):
            self.ball.dy *= -1

    def getScene(self):
        scene = []
        scene.append(
            {
                "type": "ball",
                "x": self.ball.x - self.ball.radius,
                "y": self.ball.y - self.ball.radius,
                "width": self.ball.radius * 2,
                "height": self.ball.radius * 2,
            }
        )

        scene.append(
            {
                "type": "left",
                "x": self.left.paddle.x - 0.5 * self.left.paddle.width,
                "y": self.left.paddle.y - 0.5 * self.left.paddle.height,
                "width": self.left.paddle.width,
                "height": self.left.paddle.height,
            }
        )
        scene.append(
            {
                "type": "right",
                "x": self.right.paddle.x - 0.5 * self.right.paddle.width,
                "y": self.right.paddle.y - 0.5 * self.right.paddle.height,
                "width": self.right.paddle.width,
                "height": self.right.paddle.height,
            }
        )

        if hasattr(self, "top"):
            scene.append(
                {
                    "type": "top",
                    "x": self.top.paddle.x - 0.5 * self.top.paddle.height,
                    "y": self.top.paddle.y - 0.5 * self.top.paddle.width,
                    "width": self.top.paddle.height,
                    "height": self.top.paddle.width,
                }
            )
        if hasattr(self, "bottom"):
            scene.append(
                {
                    "type": "bottom",
                    "x": self.bottom.paddle.x - 0.5 * self.bottom.paddle.height,
                    "y": self.bottom.paddle.y - 0.5 * self.bottom.paddle.width,
                    "width": self.bottom.paddle.height,
                    "height": self.bottom.paddle.width,
                }
            )
        return scene


# return a random float between '-max_value' and 'max_value' with magnitude greater than min_value
bipolar_between = lambda min_value, max_value: random.uniform(
    min_value, max_value
) * random.choice([-1, 1])

# constrain 'value' to between 'min_value' and 'max_value'
clamp = lambda value, min_value, max_value: max(min(value, max_value), min_value)


# check if 3 points are given in a counter-clockwise order
def ccw(ax, ay, bx, by, cx, cy):
    return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)


# check if 2 lines intersect
def does_intersect(line1, line2):
    ax, ay, bx, by = line1
    cx, cy, dx, dy = line2
    return ccw(ax, ay, cx, cy, dx, dy) != ccw(bx, by, cx, cy, dx, dy) and ccw(
        ax, ay, bx, by, cx, cy
    ) != ccw(ax, ay, bx, by, dx, dy)
