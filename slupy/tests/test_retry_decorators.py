import logging
import unittest
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

from slupy.decorators.retry import (
    retry_on_exception,
    retry_on_exception_async,
    RetryConfig,
    RetryLoggingConfig,
)


class TestRetryConfig(unittest.TestCase):

    def test_valid_retry_config(self):
        retry_config = RetryConfig(
            num_retries=3,
            base_delay_in_seconds=10.0,
            backoff="linear",
            jitter_range=(1.0, 2.0),
            should_retry=lambda exc: isinstance(exc, (ValueError, TypeError)),
        )
        self.assertIsInstance(retry_config, RetryConfig)

        ## since there is a random jitter_range, let's check if the delay is correctly computed multiple times
        for _ in range(10_000):
            self.assertTrue(
                11 <= retry_config.compute_delays_between_retries(retry_attempt=1) <= 12
            )
            self.assertTrue(
                61 <= retry_config.compute_delays_between_retries(retry_attempt=6) <= 62
            )
            self.assertTrue(
                251 <= retry_config.compute_delays_between_retries(retry_attempt=25) <= 252
            )

    def test_invalid_should_retry(self):
        with self.assertRaises(AssertionError) as exc:
            RetryConfig(
                num_retries=3,
                should_retry=False,
            )
        self.assertEqual(
            str(exc.exception),
            "Param `should_retry` must be a callable which takes an Exception (exc) and returns a boolean",
        )


class TestRetryDecorators(unittest.IsolatedAsyncioTestCase):

    # ==========================================
    # TESTS FOR SYNCHRONOUS DECORATOR
    # ==========================================

    @patch("time.sleep", return_value=None)
    def test_sync_success_on_first_try(self, mock_sleep: MagicMock):
        call_count = 0

        @retry_on_exception(retry_config=RetryConfig(num_retries=3))
        def sample_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = sample_func()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 1)
        mock_sleep.assert_not_called()

    @patch("time.sleep", return_value=None)
    def test_sync_succeeds_after_retries(self, mock_sleep: MagicMock):
        call_count = 0

        @retry_on_exception(retry_config=RetryConfig(num_retries=3))
        def sample_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "recovered"

        result = sample_func()
        self.assertEqual(result, "recovered")
        self.assertEqual(call_count, 3)  # 1 initial try + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep", return_value=None)
    def test_sync_exhausts_retries_raises_exception(self, mock_sleep: MagicMock):
        call_count = 0

        @retry_on_exception(
            retry_config=RetryConfig(
                num_retries=2,
            )
        )
        def sample_func():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent failure")

        with self.assertRaises(ConnectionError):
            sample_func()

        self.assertEqual(call_count, 3)  # 1 initial try + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep", return_value=None)
    def test_sync_custom_should_retry_filter(self, mock_sleep: MagicMock):
        call_count = 0

        @retry_on_exception(
            retry_config=RetryConfig(
                num_retries=3,
                should_retry=lambda exc: isinstance(exc, ValueError)  # Don't retry ConnectionError
            ),
        )
        def sample_func():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Fatal error")

        with self.assertRaises(ConnectionError):
            sample_func()

        self.assertEqual(call_count, 1)
        mock_sleep.assert_not_called()

    # ==========================================
    # TESTS FOR ASYNCHRONOUS DECORATOR
    # ==========================================

    @patch("asyncio.sleep", return_value=None)
    async def test_async_success_on_first_try(self, mock_async_sleep: AsyncMock):
        call_count = 0

        @retry_on_exception_async(retry_config=RetryConfig(num_retries=3))
        async def sample_async_func():
            nonlocal call_count
            call_count += 1
            return "async success"

        result = await sample_async_func()
        self.assertEqual(result, "async success")
        self.assertEqual(call_count, 1)
        mock_async_sleep.assert_not_called()

    @patch("asyncio.sleep", return_value=None)
    async def test_async_succeeds_after_retries(self, mock_async_sleep: AsyncMock):
        call_count = 0

        @retry_on_exception_async(retry_config=RetryConfig(num_retries=3))
        async def sample_async_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Async timeout")
            return "async recovered"

        result = await sample_async_func()
        self.assertEqual(result, "async recovered")
        self.assertEqual(call_count, 3)
        self.assertEqual(mock_async_sleep.call_count, 2)

    @patch("asyncio.sleep", return_value=None)
    async def test_async_exhausts_retries_raises_exception(self, mock_async_sleep: AsyncMock):
        call_count = 0

        @retry_on_exception_async(
            retry_config=RetryConfig(
                num_retries=2,
            ),
        )
        async def sample_async_func():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Fatal async crash")

        with self.assertRaises(RuntimeError):
            await sample_async_func()

        self.assertEqual(call_count, 3)
        self.assertEqual(mock_async_sleep.call_count, 2)


class TestRetryLogging(unittest.IsolatedAsyncioTestCase):

    @patch("time.sleep", return_value=None)
    def test_sync_retry_log_attempt_labels(self, mock_sleep: MagicMock):
        call_count = 0

        @retry_on_exception(
            retry_config=RetryConfig(num_retries=5),
            log_config=RetryLoggingConfig(include_error_log=True),
        )
        def flaky_func():
            nonlocal call_count
            call_count += 1
            # Fail 5 times, succeed on the 6th time (Retry #5)
            if call_count < 6:
                raise ValueError("Temporary failure")
            return "recovered"

        with self.assertLogs("slupy.decorators.retry", level="ERROR") as cm:
            result = flaky_func()

        self.assertEqual(result, "recovered")

        # cm.output contains all logged messages strings
        log_messages = cm.output

        # Verify that the correct attempt tags were logged sequentially
        self.assertTrue(any("[Initial try]" in msg for msg in log_messages), "Missing [Initial try] log")
        self.assertTrue(any("[Retry #1/5]" in msg for msg in log_messages), "Missing [Retry #1/5] log")
        self.assertTrue(any("[Retry #2/5]" in msg for msg in log_messages), "Missing [Retry #2/5] log")
        self.assertTrue(any("[Retry #3/5]" in msg for msg in log_messages), "Missing [Retry #3/5] log")
        self.assertTrue(any("[Retry #4/5]" in msg for msg in log_messages), "Missing [Retry #4/5] log")
        self.assertTrue(not any("[Retry #5/5]" in msg for msg in log_messages), "[Retry #5/5] log should be missing")

    @patch("asyncio.sleep", return_value=None)
    async def test_async_retry_log_attempt_labels(self, mock_async_sleep: AsyncMock):
        call_count = 0

        @retry_on_exception_async(
            retry_config=RetryConfig(num_retries=5),
            log_config=RetryLoggingConfig(include_error_log=True),
        )
        async def flaky_async_func():
            nonlocal call_count
            call_count += 1
            # Fail 5 times, succeed on the 6th time (Retry #5)
            if call_count < 6:
                raise ValueError("Temporary async failure")
            return "async recovered"

        with self.assertLogs("slupy.decorators.retry", level="ERROR") as cm:
            result = await flaky_async_func()

        self.assertEqual(result, "async recovered")

        # cm.output contains all logged message strings
        log_messages = cm.output

        # Verify that the correct attempt tags were logged sequentially
        self.assertTrue(any("[Initial try]" in msg for msg in log_messages), "Missing [Initial try] log")
        self.assertTrue(any("[Retry #1/5]" in msg for msg in log_messages), "Missing [Retry #1/5] log")
        self.assertTrue(any("[Retry #2/5]" in msg for msg in log_messages), "Missing [Retry #2/5] log")
        self.assertTrue(any("[Retry #3/5]" in msg for msg in log_messages), "Missing [Retry #3/5] log")
        self.assertTrue(any("[Retry #4/5]" in msg for msg in log_messages), "Missing [Retry #4/5] log")
        self.assertTrue(not any("[Retry #5/5]" in msg for msg in log_messages), "[Retry #5/5] log should be missing")

