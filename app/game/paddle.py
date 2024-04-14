class Paddle:
    def __init__(self, side):
        self.side = side
        self.margin = 0.04
        self.depth = 0.04
        self.length = 0.16
        if side == "left":
            self.x = self.margin
            self.y = 0.5 - 0.5 * self.length
        elif side == "right":
            self.x = 1 - self.margin - self.depth
            self.y = 0.5 - 0.5 * self.length
        elif side == "top":
            self.x = 0.5 - 0.5 * self.length
            self.y = self.margin
        elif side == "bottom":
            self.x = 0.5 - 0.5 * self.length
            self.y = 1 - self.margin - self.depth
        self.speed = 0.8
        self.is_down_pressed = False
        self.is_up_pressed = False

    def update(self, dt):
        if self.side == "left" or self.side == "right":
            self.move(dt, True)
        else:
            self.move(dt, False)

    def move(self, dt, move_vertically):
        direction = 1 if self.is_down_pressed else -1 if self.is_up_pressed else 0
        if move_vertically:
            self.y += direction * self.speed * dt
            self.y = clamp(self.y, 0, 1 - self.length)
        else:
            self.x += direction * self.speed * dt
            self.x = clamp(self.x, 0, 1 - self.length)

    # TODO: check if all edges are needed (e.g. top and bottom edges of vertically moving paddles)
    def get_edge(self, edge):
        if edge == "left":
            if self.side == "left" or self.side == "right":
                return (self.x, self.y, self.x, self.y + self.length)
            else:
                return (self.x, self.y, self.x, self.y + self.depth)

        elif edge == "right":
            if self.side == "left" or self.side == "right":
                return (
                    self.x + self.depth,
                    self.y,
                    self.x + self.depth,
                    self.y + self.length,
                )
            else:
                return (
                    self.x + self.length,
                    self.y,
                    self.x + self.length,
                    self.y + self.depth,
                )
        elif edge == "top":
            if self.side == "left" or self.side == "right":
                return (self.x, self.y, self.x + self.depth, self.y)
            else:
                return (self.x, self.y, self.x + self.length, self.y)
        elif edge == "bottom":
            if self.side == "left" or self.side == "right":
                return (
                    self.x,
                    self.y + self.length,
                    self.x + self.depth,
                    self.y + self.length,
                )
            else:
                return (
                    self.x,
                    self.y + self.depth,
                    self.x + self.length,
                    self.y + self.depth,
                )


# constrain 'value' to between 'min_value' and 'max_value'
clamp = lambda value, min_value, max_value: max(min(value, max_value), min_value)
