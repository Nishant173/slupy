import unittest

from slupy.core import dev_helpers


class Person:
    pass


class TestCore(unittest.TestCase):

    def test_create_repr(self):
        repr_string = dev_helpers.create_repr(
            instance=Person(),
            kwargs_dict={"name": "james", "age": 42, "is_partner": False},
            multi_line=False,
        )
        self.assertEqual(
            repr_string,
            "Person(name='james', age=42, is_partner=False)",
        )

