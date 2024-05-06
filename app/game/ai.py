import asyncio


class BehaviorTree:
    def __init__(self, game_state, player):
        self.gs = game_state
        self.player = player
        self.difficulty = 0.0
        self.inaccuracy = 0.0
        self.hesitation_start = asyncio.get_event_loop().time()
        self.hesitation_seconds = 3
        self.predict_x = 0.0
        self.predict_y = 0.0

    def update(self):
        # called once per frame
        if not self.is_defending():
            self.hesitation_start = asyncio.get_event_loop().time()
            return
        if self.is_hesitating():
            return
        self.set_difficulty()
        self.apply_difficulty()
        self.predict()
        self.move_to_ball()

    def set_difficulty(self):
        # set difficulty using gs, e.g. scores
        # TODO: depends on score/life implementation
        pass

    def apply_difficulty(self):
        # using difficulty, set hesitation and inaccuracy
        pass

    def is_defending(self):
        # true if ball is approaching ai paddle
        return (
            self.player.side == "left"
            and self.gs.ball.dx < 0
            or self.player.side == "right"
            and self.gs.ball.dx > 0
            or self.player.side == "top"
            and self.gs.ball.dy < 0
            or self.player.side == "bottom"
            and self.gs.ball.dy > 0
        )

    def is_hesitating(self):
        # returns true if still hesitating
        return (
            asyncio.get_event_loop().time()
            < self.hesitation_start + self.hesitation_seconds
        )

    def predict(self):
        # predict where to move, using inaccuracy
        # TODO: use inaccuracy
        self.get_intercept()

    def get_gradient(self):
        if self.gs.ball.dx == 0.0:
            return 1e5
        return self.gs.ball.dy / self.gs.ball.dx

    def get_intercept(self):
        gradient = self.get_gradient()
        if gradient == 0.0:
            gradient = 1e-4
        # TODO: check the math...
        if self.player.side == "left":
            self.predict_x = 0
            self.predict_y = self.gs.ball.y - gradient * self.gs.ball.x
        elif self.player.side == "right":
            self.predict_x = 1
            self.predict_y = self.gs.ball.y + gradient * (1 - self.gs.ball.x)
        elif self.player.side == "top":
            self.predict_x = (0 - self.gs.ball.y) / gradient + self.gs.ball.x
            self.predict_y = 0
        elif self.player.side == "bottom":
            self.predict_x = (1 - self.gs.ball.y) / gradient + self.gs.ball.x
            self.predict_y = 1

    def move_to_ball(self):
        # move paddle to intercept ball
        # TODO: fix "wiggle"
        self.player.paddle.is_up_pressed = False
        self.player.paddle.is_down_pressed = False
        if self.player.side == "left" or self.player.side == "right":
            if self.predict_y < self.player.paddle.y + 0.5 * self.player.paddle.length:
                self.player.paddle.is_up_pressed = True
            elif (
                self.predict_y > self.player.paddle.y + 0.5 * self.player.paddle.length
            ):
                self.player.paddle.is_down_pressed = True
        else:
            if self.predict_x < self.player.paddle.x + 0.5 * self.player.paddle.length:
                self.player.paddle.is_up_pressed = True
            elif (
                self.predict_x > self.player.paddle.x + 0.5 * self.player.paddle.length
            ):
                self.player.paddle.is_down_pressed = True
