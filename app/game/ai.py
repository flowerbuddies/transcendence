import asyncio
import random


class BehaviorTree:
    def __init__(self, game_state, player):
        self.gs = game_state
        self.player = player
        self.difficulty = 0.0
        self.accumulated_scores = 0
        self.hesitation_seconds = 1
        self.hesitation_start = asyncio.get_event_loop().time()
        self.inaccuracy_max = 0.0
        self.inaccuracy = 0.0
        self.predict_x = 0.5
        self.predict_y = 0.5

    # called once per frame
    def update(self):
        if not self.is_defending():
            self.hesitation_start = asyncio.get_event_loop().time()
            return
        if self.did_scores_change():
            self.set_difficulty()
            self.apply_difficulty()
        self.predict()
        if not self.is_hesitating():
            self.move_to_prediction()

    # TODO: depends on score/life implementation
    # set difficulty using gs, e.g. scores
    def set_difficulty(self):
        # something = equation(self.player.score, self.accumulated_scores)
        # self.inaccuracy_max = something * {0, 1}
        # self.hesitation_seconds = something * {0, max_seconds}
        pass

    # using difficulty, set hesitation and inaccuracy
    def apply_difficulty(self):
        self.inaccuracy = random.uniform(-self.inaccuracy_max, self.inaccuracy_max)

    def did_scores_change(self):
        previous_accumulated_scores = self.accumulated_scores
        self.accumulated_scores = self.gs.left.score
        self.accumulated_scores += self.gs.right.score
        if self.gs.is_four_player:
            self.accumulated_scores += self.gs.top.score
            self.accumulated_scores += self.gs.bottom.score
        return previous_accumulated_scores != self.accumulated_scores

    # true if ball is approaching ai paddle
    def is_defending(self):
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

    # returns true if still hesitating
    def is_hesitating(self):
        return (
            asyncio.get_event_loop().time()
            < self.hesitation_start + self.hesitation_seconds
        )

    # predict where to move, using inaccuracy
    def predict(self):
        self.set_prediction()
        self.predict_x += self.inaccuracy
        self.predict_y += self.inaccuracy
        offset = self.player.paddle.margin + 0.5 * self.player.paddle.length
        self.predict_x = clamp(self.predict_x, offset, 1.0 - offset)
        self.predict_y = clamp(self.predict_y, offset, 1.0 - offset)

    def get_gradient(self):
        if self.gs.ball.dx == 0.0:
            return 1e5
        return self.gs.ball.dy / self.gs.ball.dx

    def set_prediction(self):
        offset = self.player.paddle.margin + self.player.paddle.depth
        gradient = self.get_gradient()
        if gradient == 0.0:
            gradient = 1e-4
        if self.player.side == "left":
            self.predict_y = self.gs.ball.y + gradient * (offset - self.gs.ball.x)
        elif self.player.side == "right":
            self.predict_y = self.gs.ball.y + gradient * (1 - offset - self.gs.ball.x)
        elif self.player.side == "top":
            self.predict_x = (offset - self.gs.ball.y) / gradient + self.gs.ball.x
        elif self.player.side == "bottom":
            self.predict_x = (1 - offset - self.gs.ball.y) / gradient + self.gs.ball.x

    # move paddle to intercept ball
    # start hesitation when reaching prediction
    def move_to_prediction(self):
        paddle = self.player.paddle
        paddle.is_up_pressed = False
        paddle.is_down_pressed = False
        if self.player.side == "left" or self.player.side == "right":
            if self.is_nearby(self.predict_y, paddle.y):
                self.hesitation_start = asyncio.get_event_loop().time()
            else:
                if self.predict_y < paddle.y + 0.5 * paddle.length:
                    paddle.is_up_pressed = True
                else:
                    paddle.is_down_pressed = True
        else:
            if self.is_nearby(self.predict_x, paddle.x):
                self.hesitation_start = asyncio.get_event_loop().time()
            else:
                if self.predict_x < paddle.x + 0.5 * paddle.length:
                    paddle.is_up_pressed = True
                else:
                    paddle.is_down_pressed = True

    # check if paddle is near prediction
    def is_nearby(self, predict, paddle):
        return (
            paddle + 0.2 * self.player.paddle.length
            < predict
            < paddle + 0.8 * self.player.paddle.length
        )


# constrain 'value' to between 'min_value' and 'max_value'
clamp = lambda value, min_value, max_value: max(min(value, max_value), min_value)
