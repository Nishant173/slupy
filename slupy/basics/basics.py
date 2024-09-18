from typing import Any, Union


def is_zero_or_none(x: Any, /) -> bool:
    return x == 0 or x is None


def is_boolean(x: Any, /) -> bool:
    return isinstance(x, bool)


def is_integer(x: Any, /) -> bool:
    return isinstance(x, int)


def is_positive_integer(x: Any, /) -> bool:
    return isinstance(x, int) and x > 0


def is_positive_number(x: Any, /) -> bool:
    return isinstance(x, (int, float)) and x > 0


def is_non_negative_integer(x: Any, /) -> bool:
    return isinstance(x, int) and x >= 0


def is_non_negative_number(x: Any, /) -> bool:
    return isinstance(x, (int, float)) and x >= 0


def is_whole_number(number: Union[int, float], /) -> bool:
    return int(number) == number


def integerify_if_possible(number: Union[int, float], /) -> Union[int, float]:
    """Converts whole numbers represented as floats to integers"""
    return int(number) if is_whole_number(number) else number

