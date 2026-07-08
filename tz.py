from datetime import datetime
from zoneinfo import ZoneInfo

MOSCOW = ZoneInfo("Europe/Moscow")


def now() -> datetime:
    return datetime.now(MOSCOW).replace(tzinfo=None)
