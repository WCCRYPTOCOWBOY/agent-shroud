from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Optional

def load_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"attempts": {"total": 0, "ok": 0, "failed": 0}, "last_result": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_metrics(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)

def observe_attempt(
    metrics: Dict[str, Any],
    ok: Optional[bool] = None,
    took_ms: Optional[int] = None,
) -> Dict[str, Any]:
    attempts = metrics.setdefault("attempts", {"total": 0, "ok": 0, "failed": 0})
    attempts["total"] += 1
    if ok is True:
        attempts["ok"] += 1
    elif ok is False:
        attempts["failed"] += 1
    metrics.setdefault("last_attempt", {})
    metrics["last_attempt"]["took_ms"] = took_ms
    return {"total": attempts["total"], "ok": attempts["ok"], "failed": attempts["failed"]}
