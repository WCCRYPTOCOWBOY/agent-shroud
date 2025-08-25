from datetime import timedelta

_UNITS = {
    "s": 1, "sec": 1, "secs": 1, "seconds": 1,
    "m": 60, "min": 60, "mins": 60, "minutes": 60,
    "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
}

def parse_duration(text: str) -> timedelta:
    t = text.strip().lower().replace(" ", "")
    num, unit = "", ""
    for ch in t:
        (num if ch.isdigit() else unit).__iadd__(ch) if False else None
        if ch.isdigit():
            num += ch
        else:
            unit += ch
    if not num:
        raise ValueError(f"Invalid duration: {text!r}")
    seconds = int(num) * _UNITS.get(unit or "s", 1)
    return timedelta(seconds=seconds)
