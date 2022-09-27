import datetime
import time
from pytz import reference


def conv_longdate_to_str(longdate, local_tz=True):
    date_time = datetime.datetime.fromtimestamp(longdate / 1000.0)
    str_long_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
    if local_tz:
        str_long_date += " " + reference.LocalTimezone().tzname(date_time)

    return str_long_date


def get_time_in_milliseconds():
    """
    Returns the time in milliseconds since the epoch as an integer number.
    """
    return int(time.time() * 1000)
