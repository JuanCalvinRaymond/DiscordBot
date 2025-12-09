from datetime import datetime, timedelta
import time
import re

estTimeZone = (4 if time.daylight else 5)


def timestampConverter(arg: datetime) -> int:
    """
    Convert datetime object to Unix timestamp (int).

    :param arg: datetime.datetime the datetime to convert.
    :type arg: datetime

    :return: Unix timestamp (seconds since epoch).
    :rtype: int
    """
    unix_timestamp = int(time.mktime(arg.timetuple()))
    return unix_timestamp

def timezoneConverter(originalTime, utc = 0, format="t"):
    """
    Parse time string messages and return a discord timestamp tag.

    Parameters:
    originalTime: str — input time string (e.g., '4:30 pm', '17:00', '9 am+1').
    utc: int — optional timezone override (e.g., -4).
    format: str — Discord timestamp format code ('t','T','d','D','f','F','R').

    Supported input forms:
    'HH', 'HH:MM', 'HH:MM:SS'
    optional 'am'/'pm' suffix
    optional timezone offset like '+2' or '-4'
    if [utc](http://_vscodecontentref_/38) argument is provided (non-zero), it overrides parsed offset

    Returns:
    str: Discord-formatted timestamp tag, e.g. '<t:1234567890:t>'.
    """

    now_utc = datetime.now()

    clock = re.findall(r'\d+', originalTime)
    hour = int(clock[0])
    minute = int(clock[1] if len(clock) > 1 else 0)
    second = int(clock[2] if len(clock) > 2 else 0)

    timezone = re.search(r'[\+\-]\d', originalTime)
    tz = timezone.group() if timezone else 0
    tz = utc if utc != 0 else tz
    tzdiff = estTimeZone + int(tz)
    if "pm" in originalTime or hour > 12:
        # add 12 hour so 4 become 16, if condition is met
        # date = datetime(now_utc.year, now_utc.month, now_utc.day, int(clock[0]) + (0 if int(clock[0]) > 12 and int(clock[0]) != 0 else 12), minute, second)
        date = datetime(now_utc.year, now_utc.month, now_utc.day, hour + (0 if hour > 12 and hour != 0 else 12), minute, second) - timedelta(hours=tzdiff)

    # does it matter? if people don't specify am or pm, we just assume it's am
    # if "am" in time:
    else:
        # date = datetime(now_utc.year, now_utc.month, now_utc.day, int(clock[0]), minute, second)
        date = datetime(now_utc.year, now_utc.month, now_utc.day, hour, minute, second) - timedelta(hours=tzdiff)
    timestamp = timestampConverter(date)
    if "full" in originalTime:
        return f'<t:{timestamp}:f>'
    elif format != "":
        return f'<t:{timestamp}:{format}>'
    else:
        return f'<t:{timestamp}:t>'
