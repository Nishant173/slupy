from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Union

from slupy.core import checks
from slupy.dates import constants, utils
from slupy.dates.time_travel import TimeTravel


def offset_between_datetimes(
        *,
        start: Union[datetime, date],
        end: Union[datetime, date],
        offset_kwargs: Dict[str, int],
        ascending: Optional[bool] = True,
        as_string: Optional[bool] = False,
    ) -> Union[List[datetime], List[date], List[str]]:
    """
    Returns list of datetime/date/string objects separated by the given offset.

    For reference to `offset_kwargs` dictionary, please check the `slupy.dates.time_travel.TimeTravel` class' `add()`
    and `subtract()` methods.

    Examples:
    ```
    from datetime import date, datetime

    >>> offset_between_datetimes(
        start=date(year=2000, month=1, day=21),
        end=date(year=2000, month=1, day=27),
        offset_kwargs=dict(days=1),
        ascending=True,
        as_string=True,
    )  # Returns ["2000-01-21", "2000-01-22", "2000-01-23", "2000-01-24", "2000-01-25", "2000-01-26", "2000-01-27"]

    >>> offset_between_datetimes(
        start=date(year=2000, month=1, day=21),
        end=date(year=2000, month=1, day=27),
        offset_kwargs=dict(days=1),
        ascending=False,
        as_string=True,
    )  # Returns ["2000-01-27", "2000-01-26", "2000-01-25", "2000-01-24", "2000-01-23", "2000-01-22", "2000-01-21"]
    ```
    """
    assert (
        (utils.is_datetime_object(start) and utils.is_datetime_object(end))
        or (utils.is_date_object(start) and utils.is_date_object(end))
    ), (
        "Param `start` and `end` must be either both 'datetime' or both 'date'"
    )
    assert start <= end, "Param `start` must be <= `end`"
    assert len(offset_kwargs) == 1, "Only 1 offset can be used at a time"
    assert checks.is_boolean(ascending), "Param `ascending` must be of type 'bool'"
    assert checks.is_boolean(as_string), "Param `as_string` must be of type 'bool'"
    dt_objs = [start] if ascending else [end]
    time_travel = TimeTravel(start) if ascending else TimeTravel(end)
    while True:
        if ascending:
            time_travel.add(**offset_kwargs)
            if time_travel.value > end:
                break
            dt_objs.append(time_travel.value)
        else:
            time_travel.subtract(**offset_kwargs)
            if time_travel.value < start:
                break
            dt_objs.append(time_travel.value)
    if as_string:
        format_ = constants.DATETIME_FORMAT if time_travel.dtype == "DATETIME" else constants.DATE_FORMAT
        dt_objs = list(map(lambda x: x.strftime(format_), dt_objs))
    return dt_objs


def get_datetime_buckets(
        *,
        start: Union[datetime, date],
        num_buckets: int,
        offset_kwargs: Dict[str, int],
        ascending: Optional[bool] = True,
        as_string: Optional[bool] = False,
    ) -> Union[
        List[Tuple[datetime, datetime]],
        List[Tuple[date, date]],
        List[Tuple[str, str]],
    ]:
    """
    Returns list of buckets of datetime/date/string objects, where each bucket is separated by the given offset.

    For reference to `offset_kwargs` dictionary, please check the `slupy.dates.time_travel.TimeTravel` class' `add()`
    and `subtract()` methods.

    Examples:
    ```
    from datetime import date, datetime

    >>> get_datetime_buckets(
        start=date(year=2000, month=1, day=1),
        num_buckets=5,
        offset_kwargs=dict(weeks=1),
        ascending=True,
        as_string=True,
    )  # Returns [("2000-01-01", "2000-01-07"), ("2000-01-08", "2000-01-14"), ("2000-01-15", "2000-01-21"), ("2000-01-22", "2000-01-28"), ("2000-01-29", "2000-02-04")]

    >>> get_datetime_buckets(
        start=date(year=2000, month=1, day=1),
        num_buckets=3,
        offset_kwargs=dict(weeks=1),
        ascending=False,
        as_string=True,
    )  # Returns [("1999-12-12", "1999-12-18"), ("1999-12-19", "1999-12-25"), ("1999-12-26", "2000-01-01")]
    ```
    """
    assert utils.is_date_or_datetime_object(start), "Param `start` must be of type 'date' or 'datetime'"
    assert checks.is_positive_integer(num_buckets), "Param `num_buckets` must be a positive integer"
    assert len(offset_kwargs) == 1, "Only 1 offset can be used at a time"
    assert checks.is_boolean(ascending), "Param `ascending` must be of type 'bool'"
    assert checks.is_boolean(as_string), "Param `as_string` must be of type 'bool'"
    buckets = []
    num_buckets_filled = 0
    time_travel = TimeTravel(start)
    while True:
        if num_buckets_filled == num_buckets:
            break
        temp_start = time_travel.copy()
        if ascending:
            time_travel.add(**offset_kwargs)
            temp_end = time_travel.copy().subtract(days=1) if time_travel.dtype == "DATE" else time_travel.copy()
        else:
            time_travel.subtract(**offset_kwargs)
            temp_end = time_travel.copy().add(days=1) if time_travel.dtype == "DATE" else time_travel.copy()
        buckets.append((temp_start.value, temp_end.value))
        num_buckets_filled += 1
    if not ascending:
        buckets = [(y, x) for x, y in buckets][::-1]
    if as_string:
        format_ = constants.DATETIME_FORMAT if time_travel.dtype == "DATETIME" else constants.DATE_FORMAT
        buckets = [(x.strftime(format_), y.strftime(format_)) for x, y in buckets]
    return buckets

