import time


class TokenBucket:
    def __init__(self, capacity, rate, clock=time.monotonic):
        self.capacity = capacity
        self.rate = rate
        self.clock = clock
        self.tokens = capacity
        self.last = clock()

    def _refill(self):
        now = self.clock()
        elapsed = now - self.last
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last = now

    def take(self, n=1):
        self._refill()
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False
