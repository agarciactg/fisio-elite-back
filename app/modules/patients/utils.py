from app.modules.constants import TIMEZONE
from zoneinfo import ZoneInfo
from datetime import datetime


def _derive_status(last_visit: datetime | None, has_future: bool) -> str:
    if has_future:
        return "Disponible"
    
    if last_visit is None:
        return "Fuera"
    
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    
    if last_visit.tzinfo is None:
        last_visit = last_visit.replace(tzinfo=tz)
    
    days_since = (now - last_visit).days
    
    if days_since <= 30:
        return "Disponible"
    elif days_since <= 60:
        return "En sesión"
    else:
        return "Fuera"
