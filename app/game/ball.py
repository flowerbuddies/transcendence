import random


class Ball:
    def __init__(self):
        self.radius = 15e-3
        self.x = 0.0
        self.y = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.reset()
        self.apply_accel = False
        self.accel = 2
        self.trail = []
        self.max_trail_len = 20

    def reset(self):
        self.x = 0.5 - self.radius
        self.y = 0.5 - self.radius
        self.dx = bipolar_between(5e-2, 5e-1)
        self.dy = bipolar_between(5e-2, 5e-1)
        self.trail = []

    def update(self, dt):
        self.update_trail()
        if self.apply_accel:
            self.dx += self.accel * dt * (1 if self.dx > 0 else -1)
            self.dy += self.accel * dt * (1 if self.dy > 0 else -1)
            self.apply_accel = False
        self.x += self.dx * dt
        self.y += self.dy * dt

    def update_trail(self):
        segment = {
            "x": self.x,
            "y": self.y,
        }
        self.trail.insert(0, segment)
        if len(self.trail) > self.max_trail_len:
            self.trail.pop()

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
