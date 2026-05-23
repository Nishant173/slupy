import unittest

from slupy.decorators.decorators import RetryConfig, retry_on_exception


@retry_on_exception(num_retries=3)
def zero_division_error_func():
    1 / 0


@retry_on_exception(num_retries=3)
def type_error_func():
    1 >= "1"


@retry_on_exception(
    num_retries=10,
    retry_config=RetryConfig(
        base_delay=10,
        backoff="exponential",
        jitter_range=(0, 5),
    ),
    include_error_log=True,
    include_error_traceback=True,
    raise_if_exception=False,
    func_name="SUCCESSFUL-FUNCTION",
)
def successful_func():
    return "success"


class TestDecorators(unittest.TestCase):

    def test_retry_on_exception(self):
        with self.assertRaises(ZeroDivisionError):  
            zero_division_error_func()

        with self.assertRaises(TypeError):  
            type_error_func()

        self.assertEqual(
            successful_func(),
            "success",
        )

