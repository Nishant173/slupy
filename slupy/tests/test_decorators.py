import unittest
from unittest.mock import MagicMock, patch

from slupy.decorators.decorators import (
    execute_with_decorator,
    repeat,
)


class TestDecorators(unittest.TestCase):

    @patch("builtins.print", return_value=None)
    def test_execute_with_decorator_with_error(self, mock_print: MagicMock):
        call_count = 0
        num_times = 5

        def mock_func():
            nonlocal call_count
            call_count += 1

        decorated_func = execute_with_decorator(
            decorator=repeat(num_times=num_times),
            func=mock_func,
        )
        decorated_func()
        self.assertEqual(call_count, num_times)
        self.assertEqual(mock_print.call_count, 1)

    @patch("builtins.print", return_value=None)
    def test_execute_with_decorator_with_result(self, mock_print: MagicMock):
        call_count = 0
        num_times = 3

        def mock_func(number: int):
            nonlocal call_count
            call_count += 1
            return "Hello World" + " " + str(number)

        decorated_func = execute_with_decorator(
            decorator=repeat(num_times=num_times),
            func=mock_func,
        )
        result = decorated_func(123)
        self.assertEqual(result, "Hello World 123")
        self.assertEqual(call_count, 3)
        self.assertEqual(mock_print.call_count, 1)

