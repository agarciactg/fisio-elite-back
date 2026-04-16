from app.modules.constants import TIMEZONE
from zoneinfo import ZoneInfo
from datetime import datetime


def _derive_status(last_visit: datetime | None, has_future: bool) -> str:
    if has_future:
        return "ACTIVE"
    if last_visit is None:
        return "INACTIVE"
    days_since = (datetime.now(ZoneInfo(TIMEZONE)) - last_visit).days
    if days_since <= 30:
        return "ACTIVE"
    if days_since <= 60:
        return "PACKAGE PENDING"
    return "INACTIVE"
