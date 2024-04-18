from .game import GameState


class BehaviorTree:
    def __init__(self, game_state):
        self.is_up_pressed = False
        self.is_down_pressed = False
        self.gs = game_state
        self.difficulty = 0.0
        self.hesitation = 0.0
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
        pass

    def apply_difficulty(self):
        # using difficulty, set hesitation and inaccuracy
        pass

    def is_defending(self):
        # true if ball is approaching ai paddle
        pass

    def predict(self):
        # predict where to move, using inaccuracy
        # approaches:
        # 1) move to intercept ball where it will intersect with goal
        #       from ball xy, draw an infinite line through ball dxdy, the "path".
        #       move paddle to x or y intercept of path and goal
        # 2) simply track ball xy
        #       if ball xy > paddle xy, move paddle down/right
        #       else move paddle up/left
        pass

    def move_to_ball(self):
        # move paddle to intercept ball
        pass

    def is_hesitating(self):
        # returns true if still hesitating
        pass
