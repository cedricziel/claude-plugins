def page_count(total, size):
    return (total + size - 1) // size


def paginate(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]
