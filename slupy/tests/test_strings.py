import unittest

from slupy.strings import strings


class TestStrings(unittest.TestCase):

    def test_string_case_conversions(self):
        self.assertEqual(
            strings.camel_to_pascal("helloAndGoodMorning"),
            "HelloAndGoodMorning",
        )
        self.assertEqual(
            strings.pascal_to_camel("HelloAndGoodMorning"),
            "helloAndGoodMorning",
        )
        self.assertEqual(
            strings.pascal_to_snake("HelloAndGoodMorning"),
            "hello_and_good_morning",
        )
        self.assertEqual(
            strings.snake_to_pascal("hello_and_good_morning"),
            "HelloAndGoodMorning",
        )
        self.assertEqual(
            strings.camel_to_snake("helloAndGoodMorning"),
            "hello_and_good_morning",
        )
        self.assertEqual(
            strings.snake_to_camel("hello_and_good_morning"),
            "helloAndGoodMorning",
        )

    def test_string_slicing(self):
        self.assertEqual(
            strings.get_first_n_characters(text="hello-world", num_chars=4),
            "hell",
        )
        self.assertEqual(
            strings.get_last_n_characters(text="hello-world", num_chars=4),
            "orld",
        )
        self.assertEqual(
            strings.remove_first_n_characters(text="hello-world", num_chars=4),
            "o-world",
        )
        self.assertEqual(
            strings.remove_last_n_characters(text="hello-world", num_chars=4),
            "hello-w",
        )

    def test_remove_characters_at_indices(self):
        self.assertEqual(
            strings.remove_characters_at_indices(text="hello and good morning", indices=[]),
            "hello and good morning",
        )
        self.assertEqual(
            strings.remove_characters_at_indices(text="hello and good morning", indices=[6, 8, 11, 21]),
            "hello n god mornin",
        )
        with self.assertRaises(IndexError):
            strings.remove_characters_at_indices(text="hello and good morning", indices=[100])

    def test_to_dumbo_text(self):
        self.assertEqual(
            strings.to_dumbo_text("Hello, and good morning!"),
            "hElLo, AnD gOoD mOrNiNg!",
        )

    def test_make_message(self):
        self.assertEqual(
            strings.make_message("hello", prefix="prefix", suffix="suffix", sep="|"),
            "prefix|hello|suffix",
        )

