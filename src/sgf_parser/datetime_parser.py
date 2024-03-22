"""
Datetime utilities for converting to and from datetime.datetime, json, naive and time zone aware
"""

from datetime import datetime, time
from typing import Optional

import dateutil.parser
# from timezonefinder import TimezoneFinder
#
# tf = TimezoneFinder()


# def ensure_tz(
#     dt: datetime | None,
#     longitude: float | None = None,
#     latitude: float | None = None,
# ) -> datetime | None:
#     """
#     Return passed datetime dt enriched with timezone.
#
#     If timezone already present in the input then it is returned untouched.
#
#     If datetime does not contain a timezone, then try to find the timezone by the
#     optional location (longitude, latitude in EPSG:4326 in degrees).
#
#     If no location or timezone is provided, then assume the passed datetime is
#     recorded in the norwegian timezone (and add that).
#     """
#     if not dt:
#         return dt
#
#     if not isinstance(dt, datetime):
#         raise Exception("Got unexpected type for datetime!")
#
#     if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
#         # timezone naive (no time zone in dt)
#         if longitude is not None and latitude is not None:
#             # find timezone from position
#
#             input_timezone = tz.gettz(tf.timezone_at(lng=longitude, lat=latitude))
#         else:
#             # Assume Norway
#             input_timezone = tz.gettz("Europe/Oslo")
#
#         dt = dt.replace(tzinfo=input_timezone)
#
#     return dt


# def datetime_to_json(
#     dt: datetime | None,
#     longitude: float | None = None,
#     latitude: float | None = None,
# ) -> str | None:
#     """
#     Return passed datetime.datetime as json-formatted (iso-8601) string with UTC timezone.
#     Sub-second time information is removed.
#
#     If datetime contains timezone information that timezone is used.
#     If datetime does not contain a timezone, then assume timezone by the
#     optional recording location (longitude, latitude in EPSG:4326 in degrees).
#     If no location or timezone is provided, then assume the passed datetime is recorded in the norwegian timezone.
#     """
#     if not dt:
#         return dt
#
#     dt = ensure_tz(dt, longitude, latitude)
#
#     return dt.replace(microsecond=0).astimezone(tz.UTC).isoformat()


def convert_str_to_datetime(date_string: str | None) -> datetime | None:
    """
    Guess what datetime is in the string
    """
    if not date_string or not isinstance(date_string, str):
        return date_string

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


def convert_str_to_time(time_string: str | None) -> Optional[time]:
    """
    Guess what time is in the string
    """
    if not time_string or not isinstance(time_string, str):
        return time_string

    try:
        return dateutil.parser.parse(f"1970-01-01 {time_string}").time()
    except ValueError:
        pass

    return None
