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
        if n > self.capacity:
            raise ValueError("request exceeds bucket capacity")
        self._refill()
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False

    def wait_time(self, n=1):
        """Seconds until `n` tokens are available."""
        self._refill()
        missing = n - self.tokens
        return missing / self.rate


class Limiter:
    def __init__(self, capacity, rate, overrides={}, clock=time.monotonic):
        self.capacity = capacity
        self.rate = rate
        self.overrides = overrides
        self.clock = clock
        self._buckets = {}

    def set_override(self, tenant, capacity):
        self.overrides[tenant] = capacity
        self._buckets.pop(tenant, None)

    def bucket(self, tenant):
        if tenant not in self._buckets:
            capacity = self.overrides.get(tenant, self.capacity)
            self._buckets[tenant] = TokenBucket(capacity, self.rate, self.clock)
        return self._buckets[tenant]

    def take(self, tenant, n=1):
        return self.bucket(tenant).take(n)
