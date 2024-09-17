from typing import Any


def is_zero_or_none(x: Any, /) -> bool:
    return x == 0 or x is None


def is_boolean(x: Any, /) -> bool:
    return isinstance(x, bool)


def is_positive_integer(x: Any, /) -> bool:
    return isinstance(x, int) and x > 0


def is_non_negative_integer(x: Any, /) -> bool:
    return isinstance(x, int) and x >= 0

