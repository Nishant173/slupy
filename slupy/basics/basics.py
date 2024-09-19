from typing import Any, Dict, List, Optional, Type, Union


def is_instance_of_any(obj: Any, *, types: List[Type]) -> bool:
    return isinstance(obj, tuple(types))


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


def _get_kwarg_as_string(key: Any, value: Any) -> str:
    return f"{key}='{value}'" if isinstance(value, str) else f"{key}={value}"


def _single_line_repr(
        *,
        class_name: str,
        kwargs_dict: Dict[str, Any],
    ) -> str:
    if not kwargs_dict:
        return f"{class_name}()"
    kwargs_dict_as_string = ", ".join(
        [_get_kwarg_as_string(key=key, value=value) for key, value in kwargs_dict.items()]
    )
    return f"{class_name}({kwargs_dict_as_string})"


def _multi_line_repr(
        *,
        class_name: str,
        kwargs_dict: Dict[str, Any],
    ) -> str:
    if not kwargs_dict:
        return f"{class_name}()"
    indent = 4
    kwargs_dict_as_string = ""
    for key, value in kwargs_dict.items():
        kwargs_dict_as_string += " " * indent + _get_kwarg_as_string(key=key, value=value) + "," + "\n"
    kwargs_dict_as_string = kwargs_dict_as_string.rstrip()
    return f"{class_name}(\n{kwargs_dict_as_string}\n)"


def create_repr(
        *,
        instance: Any,
        kwargs_dict: Optional[Dict[str, Any]] = None,
        multi_line: Optional[bool] = True,
    ) -> str:
    """
    Returns a representation of a class' instance.

    ```
    class Person:
        pass

    create_repr(
        instance=Person(),
        kwargs_dict={
            "first_name": "James",
            "last_name": "Murphy",
            "age": 35,
            "is_developer": True,
        },
        multi_line=False,
    ) # Returns the string: "Person(first_name='James', last_name='Murphy', age=35, is_developer=True)"
    ```
    """
    assert kwargs_dict is None or isinstance(kwargs_dict, dict), f"Param `kwargs_dict` must be of type 'dict'"
    kwargs_dict = kwargs_dict or {}
    kw = {
        "class_name": instance.__class__.__name__,
        "kwargs_dict": kwargs_dict,
    }
    return _multi_line_repr(**kw) if multi_line else _single_line_repr(**kw)


def print_docstring(obj: Any) -> None:
    """Prints the doc-string (if available). Usually of a class, method or function."""
    if hasattr(obj, "__doc__"):
        print(obj.__doc__)


def round_off_as_string(number: Union[int, float], round_by: int) -> str:
    """
    Rounds off the given `number` to `round_by` decimal places, and type casts
    it to a string (to retain the exact number of decimal places desired).
    """
    if round_by < 0:
        raise ValueError("The `round_by` parameter must be >= 0")
    if round_by == 0:
        return str(round(number))
    number_stringified = str(round(number, round_by))
    decimal_places_filled = len(number_stringified.split('.')[-1])
    decimal_places_to_fill = round_by - decimal_places_filled
    for _ in range(decimal_places_to_fill):
        number_stringified += '0'
    return number_stringified


def commafy_number(number: Union[int, float]) -> str:
    """
    Adds commas to number for better readability.

    ```
    >>> commafy_number(number=1738183090) # Returns "1,738,183,090"
    >>> commafy_number(number=1738183090.90406) # Returns "1,738,183,090.90406"
    ```
    """
    if int(number) == number:
        return format(int(number), ",d")
    return format(number, ",f")


def string_to_int_or_float(value: str) -> Union[int, float]:
    """Converts stringified number to either int or float"""
    number = float(value)
    number = integerify_if_possible(number)
    return number


def stringify_list_of_nums(array: List[Union[int, float]]) -> str:
    """Converts list of ints/floats to comma separated string of the same"""
    return ",".join(list(map(str, array)))


def listify_string_of_nums(s: str) -> List[Union[int, float]]:
    """Converts string of comma separated ints/floats to list of numbers"""
    numbers = s.split(",")
    numbers = list(map(string_to_int_or_float, numbers))
    return numbers


def list_has_negative_number(array: List[Union[int, float]]) -> bool:
    return any((number < 0 for number in array))


def list_has_non_negative_number(array: List[Union[int, float]]) -> bool:
    return any((number >= 0 for number in array))


def list_has_positive_number(array: List[Union[int, float]]) -> bool:
    return any((number > 0 for number in array))


def cumulative_aggregate(*, numbers: List[Union[int, float]], method: str) -> List[Union[int, float]]:
    """
    Returns list of cumulative aggregates.
    Options for `method` are: `["sum", "difference", "product", "division"]`.
    """
    method_mapper = {
        "sum": lambda x, y: x + y,
        "difference": lambda x, y: x - y,
        "product": lambda x, y: x * y,
        "division": lambda x, y: x / y,
    }
    assert method in method_mapper, f"Param `method` must be one of: {list(method_mapper.keys())}"

    length = len(numbers)
    if length == 0:
        return []
    cumulative_array = [numbers[0]]
    if length == 1:
        return cumulative_array
    for number in numbers[1:]:
        cumulative_array.append(method_mapper[method](cumulative_array[-1], number))
    return cumulative_array

