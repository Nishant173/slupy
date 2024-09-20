import unittest

from slupy.core import helpers


class Person:
    pass


class TestCore(unittest.TestCase):

    def test_create_repr(self):
        repr_string = helpers.create_repr(
            instance=Person(),
            kwargs_dict={"name": "james", "age": 42, "is_partner": False},
            multi_line=False,
        )
        self.assertEqual(
            repr_string,
            "Person(name='james', age=42, is_partner=False)",
        )

    def test_slice_by_position(self):
        sliceable_list = list(range(1, 30+1))
        sliceable_tuple = tuple(sliceable_list)
        sliceable_string = "hello world"

        self.assertEqual(
            helpers.slice_by_position(sliceable_list, start=5, end=12),
            list(range(5, 12+1)),
        )
        self.assertEqual(
            helpers.slice_by_position(sliceable_tuple, start=5, end=12),
            tuple(range(5, 12+1)),
        )
        self.assertEqual(
            helpers.slice_by_position(sliceable_string, start=2, end=8),
            "ello wo",
        )

