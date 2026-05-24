from dataclasses import dataclass
import functools
import logging
import random
import time
from typing import Any, Callable, Dict, List, Literal, Optional, ParamSpec, Tuple, TypeVar

from slupy.dates.utils import get_timetaken_fstring

logger = logging.getLogger(__name__)


P = ParamSpec("P")
R = TypeVar("R")


def execute_with_decorator(
        *,
        decorator: Callable[[Callable[P, R]], Callable[P, R]],
        func: Callable[P, R],
    ) -> Callable[P, R]:
    """
    Applies a decorator to a callable through a direct function call instead of using the `@decorator` syntax.
    The `decorator` argument must be a decorator callable, or the result of a decorator factory.

    Example:
    ```python
    def main():
        pass

    decorated_func = execute_with_decorator(
        decorator=retry_on_exception(num_retries=5),
        func=main,
    )
    result = decorated_func(*args, **kwargs)
    ```

    Equivalent to:
    ```python
    @retry_on_exception(num_retries=5)
    def main():
        pass
    ```

    Parameters:
        decorator: The decorator to apply.
        func: The callable to decorate.

    Returns a decorated callable with the same signature and return type as the original function.
    """
    return decorator(func)


def timer(func: Callable) -> Callable:
    """Decorator that prints the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        time_taken_in_secs = round(end - start, 6)
        timetaken_fstring = get_timetaken_fstring(num_seconds=time_taken_in_secs)
        print(f"Executed function '{func.__name__}' in: {timetaken_fstring}")
        return result
    return wrapper_timer


def slow_down(func: Callable) -> Callable:
    """
    Decorator that slows down the execution of the decorated function.
    Slows down the execution by 10-20 minutes.
    """
    @functools.wraps(func)
    def wrapper_slow_down(*args, **kwargs):
        num_seconds_delayed = random.randint(600, 1200)
        time.sleep(num_seconds_delayed)
        return func(*args, **kwargs)
    return wrapper_slow_down


def repeat(*, num_times: int) -> Callable:
    """Decorator that executes the decorated function `num_times` times"""
    def repeat_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Repeating function '{func.__name__}' {num_times} times")
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return repeat_decorator


def functionality_injector(
        *,
        before: Optional[Callable] = None,
        after: Optional[Callable] = None,
    ) -> Callable:
    """
    Decorator that injects some functionality which gets executed before/after the decorated function.

    Parameters:
        - before (callable): Executes just before calling the decorated function.
        - after (callable): Executes just after calling the decorated function.
    """
    def outer_func(func: Callable) -> Callable:
        @functools.wraps(func)
        def inner_func(*args: Any, **kwargs: Any) -> Any:
            if before:
                before()
            result = func(*args, **kwargs)
            if after:
                after()
            return result
        return inner_func
    return outer_func


@dataclass
class RetryConfig:
    base_delay: int = 0
    backoff: Literal["constant", "linear", "exponential"] = "constant"
    jitter_range: Optional[Tuple[int, int]] = None

    def __post_init__(self):
        assert isinstance(self.base_delay, int) and self.base_delay >= 0, (
            "Param `base_delay` must be a non-negative integer"
        )
        assert self.jitter_range is None or (
            isinstance(self.jitter_range, tuple)
            and len(self.jitter_range) == 2
            and self.jitter_range[0] <= self.jitter_range[1]
        ), "Param `jitter_range` must be a tuple of two numbers (min, max) where min <= max"


def _compute_delays_between_retries(
        *,
        num_retries: int,
        retry_config: RetryConfig,
    ) -> List[int]:
    """
    Computes the delays (in seconds) between retries.
    For N retries, there will be N delays.
    """
    backoff_mapper: Dict[str, Callable[[int], int]] = {
        "constant": lambda retry_count: retry_config.base_delay,
        "linear": lambda retry_count: retry_config.base_delay * retry_count,
        "exponential": lambda retry_count: retry_config.base_delay * (2 ** (retry_count - 1)),
    }
    delays = []
    for retry_count in range(1, num_retries + 1):
        delay = backoff_mapper[retry_config.backoff](retry_count)
        delay = delay if retry_config.jitter_range is None else delay + random.uniform(*retry_config.jitter_range)
        delay = round(delay)
        delays.append(delay)
    return delays


def retry_on_exception(
        *,
        num_retries: int = 0,
        retry_config: Optional[RetryConfig] = None,
        include_error_log: Optional[bool] = False,
        include_error_traceback: Optional[bool] = False,
        raise_if_exception: Optional[bool] = True,
        func_name: Optional[str] = None,
    ) -> Callable:
    """
    Decorator used to retry a function in case of an exception.

    Usage:
    ```python
    @retry_on_exception(num_retries=3)
    def my_func():
        ...
    ```
    """

    assert isinstance(num_retries, int) and num_retries >= 0, (
        "Param `num_retries` must be a non-negative integer"
    )
    assert retry_config is None or isinstance(retry_config, RetryConfig), (
        "Param `retry_config` must be of type RetryConfig"
    )
    retry_config = retry_config or RetryConfig()

    def decorator(func: Callable) -> Callable:
        assert callable(func), "Decorated object must be a callable"

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delays_between_retries = _compute_delays_between_retries(
                num_retries=num_retries,
                retry_config=retry_config,
            )
            actual_func_name = func_name or func.__name__
            total_tries = num_retries + 1

            for try_count in range(1, total_tries + 1):
                is_first_try = (try_count == 1)
                is_last_try = (try_count == total_tries)
                try_count_string = (
                    "[Initial try]"
                    if is_first_try
                    else f"[Retry #{try_count - 1}/{total_tries - 1}]"
                )
                try:
                    result = func(*args, **kwargs)
                except Exception as exc:
                    if include_error_log:
                        msg = (
                            f"{try_count_string}"
                            f" Error while calling '{actual_func_name}'."
                            f" Error type: '{type(exc).__name__}'."
                        )
                        logger.error(
                            msg,
                            exc_info=include_error_traceback,
                        )
                    if is_last_try:
                        if raise_if_exception:
                            raise exc
                        return None
                    delay_in_secs = delays_between_retries[try_count - 1]
                    time.sleep(delay_in_secs)
                else:
                    return result

        return wrapper

    return decorator

