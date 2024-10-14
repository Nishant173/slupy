import unittest

from slupy.data_wrangler.data_wrangler import DataWrangler


class TestDataWrangler(unittest.TestCase):

    def setUp(self) -> None:
        self.list_of_dicts = [
            {
                "index": 1,
                "text": "AAA",
                "number": 10,
            },
            {
                "index": 2,
                "text": "AAA",
                "number": 20,
            },
            {
                "index": 3,
                "text": "AAA",
                "number": 30,
            },
            {
                "index": 4,
                "text": "BBB",
                "number": -1,
            },
            {
                "index": 5,
                "text": "BBB",
                "number": -1,
            },
            {
                "index": 6,
                "text": "BBB",
                "number": -5,
            },
            {
                "index": 7,
                "text": "CCC",
                "number": 45,
            },
            {
                "index": 8,
                "text": "CCC",
                "number": 50,
            },
            {
                "index": 9,
                "text": "CCC",
                "number": 50,
            },
        ]

    def test_has_duplicates(self):
        dw = DataWrangler(self.list_of_dicts)

        self.assertTrue(not dw.has_duplicates())
        self.assertTrue(dw.has_duplicates(subset=["text"]))
        self.assertTrue(dw.has_duplicates(subset=["text", "number"]))

        with self.assertRaises(KeyError):
            dw.has_duplicates(subset=["text", "number", "key-that-does-not-exist"])

        with self.assertRaises(KeyError):
            dw.has_duplicates(subset=["key-that-does-not-exist"])

        self.assertEqual(len(self.list_of_dicts), 9)

    def test_drop_duplicates(self):
        dw = DataWrangler(self.list_of_dicts)

        result_1 = dw.drop_duplicates(keep="first", subset=["text", "number"]).data
        self.assertEqual(len(result_1), 7)

        result_2 = dw.drop_duplicates(keep="first", subset=["text"]).data
        self.assertEqual(len(result_2), 3)
        self.assertEqual(
            result_2,
            [
                {
                    "index": 1,
                    "text": "AAA",
                    "number": 10,
                },
                {
                    "index": 4,
                    "text": "BBB",
                    "number": -1,
                },
                {
                    "index": 7,
                    "text": "CCC",
                    "number": 45,
                },
            ],
        )

        result_3 = dw.drop_duplicates(keep="last", subset=["text"]).data
        self.assertEqual(len(result_3), 3)
        self.assertEqual(
            result_3,
            [
                {
                    "index": 3,
                    "text": "AAA",
                    "number": 30,
                },
                {
                    "index": 6,
                    "text": "BBB",
                    "number": -5,
                },
                {
                    "index": 9,
                    "text": "CCC",
                    "number": 50,
                },
            ],
        )

        self.assertEqual(len(self.list_of_dicts), 9)

    def test_drop_duplicates_inplace(self):
        dw = DataWrangler(self.list_of_dicts, deep_copy=True)
        dw.drop_duplicates(keep="last", subset=["text"], inplace=True)
        result = dw.data
        self.assertEqual(len(result), 3)
        self.assertEqual(
            result,
            [
                {
                    "index": 3,
                    "text": "AAA",
                    "number": 30,
                },
                {
                    "index": 6,
                    "text": "BBB",
                    "number": -5,
                },
                {
                    "index": 9,
                    "text": "CCC",
                    "number": 50,
                },
            ],
        )
        self.assertEqual(len(self.list_of_dicts), 9)

    def test_apply_to_field(self):
        dw = DataWrangler(self.list_of_dicts)
        result = dw.apply_to_field(field="index", func=lambda value: value + 100).data

        result_expected = []
        for item in DataWrangler(self.list_of_dicts).data_copy():
            item["index"] += 100
            result_expected.append(item)

        self.assertEqual(result, result_expected)

        with self.assertRaises(KeyError):
            dw.apply_to_field(field="--index--", func=lambda value: value + 100)
        
        self.assertEqual(len(self.list_of_dicts), 9)

    def test_apply_to_field_inplace(self):
        dw = DataWrangler(self.list_of_dicts, deep_copy=True)
        dw.apply_to_field(field="index", func=lambda value: value + 100, inplace=True)
        result = dw.data

        result_expected = []
        for item in DataWrangler(self.list_of_dicts).data_copy():
            item["index"] += 100
            result_expected.append(item)

        self.assertEqual(result, result_expected)

        with self.assertRaises(KeyError):
            dw.apply_to_field(field="--index--", func=lambda value: value + 100, inplace=True)

        self.assertEqual(len(self.list_of_dicts), 9)

