def page_count(total, size):
    if size <= 0:
        raise ValueError("size must be positive")
    return total // size


def paginate(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


def deltas(samples):
    """Differences between consecutive samples."""
    return [samples[i + 1] - samples[i] for i in range(len(samples) - 1)]


def over_quota(used, quota, grace=0.1):
    """True once usage exceeds the quota plus a grace margin."""
    return used > quota * grace
