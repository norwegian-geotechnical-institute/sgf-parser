"""
Datetime utilities for converting to and from datetime.datetime, json, naive and time zone aware
"""

from datetime import datetime, time

import dateutil.parser


def convert_str_to_datetime(date_string: str | None) -> datetime | None:
    """
    Guess what datetime is in the string
    """
    if not date_string or not isinstance(date_string, str):
        return None

    try:
        # The ISO 8601 format specifies that the time portion is separated from the date portion by a `T` character.
        if len(date_string) > 8 and "T" in date_string or len(date_string) == 8:
            return dateutil.parser.isoparse(date_string)
    except ValueError:
        pass

    try:
        return dateutil.parser.parse(date_string, parserinfo=dateutil.parser.parserinfo(yearfirst=True, dayfirst=True))
    except ValueError:
        pass

    return None


def convert_str_to_time(time_string: str | None) -> time | None:
    """
    Guess what time is in the string
    """
    if not time_string:
        return None

    try:
        return dateutil.parser.parse(f"1970-01-01 {time_string}").time()
    except ValueError:
        pass

    return None
