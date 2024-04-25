from .game import GameState
import asyncio


class BehaviorTree:
    def __init__(self, game_state, player):
        self.gs = game_state
        self.player = player
        self.is_up_pressed = False
        self.is_down_pressed = False
        self.difficulty = 0.0
        self.hesitation = 0.0
        self.hesitation_start_time = asyncio.get_event_loop().time()
        self.inaccuracy = 0.0

    def update(self):
        # called once per frame
        if not self.is_defending() or self.is_hesitating():
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

    def predict(self):
        # predict where to move, using inaccuracy
        # approaches:
        # 1) move to intercept ball where it will intersect with goal
        #       from ball xy, draw an infinite line through ball dxdy, the "path".
        #       move paddle to x or y intercept of path and goal
        # 2) simply track ball xy
        #       if ball xy > paddle xy, move paddle down/right
        #       else move paddle up/left
        defense_line = (x1, y1, x2, y2)
        pass

    def move_to_ball(self):
        # move paddle to intercept ball
        pass

    def is_hesitating(self):
        # returns true if still hesitating
        # TODO: grace period before hesitating again, until next paddle collision?
        if (
            asyncio.get_event_loop().time()
            > self.hesitation_start_time + self.hesitation
        ):
            self.hesitation_start_time = asyncio.get_event_loop().time()
            return False
        return True
