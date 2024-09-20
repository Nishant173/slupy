from typing import Any, Dict, Optional, Union

Sliceable = Union[list, tuple, str]


def slice_by_position(
        sliceable: Sliceable,
        /,
        *,
        start: int,
        end: int,
    ) -> Sliceable:
    """
    Slice the given sliceable object by position (not by index).
    The position can range from 1-n (where `n` is the length of the sliceable).
    """
    length = len(sliceable)
    assert start >= 1, "Position `start` is out of bounds"
    assert end <= length, "Position `end` is out of bounds"
    return sliceable[start - 1 : end]


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

