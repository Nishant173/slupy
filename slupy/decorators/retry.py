import asyncio
from dataclasses import dataclass
import functools
import logging
import random
import time
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Literal,
    Optional,
    ParamSpec,
    Tuple,
    TypeVar,
    Union,
)


logger = logging.getLogger(__name__)


P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class RetryConfig:
    num_retries: Union[int, None] = 0
    base_delay_in_seconds: float = 0.0
    backoff: Literal["constant", "linear", "exponential"] = "constant"
    jitter_range: Tuple[float, float] = (0.0, 0.0)
    should_retry: Callable[[Exception], bool] = lambda exc: isinstance(exc, Exception)

    def __post_init__(self):
        assert self.num_retries is None or (
            isinstance(self.num_retries, int)
            and self.num_retries >= 0
        ), (
            "Param `num_retries` must be a non-negative integer (or None)."
            " You can set to None if you want infinite retries."
        )
        assert isinstance(self.base_delay_in_seconds, float) and self.base_delay_in_seconds >= 0.0, (
            "Param `base_delay_in_seconds` must be a non-negative float"
        )
        assert (
            isinstance(self.jitter_range, tuple)
            and len(self.jitter_range) == 2
            and self.jitter_range[0] <= self.jitter_range[1]
        ), "Param `jitter_range` must be a tuple of two numbers (min, max) where min <= max"
        assert callable(self.should_retry), (
            "Param `should_retry` must be a callable which takes an Exception (exc) and returns a boolean"
        )

    def compute_delays_between_retries(self, *, retry_attempt: int) -> float:
        """Computes the delays (in seconds) between retries. The `retry_attempt` must be >= 1."""
        assert isinstance(retry_attempt, int) and retry_attempt >= 1, "Param `retry_attempt` must be >= 1"
        backoff_mapper: Dict[str, Callable[[int], float]] = {
            "constant": lambda retry_attempt: self.base_delay_in_seconds,
            "linear": lambda retry_attempt: self.base_delay_in_seconds * retry_attempt,
            "exponential": lambda retry_attempt: self.base_delay_in_seconds * (2 ** (retry_attempt - 1)),
        }
        delay = backoff_mapper[self.backoff](retry_attempt)
        delay += random.uniform(*self.jitter_range)
        delay = round(delay, 3)
        return delay


@dataclass
class RetryLoggingConfig:
    include_error_log: Optional[bool] = False
    include_error_traceback: Optional[bool] = False


def retry_on_exception(
        *,
        retry_config: Optional[RetryConfig] = None,
        log_config: Optional[RetryLoggingConfig] = None,
        raise_if_exception: Optional[bool] = True,
        func_name: Optional[str] = None,
    ) -> Callable[[Callable[P, R]], Callable[P, Optional[R]]]:
    """
    Decorator used to retry a function in case of an exception.

    Usage:
    ```python
    @retry_on_exception()
    def my_func():
        pass
    ```
    """

    assert retry_config is None or isinstance(retry_config, RetryConfig), (
        "Param `retry_config` must be of type RetryConfig"
    )
    assert log_config is None or isinstance(log_config, RetryLoggingConfig), (
        "Param `log_config` must be of type RetryLoggingConfig"
    )
    retry_config = retry_config or RetryConfig()
    log_config = log_config or RetryLoggingConfig()

    def decorator(func: Callable) -> Callable:
        assert callable(func), "Decorated object must be a callable"

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            actual_func_name = func_name or getattr(func, "__name__", "<unknown>")
            num_retries = (
                float("inf")
                if retry_config.num_retries is None else
                retry_config.num_retries
            )
            num_retries_str = "inf" if num_retries == float("inf") else str(int(num_retries))
            retry_attempt = 0

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    is_initial_try = (retry_attempt == 0)
                    if log_config.include_error_log:
                        attempt_info = (
                            "[Initial try]"
                            if is_initial_try
                            else f"[Retry #{retry_attempt}/{num_retries_str}]"
                        )
                        msg = (
                            f"Error while calling function '{actual_func_name}'."
                            f" Error type is '{type(exc).__name__}'."
                            f" {attempt_info}."
                        )
                        logger.error(
                            msg,
                            exc_info=log_config.include_error_traceback,
                        )
                    if not retry_config.should_retry(exc) or retry_attempt >= num_retries:
                        if raise_if_exception:
                            raise
                        return
                    retry_attempt += 1
                    delay_in_secs = retry_config.compute_delays_between_retries(retry_attempt=retry_attempt)
                    time.sleep(delay_in_secs)

        return wrapper

    return decorator


def retry_on_exception_async(
        *,
        retry_config: Optional[RetryConfig] = None,
        log_config: Optional[RetryLoggingConfig] = None,
        raise_if_exception: Optional[bool] = True,
        func_name: Optional[str] = None,
    ) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Coroutine[Any, Any, Optional[R]]]]:
    """
    Decorator used to retry an async function in case of an exception.

    Usage:
    ```python
    @retry_on_exception_async()
    async def my_func():
        pass
    ```
    """

    assert retry_config is None or isinstance(retry_config, RetryConfig), (
        "Param `retry_config` must be of type RetryConfig"
    )
    assert log_config is None or isinstance(log_config, RetryLoggingConfig), (
        "Param `log_config` must be of type RetryLoggingConfig"
    )
    retry_config = retry_config or RetryConfig()
    log_config = log_config or RetryLoggingConfig()

    def decorator(func: Callable) -> Callable:
        assert callable(func), "Decorated object must be a callable"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            actual_func_name = func_name or getattr(func, "__name__", "<unknown>")
            num_retries = (
                float("inf")
                if retry_config.num_retries is None else
                retry_config.num_retries
            )
            num_retries_str = "inf" if num_retries == float("inf") else str(int(num_retries))
            retry_attempt = 0

            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    is_initial_try = (retry_attempt == 0)
                    if log_config.include_error_log:
                        attempt_info = (
                            "[Initial try]"
                            if is_initial_try
                            else f"[Retry #{retry_attempt}/{num_retries_str}]"
                        )
                        msg = (
                            f"Error while calling function '{actual_func_name}'."
                            f" Error type is '{type(exc).__name__}'."
                            f" {attempt_info}."
                        )
                        logger.error(
                            msg,
                            exc_info=log_config.include_error_traceback,
                        )
                    if not retry_config.should_retry(exc) or retry_attempt >= num_retries:
                        if raise_if_exception:
                            raise
                        return
                    retry_attempt += 1
                    delay_in_secs = retry_config.compute_delays_between_retries(retry_attempt=retry_attempt)
                    await asyncio.sleep(delay_in_secs)

        return wrapper

    return decorator


