"""KST (UTC+9, no daylight saving) for every human-visible time (decision 0012).

Use this instead of the machine's local time: teammates' WSL may run in UTC.
"""

from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9), "KST")


def now_kst() -> datetime:
    return datetime.now(KST)
