from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional, Tuple, Union

from slupy.dates import constants


def is_date_object(x: Any, /) -> bool:
    return isinstance(x, date) and x.__class__ is date


def is_datetime_object(x: Any, /) -> bool:
    return isinstance(x, datetime) and x.__class__ is datetime


def is_date_or_datetime_object(x: Any, /) -> bool:
    return isinstance(x, datetime) or isinstance(x, date)


def is_first_day_of_month(dt_obj: Union[datetime, date], /) -> bool:
    return dt_obj.day == 1


def is_last_day_of_month(dt_obj: Union[datetime, date], /) -> bool:
    if dt_obj.month in constants.MONTHS_HAVING_30_DAYS:
        return dt_obj.day == 30
    if dt_obj.month in constants.MONTHS_HAVING_31_DAYS:
        return dt_obj.day == 31
    return dt_obj.day == 29 if is_leap_year(dt_obj.year) else dt_obj.day == 28


def is_first_day_of_year(dt_obj: Union[datetime, date], /) -> bool:
    return dt_obj.month == 1 and dt_obj.day == 1


def is_last_day_of_year(dt_obj: Union[datetime, date], /) -> bool:
    return dt_obj.month == 12 and dt_obj.day == 31


def get_first_day_of_current_month(dt_obj: Union[datetime, date], /) -> Union[datetime, date]:
    return dt_obj.replace(day=1)


def get_last_day_of_current_month(dt_obj: Union[datetime, date], /) -> Union[datetime, date]:
    current_month = dt_obj.month
    if current_month in constants.MONTHS_HAVING_30_DAYS:
        return dt_obj.replace(day=30)
    elif current_month in constants.MONTHS_HAVING_31_DAYS:
        return dt_obj.replace(day=31)
    return dt_obj.replace(day=29) if is_leap_year(dt_obj.year) else dt_obj.replace(day=28)


def get_first_day_of_next_month(dt_obj: Union[datetime, date], /) -> Union[datetime, date]:
    if dt_obj.month == 12:
        return dt_obj.replace(year=dt_obj.year + 1, month=1, day=1)
    return dt_obj.replace(month=dt_obj.month + 1, day=1)


def is_february_29th(x: Union[datetime, date]) -> bool:
    assert is_date_or_datetime_object(x), "Param must be of type 'date' or 'datetime'"
    return x.month == 2 and x.day == 29


def compare_day_and_month(a: date, b: date, /) -> Literal["<", ">", "=="]:
    """
    Compares only the day and month of the given date objects.
        - If a < b, returns '<'
        - If a > b, returns '>'
        - If a == b, returns '=='
    """
    if a.month < b.month:
        return "<"
    if a.month > b.month:
        return ">"
    if a.day < b.day:
        return "<"
    if a.day > b.day:
        return ">"
    return "=="


def compute_date_difference(d1: date, d2: date, /) -> Tuple[int, int]:
    """Computes the absolute date-difference, and returns a tuple of (years, days)"""
    if d1 == d2:
        return (0, 0)
    if d1 > d2:
        d1, d2 = d2, d1  # ensure that d1 < d2

    d1_copy = d1.replace()
    year_difference = d2.year - d1.year
    operator = compare_day_and_month(d2, d1)
    if operator == ">":
        if is_february_29th(d1_copy):
            d1_copy = d1_copy.replace(year=d2.year, month=2, day=28)
        else:
            d1_copy = d1_copy.replace(year=d2.year)
    elif operator == "<":
        year_difference -= 1
        if is_february_29th(d1_copy):
            d1_copy = d1_copy.replace(year=d2.year - 1, month=2, day=28)
        else:
            d1_copy = d1_copy.replace(year=d2.year - 1)
    elif operator == "==":
        return (year_difference, 0)
    day_difference = (d2 - d1_copy).days
    return (year_difference, day_difference)


def is_leap_year(year: int, /) -> bool:
    assert isinstance(year, int), "Param `year` must be of type 'int'"
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return True if year % 400 == 0 else False


def get_day_of_week(
        dt_obj: Union[datetime, date],
        /,
        *,
        shorten: Optional[bool] = False,
    ) -> str:
    """
    Returns the day of the week.
    Day of week options when `shorten` is set to False: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].
    Day of week options when `shorten` is set to True: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].
    """
    if shorten:
        return dt_obj.strftime("%a")
    return dt_obj.strftime("%A")

