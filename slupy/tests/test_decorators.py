import unittest

from slupy.decorators.decorators import (
    execute_with_decorator,
    retry_on_exception,
)


class TestDecorators(unittest.TestCase):

    def test_retry_on_exception_for_success(self):
        call_count = 0
        num_retries = 5

        @retry_on_exception(num_retries=num_retries)
        def mock_func():
            nonlocal call_count
            call_count += 1
            return "Hello World"

        self.assertEqual(mock_func(), "Hello World")
        self.assertEqual(call_count, 1)

    def test_retry_on_exception_for_error(self):
        call_count = 0
        num_retries = 5

        @retry_on_exception(num_retries=num_retries)
        def mock_func():
            nonlocal call_count
            call_count += 1
            raise AssertionError()

        with self.assertRaises(AssertionError):
            mock_func()

        self.assertEqual(call_count, num_retries + 1)

    def test_execute_with_decorator_with_error(self):
        call_count = 0
        num_retries = 5

        def mock_func():
            nonlocal call_count
            call_count += 1
            raise ZeroDivisionError()

        decorated_func = execute_with_decorator(
            decorator=retry_on_exception(num_retries=num_retries),
            func=mock_func,
        )

        with self.assertRaises(ZeroDivisionError):
            decorated_func()

        self.assertEqual(call_count, num_retries + 1)

    def test_execute_with_decorator_with_result(self):
        call_count = 0
        num_retries = 5

        def mock_func(number: int):
            nonlocal call_count
            call_count += 1
            return "Hello World" + " " + str(number)

        decorated_func = execute_with_decorator(
            decorator=retry_on_exception(num_retries=num_retries),
            func=mock_func,
        )

        self.assertEqual(decorated_func(123), "Hello World 123")
        self.assertEqual(call_count, 1)


