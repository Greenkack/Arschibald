import random
import string


def random_arg():
    return random.choice([
        random.randint(-1000, 1000),
        ''.join(random.choices(string.ascii_letters, k=8)),
        [random.randint(1, 10) for _ in range(3)]
    ])


def fuzz_test_func(func):
    for _ in range(100):
        try:
            func(*[random_arg() for _ in range(func.__code__.co_argcount)])
        except Exception as e:
            print(f"Fuzzed Error: {e}")
