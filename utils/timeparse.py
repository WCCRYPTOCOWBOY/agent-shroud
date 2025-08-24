import re
from datetime import datetime, timedelta

TIME_RE = re.compile(r"(\b\d{1,2}(:\d{2})?\s*(am|pm)\b|\b\d{1,2}:\d{2}\b)", re.I)

def parse_when(text: str) -> datetime | None:
    now = datetime.utcnow()
    low = text.lower()
    if "tonight" in low:
        target = now.replace(hour=19, minute=0, second=0, microsecond=0)
        return target if now.hour < 19 else now + timedelta(hours=1)
    m = TIME_RE.search(text)
    if not m:
        return None
    raw = m.group(0).lower().replace(" ", "")
    try:
        if raw.endswith(("am","pm")):
            hhmm, ampm = raw[:-2], raw[-2:]
            hh, mm = (hhmm.split(":") + ["00"])[:2]
            h = int(hh) % 12
            if ampm == "pm": h += 12
            dt = now.replace(hour=h, minute=int(mm), second=0, microsecond=0)
            return dt if dt >= now else dt + timedelta(days=1)
        hh, mm = (raw.split(":") + ["00"])[:2]
        dt = now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
        return dt if dt >= now else dt + timedelta(days=1)
    except Exception:
        return None
