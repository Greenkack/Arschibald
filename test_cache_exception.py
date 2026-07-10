from functools import lru_cache

counter = 0

@lru_cache(maxsize=100)
def do_something(x):
    global counter
    counter += 1
    if x == 1:
        raise ValueError("Error 1")
    return x * 2

try:
    do_something(1)
except Exception:
    pass

try:
    do_something(1)
except Exception:
    pass

print(counter)
