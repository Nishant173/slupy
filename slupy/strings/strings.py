import re
import string
from typing import List, Optional

from slupy.core import checks


ALPHABETS_LOWER_CASED = set(string.ascii_lowercase)
ALPHABETS_UPPER_CASED = set(string.ascii_uppercase)
ALPHABETS = ALPHABETS_LOWER_CASED.union(ALPHABETS_UPPER_CASED)


def make_message(
        message: str,
        /,
        *,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        sep: Optional[str] = None,
    ) -> str:
    sep = "" if sep is None else sep
    components = []
    if prefix:
        components.append(prefix)
    components.append(message)
    if suffix:
        components.append(suffix)
    return f"{sep}".join(components)


def camel_to_pascal(string: str) -> str:
    """
    Converts camel-case to pascal-case.
    >>> camel_to_pascal(string="helloAndGoodMorning") # Returns "HelloAndGoodMorning"
    """
    return string[0].upper() + string[1:]


def pascal_to_camel(string: str) -> str:
    """
    Converts pascal-case to camel-case.
    >>> pascal_to_camel(string="HelloAndGoodMorning") # Returns "helloAndGoodMorning"
    """
    return string[0].lower() + string[1:]


def pascal_to_snake(string: str) -> str:
    """
    Converts pascal-case to snake-case.
    >>> pascal_to_snake(string="HelloAndGoodMorning") # Returns "hello_and_good_morning"
    """
    words = re.findall(pattern="[A-Z][^A-Z]*", string=string)
    words_lower_cased = list(map(str.lower, words))
    return "_".join(words_lower_cased)


def camel_to_snake(string: str) -> str:
    """
    Converts camel-case to snake-case.
    >>> camel_to_snake(string="helloAndGoodMorning") # Returns "hello_and_good_morning"
    """
    string_in_pascal = camel_to_pascal(string=string)
    string_in_snake = pascal_to_snake(string=string_in_pascal)
    return string_in_snake


def snake_to_pascal(string: str) -> str:
    """
    Converts snake-case to pascal-case.
    >>> snake_to_pascal(string="hello_and_good_morning") # Returns "HelloAndGoodMorning"
    """
    words = string.split('_')
    words_capitalized = list(map(str.capitalize, words))
    return "".join(words_capitalized)


def snake_to_camel(string: str) -> str:
    """
    Converts snake-case to camel-case.
    >>> snake_to_camel(string="hello_and_good_morning") # Returns "helloAndGoodMorning"
    """
    string_in_pascal = snake_to_pascal(string=string)
    string_in_camel = pascal_to_camel(string=string_in_pascal)
    return string_in_camel


def retardify(string: str) -> str:
    """
    Converts given text to retardified text.
    >>> retardify(string="Hello, and good morning!") # Returns "hElLo, AnD gOoD mOrNiNg!"
    """
    string = string.lower().strip()
    counter = 0
    retardified_text = ""
    for character in string:
        if character in ALPHABETS:
            counter += 1
            if counter % 2 == 0:
                character = character.upper()
        retardified_text += character
    return retardified_text


def get_first_n_characters(text: str, num_chars: int) -> str:
    assert checks.is_positive_integer(num_chars), "Param `num_chars` must be a positive integer"
    return text[:num_chars]


def get_last_n_characters(text: str, num_chars: int) -> str:
    assert checks.is_positive_integer(num_chars), "Param `num_chars` must be a positive integer"
    return text[-num_chars:]


def remove_first_n_characters(text: str, num_chars: int) -> str:
    assert checks.is_positive_integer(num_chars), "Param `num_chars` must be a positive integer"
    return text[num_chars:]


def remove_last_n_characters(text: str, num_chars: int) -> str:
    assert checks.is_positive_integer(num_chars), "Param `num_chars` must be a positive integer"
    return text[:-num_chars]


def remove_characters_at_indices(*, text: str, indices: List[int]) -> str:
    """
    Removes characters present at the given `indices` in the `text`.
    Expects `indices` to be in range (0, n-1) where n is the length of the `text`.
    Raises an IndexError if any of the given `indices` are out of bounds.
    """
    if not indices:
        return text
    indices = sorted(list(set(indices)), reverse=True)
    lowest_possible_index, highest_possible_index = 0, len(text) - 1 # Must not use negative indices
    if indices[-1] < lowest_possible_index or indices[0] > highest_possible_index:
        raise IndexError(
            f"Accepted index-range for the given text is ({lowest_possible_index}, {highest_possible_index})."
            " Cannot remove character at an index outside of this range."
        )
    list_of_chars = list(text)
    for index in indices:
        list_of_chars.pop(index)
    return "".join(list_of_chars)

