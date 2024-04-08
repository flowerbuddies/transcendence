import random


class Player:
    def __init__(self, side):
        self.side = side
        self.score = 0
        self.paddle = Paddle(side)


class Paddle:
    def __init__(self, side):
        self.side = side
        if side == "left":
            self.x = 0
            self.y = 0.5
        elif side == "right":
            self.x = 1
            self.y = 0.5
        elif side == "top":
            self.x = 0.5
            self.y = 0
        elif side == "bottom":
            self.x = 0.5
            self.y = 1
        self.width = 0.1
        self.height = 0.2
        self.speed = 2e-2
        self.is_down_pressed = False
        self.is_up_pressed = False

    def update(self):
        if self.side == "left" or self.side == "right":
            self.move(True)
        else:
            self.move(False)

    def move(self, is_vertical):
        direction = 1 if self.is_down_pressed else -1 if self.is_up_pressed else 0
        if is_vertical:
            self.y += direction * self.speed
        else:
            self.x += direction * self.speed
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
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.radius = 2e-2
        self.reset()

    def reset(self):
        self.x = 0.5
        self.y = 0.5
        self.dx = bipolar_between(15, 25)
        self.dy = bipolar_between(15, 25)

    def update(self, dt):
        self.accelerate(1, dt)

    def accelerate(self, a, dt):
        a_integral = a * dt * dt * 0.5
        self.x += self.dx * dt + a_integral
        self.y += self.dy * dt + a_integral
        self.dx += a * dt * (1 if self.dx > 0 else -1)
        self.dy += a * dt * (1 if self.dy > 0 else -1)

    # TODO: currently unused
    def get_edge(self, edge):
        if edge == "left":
            return (
                self.x - self.radius,
                self.y - self.radius,
                self.x - self.radius,
                self.y + self.radius,
            )
        elif edge == "right":
            return (
                self.x + self.radius,
                self.y - self.radius,
                self.x + self.radius,
                self.y + self.radius,
            )
        elif edge == "top":
            return (
                self.x - self.radius,
                self.y - self.radius,
                self.x + self.radius,
                self.y - self.radius,
            )
        elif edge == "bottom":
            return (
                self.x - self.radius,
                self.y + self.radius,
                self.x + self.radius,
                self.y + self.radius,
            )


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
        self.left.paddle.update()
        self.right.paddle.update()
        if hasattr(self, "top"):
            self.top.paddle.update()
        if hasattr(self, "bottom"):
            self.bottom.paddle.update()
        self.ball.update(dt)
        self.handle_collisions(dt)

    def handle_collisions(self, dt):
        self.handle_goal()
        if not self.isFourPlayer:
            self.handle_wall_collision()
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

    def handle_wall_collision(self):
        if self.ball.y < self.ball.radius or self.ball.y > 1.0 - self.ball.radius:
            self.ball.dy *= -1

    def handle_paddle_collision(self, dt):
        next = Ball()
        next.x = self.ball.x
        next.y = self.ball.y
        next.dx = self.ball.dx
        next.dy = self.ball.dy
        next.accelerate(1, dt)

        if self.ball.dx < 0:
            defending_paddle = self.left.paddle
            inward_facing_edge = "right"
        else:
            defending_paddle = self.right.paddle
            inward_facing_edge = "left"

        # check inward facing paddle edge
        cx, cy, dx, dy = defending_paddle.get_edge(inward_facing_edge)
        if does_intersect(self.ball.x, self.ball.y, next.x, next.y, cx, cy, dx, dy):
            self.ball.dx *= -1
        # check top and bottom paddle edges
        cx, cy, dx, dy = defending_paddle.get_edge("top")
        if does_intersect(self.ball.x, self.ball.y, next.x, next.y, cx, cy, dx, dy):
            self.ball.dy *= -1
        cx, cy, dx, dy = defending_paddle.get_edge("bottom")
        if does_intersect(self.ball.x, self.ball.y, next.x, next.y, cx, cy, dx, dy):
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


# check if lines AB and CD intersect
def does_intersect(ax, ay, bx, by, cx, cy, dx, dy):
    return ccw(ax, ay, cx, cy, dx, dy) != ccw(bx, by, cx, cy, dx, dy) and ccw(
        ax, ay, bx, by, cx, cy
    ) != ccw(ax, ay, bx, by, dx, dy)
