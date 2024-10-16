import unittest

from slupy.core.helpers import make_deep_copy
from slupy.data_wrangler.data_wrangler import DataWrangler


class TestDataWrangler(unittest.TestCase):

    def setUp(self) -> None:
        self.list_data_1 = [
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
        self.list_data_2 = [
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
        ]
        self.list_data_3 = [
            {
                "index": 1,
                "text": None,
            },
            {
                "index": 2,
                "text": "BBB",
            },
            {
                "index": None,
                "text": None,
            },
            {
                "index": 4,
                "text": "DDD",
            },
        ]

    def test_has_duplicates(self):
        dw = DataWrangler(self.list_data_1)

        self.assertTrue(not dw.has_duplicates())
        self.assertTrue(dw.has_duplicates(subset=["text"]))
        self.assertTrue(dw.has_duplicates(subset=["text", "number"]))

        with self.assertRaises(KeyError):
            dw.has_duplicates(subset=["text", "number", "key-that-does-not-exist"])

        with self.assertRaises(KeyError):
            dw.has_duplicates(subset=["key-that-does-not-exist"])

        self.assertEqual(len(self.list_data_1), 9)

    def test_drop_duplicates(self):
        dw = DataWrangler(self.list_data_1)

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

        self.assertEqual(len(self.list_data_1), 9)

    def test_drop_duplicates_inplace(self):
        dw = DataWrangler(self.list_data_1, deep_copy=True)
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
        self.assertEqual(len(self.list_data_1), 9)

    def test_compute_field(self):
        dw = DataWrangler(self.list_data_1)
        result = dw.compute_field(field="index", func=lambda d: d["index"] + 100).data

        result_expected = []
        for item in DataWrangler(self.list_data_1).data_copy():
            item["index"] += 100
            result_expected.append(item)

        self.assertEqual(result, result_expected)

        with self.assertRaises(KeyError):
            dw.compute_field(field="index", func=lambda d: d["--index--"] + 100)

        self.assertEqual(len(self.list_data_1), 9)

    def test_compute_field_inplace(self):
        dw = DataWrangler(self.list_data_1, deep_copy=True)
        dw.compute_field(field="index", func=lambda d: d["index"] + 100, inplace=True)
        result = dw.data

        result_expected = []
        for item in DataWrangler(self.list_data_1).data_copy():
            item["index"] += 100
            result_expected.append(item)

        self.assertEqual(result, result_expected)

        with self.assertRaises(KeyError):
            dw.compute_field(field="index", func=lambda d: d["--index--"] + 100, inplace=True)

        self.assertEqual(len(self.list_data_1), 9)

    def test_drop_keys(self):
        dw = DataWrangler(self.list_data_2)
        result = dw.drop_keys(keys=["number", "key-that-does-not-exist"]).data
        result_expected = [
            {
                "index": 1,
                "text": "AAA",
            },
            {
                "index": 4,
                "text": "BBB",
            
            },
            {
                "index": 7,
                "text": "CCC",
            
            },
        ]
        self.assertEqual(result, result_expected)
        self.assertEqual(len(self.list_data_2), 3)
        self.assertTrue(
            bool(self.list_data_2)
            and all(["number" in dict_obj for dict_obj in self.list_data_2]),
        )

    def test_drop_keys_inplace(self):
        dw = DataWrangler(self.list_data_2, deep_copy=True)
        dw.drop_keys(keys=["number", "key-that-does-not-exist"], inplace=True)
        result = dw.data
        result_expected = [
            {
                "index": 1,
                "text": "AAA",
            },
            {
                "index": 4,
                "text": "BBB",
            
            },
            {
                "index": 7,
                "text": "CCC",
            
            },
        ]
        self.assertEqual(result, result_expected)
        self.assertEqual(len(self.list_data_2), 3)
        self.assertTrue(
            bool(self.list_data_2)
            and all(["number" in dict_obj for dict_obj in self.list_data_2]),
        )

    def test_fill_nulls(self):
        dw = DataWrangler(self.list_data_3)

        self.assertEqual(
            dw.fill_nulls(value="<HELLO>").data,
            [
                {
                    "index": 1,
                    "text": "<HELLO>",
                },
                {
                    "index": 2,
                    "text": "BBB",
                },
                {
                    "index": "<HELLO>",
                    "text": "<HELLO>",
                },
                {
                    "index": 4,
                    "text": "DDD",
                },
            ],
        )
        self.assertEqual(len(self.list_data_3), 4)

        self.assertEqual(
            dw.fill_nulls(value="<HELLO>", subset=["text"]).data,
            [
                {
                    "index": 1,
                    "text": "<HELLO>",
                },
                {
                    "index": 2,
                    "text": "BBB",
                },
                {
                    "index": None,
                    "text": "<HELLO>",
                },
                {
                    "index": 4,
                    "text": "DDD",
                },
            ],
        )
        self.assertEqual(len(self.list_data_3), 4)

    def test_fill_nulls_inplace(self):
        dw_1 = DataWrangler(self.list_data_3, deep_copy=True)
        self.assertEqual(
            dw_1.fill_nulls(value="<HELLO>", inplace=True).data,
            [
                {
                    "index": 1,
                    "text": "<HELLO>",
                },
                {
                    "index": 2,
                    "text": "BBB",
                },
                {
                    "index": "<HELLO>",
                    "text": "<HELLO>",
                },
                {
                    "index": 4,
                    "text": "DDD",
                },
            ],
        )
        self.assertEqual(len(self.list_data_3), 4)

        dw_2 = DataWrangler(self.list_data_3, deep_copy=True)
        self.assertEqual(
            dw_2.fill_nulls(value="<HELLO>", subset=["text"], inplace=True).data,
            [
                {
                    "index": 1,
                    "text": "<HELLO>",
                },
                {
                    "index": 2,
                    "text": "BBB",
                },
                {
                    "index": None,
                    "text": "<HELLO>",
                },
                {
                    "index": 4,
                    "text": "DDD",
                },
            ],
        )
        self.assertEqual(len(self.list_data_3), 4)

