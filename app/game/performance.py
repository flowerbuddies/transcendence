import time


class FPSMonitor:
    def __init__(self):
        self.frames = 0
        self.start_time = time.time()

    def tick(self):
        self.frames += 1
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= 1.0:
            print(f"FPS: {self.frames}")
            self.frames = 0
            self.start_time = current_time
