import random
import string
from typing import Dict, List, Optional

HEX_CODE_CHARSET = set(string.digits).union(set(string.ascii_uppercase))


def generate_random_hex_code() -> str:
    """Generates random 6-digit hexadecimal code"""
    random_hex_code = "#"
    for _ in range(6):
        random_hex_code += random.choice(HEX_CODE_CHARSET)
    return random_hex_code


def generate_random_hex_codes(*, how_many: int) -> List[str]:
    """Returns list of random 6-digit hexadecimal codes"""
    return [generate_random_hex_code() for _ in range(how_many)]


def generate_random_string(
        *,
        length: Optional[int] = 15,
        include_lowercase: Optional[bool] = True,
        include_uppercase: Optional[bool] = True,
        include_digits: Optional[bool] = True,
        include_punctuations: Optional[bool] = True,
    ) -> str:
    character_set = ""
    if include_lowercase:
        character_set += string.ascii_lowercase
    if include_uppercase:
        character_set += string.ascii_uppercase
    if include_digits:
        character_set += string.digits
    if include_punctuations:
        character_set += string.punctuation
    return "".join((random.choice(character_set) for _ in range(length)))

