#!/usr/bin/env python
MAX_JOBS = 3
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

MIN_DATE = -8640000000000000
MAX_DATE = 8640000000000000


def time(hour: int, minute: int = 0, seconds: int = 0):
    return hour * HOUR + minute * MINUTE + seconds * SECOND
