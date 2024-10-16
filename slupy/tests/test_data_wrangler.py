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
        self.list_data_1_copy = make_deep_copy(self.list_data_1)
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
        self.list_data_2_copy = make_deep_copy(self.list_data_2)
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
        self.list_data_3_copy = make_deep_copy(self.list_data_3)
        self.list_data_4 = [
            {
                "a": 1,
                "b": 2,
                "c": 3,
            },
            {
                "a": 10,
                "b": 20,
            },
            {
                "a": 100,
                "b": 200,
            },
        ]
        self.list_data_4_copy = make_deep_copy(self.list_data_4)
        self.list_data_5 = [
            {
                "text": "AAA",
                "number": -1,
            },
            {
                "text": "BBB",
                "number": -1,
            },
            {
                "text": "AAA",
                "number": 50,
            },
            {
                "text": "BBB",
                "number": 50,
            },
            {
                "text": "BBB",
                "number": 20,
            },
            {
                "text": "AAA",
                "number": 5,
            },
        ]
        self.list_data_5_copy = make_deep_copy(self.list_data_5)

    def _assert_list_data_is_unchanged(self):
        msg = "The value of list data should not be modified in-place"

        self.assertEqual(
            self.list_data_1,
            self.list_data_1_copy,
            msg=msg,
        )
        self.assertNotEqual(
            id(self.list_data_1),
            id(self.list_data_1_copy),
        )

        self.assertEqual(
            self.list_data_2,
            self.list_data_2_copy,
            msg=msg,
        )
        self.assertNotEqual(
            id(self.list_data_2),
            id(self.list_data_2_copy),
        )

        self.assertEqual(
            self.list_data_3,
            self.list_data_3_copy,
            msg=msg,
        )
        self.assertNotEqual(
            id(self.list_data_3),
            id(self.list_data_3_copy),
        )

        self.assertEqual(
            self.list_data_4,
            self.list_data_4_copy,
            msg=msg,
        )
        self.assertNotEqual(
            id(self.list_data_4),
            id(self.list_data_4_copy),
        )

        self.assertEqual(
            self.list_data_5,
            self.list_data_5_copy,
            msg=msg,
        )
        self.assertNotEqual(
            id(self.list_data_5),
            id(self.list_data_5_copy),
        )

    def test_len(self):
        dw = DataWrangler(self.list_data_1)
        self.assertEqual(len(dw), len(dw.data))
        self._assert_list_data_is_unchanged()

    def test_getitem(self):
        dw = DataWrangler(self.list_data_1)

        self.assertEqual(dw[0], dw.data[0])
        self.assertEqual(dw[-1], dw.data[-1])

        with self.assertRaises(IndexError):
            dw[len(dw)]  # Should always raise IndexError since len(dw) will always be > it's last index

        self._assert_list_data_is_unchanged()

    def test_has_duplicates(self):
        dw = DataWrangler(self.list_data_1)

        self.assertTrue(not dw.has_duplicates())
        self.assertTrue(dw.has_duplicates(subset=["text"]))
        self.assertTrue(dw.has_duplicates(subset=["text", "number"]))

        with self.assertRaises(KeyError):
            dw.has_duplicates(subset=["text", "number", "key-that-does-not-exist"])

        with self.assertRaises(KeyError):
            dw.has_duplicates(subset=["key-that-does-not-exist"])

        self._assert_list_data_is_unchanged()

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

        self._assert_list_data_is_unchanged()

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
        self._assert_list_data_is_unchanged()

    def test_get_values_by_field(self):
        dw = DataWrangler(self.list_data_4)

        self.assertEqual(
            dw.get_values_by_field(field="a"),
            [1, 10, 100],
        )
        self.assertEqual(
            dw.get_values_by_field(field="b"),
            [2, 20, 200],
        )

        with self.assertRaises(KeyError):
            dw.get_values_by_field(field="c")

        self._assert_list_data_is_unchanged()

    def test_get_unique_fields(self):
        dw = DataWrangler(self.list_data_1, deep_copy=True)
        self.assertEqual(
            dw.get_unique_fields(),
            ["index", "number", "text"],
        )
        self._assert_list_data_is_unchanged()

        dw.compute_field(field="new_field", func=lambda d: None, inplace=True)
        self.assertEqual(
            dw.get_unique_fields(),
            ["index", "new_field", "number", "text"],
        )
        self._assert_list_data_is_unchanged()

    def test_set_defaults_for_fields(self):
        dw = DataWrangler(self.list_data_4)
        result = dw.set_defaults_for_fields(fields=["c", "d"]).data
        result_expected = [
            {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": None,
            },
            {
                "a": 10,
                "b": 20,
                "c": None,
                "d": None,
            },
            {
                "a": 100,
                "b": 200,
                "c": None,
                "d": None,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

    def test_set_defaults_for_fields_inplace(self):
        dw = DataWrangler(self.list_data_4, deep_copy=True)
        dw.set_defaults_for_fields(fields=["c", "d"], inplace=True)
        result = dw.data
        result_expected = [
            {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": None,
            },
            {
                "a": 10,
                "b": 20,
                "c": None,
                "d": None,
            },
            {
                "a": 100,
                "b": 200,
                "c": None,
                "d": None,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

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

        self._assert_list_data_is_unchanged()

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

        self._assert_list_data_is_unchanged()

    def test_drop_fields(self):
        dw = DataWrangler(self.list_data_2)
        result = dw.drop_fields(fields=["number", "key-that-does-not-exist"]).data
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
        self._assert_list_data_is_unchanged()

    def test_drop_fields_inplace(self):
        dw = DataWrangler(self.list_data_2, deep_copy=True)
        dw.drop_fields(fields=["number", "key-that-does-not-exist"], inplace=True)
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
        self._assert_list_data_is_unchanged()

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
        self._assert_list_data_is_unchanged()

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
        self._assert_list_data_is_unchanged()

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
        self._assert_list_data_is_unchanged()

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
        self._assert_list_data_is_unchanged()

    def test_autofill_from_init(self):
        dw = DataWrangler(self.list_data_4, deep_copy=True, autofill=True)
        result = dw.data
        result_expected = [
            {
                "a": 1,
                "b": 2,
                "c": 3,
            },
            {
                "a": 10,
                "b": 20,
                "c": None,
            },
            {
                "a": 100,
                "b": 200,
                "c": None,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

    def test_autofill_missing_fields(self):
        dw = DataWrangler(self.list_data_4)
        result = dw.autofill_missing_fields().data
        result_expected = [
            {
                "a": 1,
                "b": 2,
                "c": 3,
            },
            {
                "a": 10,
                "b": 20,
                "c": None,
            },
            {
                "a": 100,
                "b": 200,
                "c": None,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

    def test_autofill_missing_fields_inplace(self):
        dw = DataWrangler(self.list_data_4, deep_copy=True)
        dw.autofill_missing_fields(inplace=True)
        result = dw.data
        result_expected = [
            {
                "a": 1,
                "b": 2,
                "c": 3,
            },
            {
                "a": 10,
                "b": 20,
                "c": None,
            },
            {
                "a": 100,
                "b": 200,
                "c": None,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

    def test_drop_nulls(self):
        dw = DataWrangler(self.list_data_3)

        result_1 = dw.drop_nulls().data
        result_expected_1 = [
            {
                "index": 2,
                "text": "BBB",
            },
            {
                "index": 4,
                "text": "DDD",
            },
        ]
        self.assertEqual(result_1, result_expected_1)
        self._assert_list_data_is_unchanged()

        result_2 = dw.drop_nulls(subset=["index"]).data
        result_expected_2 = [
            {
                "index": 1,
                "text": None,
            },
            {
                "index": 2,
                "text": "BBB",
            },
            {
                "index": 4,
                "text": "DDD",
            },
        ]
        self.assertEqual(result_2, result_expected_2)
        self._assert_list_data_is_unchanged()

    def test_drop_nulls_inplace(self):
        dw_1 = DataWrangler(self.list_data_3, deep_copy=True)
        dw_1.drop_nulls(inplace=True)
        result_1 = dw_1.data
        result_expected_1 = [
            {
                "index": 2,
                "text": "BBB",
            },
            {
                "index": 4,
                "text": "DDD",
            },
        ]
        self.assertEqual(result_1, result_expected_1)
        self._assert_list_data_is_unchanged()

        dw_2 = DataWrangler(self.list_data_3, deep_copy=True)
        dw_2.drop_nulls(subset=["index"], inplace=True)
        result_2 = dw_2.data
        result_expected_2 = [
            {
                "index": 1,
                "text": None,
            },
            {
                "index": 2,
                "text": "BBB",
            },
            {
                "index": 4,
                "text": "DDD",
            },
        ]
        self.assertEqual(result_2, result_expected_2)
        self._assert_list_data_is_unchanged()

    def test_filter_rows(self):
        dw = DataWrangler(self.list_data_1)
        
        with self.assertRaises(AssertionError):
            dw.filter_rows(func=lambda d: d)
        
        result = dw.filter_rows(func=lambda d: d["text"] == "AAA" and d["index"] % 2 != 0).data
        result_expected = [
            {
                "index": 1,
                "text": "AAA",
                "number": 10,
            },
            {
                "index": 3,
                "text": "AAA",
                "number": 30,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

    def test_filter_rows_inplace(self):
        dw = DataWrangler(self.list_data_1, deep_copy=True)
        
        with self.assertRaises(AssertionError):
            dw.filter_rows(func=lambda d: d, inplace=True)

        dw.filter_rows(func=lambda d: d["text"] == "AAA" and d["index"] % 2 != 0, inplace=True)
        result = dw.data
        result_expected = [
            {
                "index": 1,
                "text": "AAA",
                "number": 10,
            },
            {
                "index": 3,
                "text": "AAA",
                "number": 30,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

    def test_order_by(self):
        dw = DataWrangler(self.list_data_5)
        dw_ordered = dw.order_by(fields=["number", "text"], ascending=[False, False])
        self.assertNotEqual(
            id(dw),
            id(dw_ordered),
        )
        result = dw_ordered.data
        result_expected = [
            {
                "text": "BBB",
                "number": 50,
            },
            {
                "text": "AAA",
                "number": 50,
            },
            {
                "text": "BBB",
                "number": 20,
            },
            {
                "text": "AAA",
                "number": 5,
            },
            {
                "text": "BBB",
                "number": -1,
            },
            {
                "text": "AAA",
                "number": -1,
            },
        ]
        self.assertEqual(result, result_expected)
        self._assert_list_data_is_unchanged()

