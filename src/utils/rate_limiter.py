# src/utils/rate_limiter.py

import time

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps = []

    def wait(self):
        now = time.time()
        self.timestamps = [t for t in self.timestamps if now - t < self.period]
        if len(self.timestamps) >= self.calls:
            time.sleep(self.period - (now - self.timestamps[0]))
        self.timestamps.append(time.time())

