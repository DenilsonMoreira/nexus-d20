import math


def ability_modifier(score: int) -> int:
    return math.floor((score - 10) / 2)
