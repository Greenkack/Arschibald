import sys


def set_recursion_limit(limit=10000):
    sys.setrecursionlimit(limit)
    print(f"✅ Recursion Limit auf {limit} gesetzt!")
