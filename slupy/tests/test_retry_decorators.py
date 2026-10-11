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
