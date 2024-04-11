import random


class Ball:
    def __init__(self):
        self.radius = 15e-3
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.reset()

    def reset(self):
        self.x = 0.5 - self.radius
        self.y = 0.5 - self.radius
        self.dx = bipolar_between(3, 15)
        self.dy = bipolar_between(3, 15)

    def update(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt

    def accelerate(self, a, dt):
        self.dx += a * dt * (1 if self.dx > 0 else -1)
        self.dy += a * dt * (1 if self.dy > 0 else -1)

    def next_position(self, dt):
        next = Ball()
        next.x = self.x
        next.y = self.y
        next.dx = self.dx
        next.dy = self.dy
        next.update(dt)
        return next

    def get_edge(self, edge):
        if edge == "left":
            return (self.x, self.y, self.x, self.y + self.radius)
        elif edge == "right":
            return (
                self.x + self.radius,
                self.y,
                self.x + self.radius,
                self.y + self.radius,
            )
        elif edge == "top":
            return (self.x, self.y, self.x + self.radius, self.y)
        elif edge == "bottom":
            return (
                self.x,
                self.y + self.radius,
                self.x + self.radius,
                self.y + self.radius,
            )


# return a random float between '-max_value' and 'max_value' with magnitude greater than min_value
bipolar_between = lambda min_value, max_value: random.uniform(
    min_value, max_value
) * random.choice([-1, 1])