# shroud/scheduler.py
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# --- .env loading (optional, won’t crash if python-dotenv isn’t installed) ---
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    def load_dotenv(*_args: Any, **_kwargs: Any) -> None:
        return

# --- Package-local utils (your files) ---
try:
    from shroud.utils.logger import setup_logger  # type: ignore
except Exception:
    # Fallback logger if your utils.logger isn't present yet
    import logging
    def setup_logger(name: str = "shroud", level: int = 20) -> logging.Logger:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        return logging.getLogger(name)

from shroud.utils.stopwatch import Stopwatch  # type: ignore
from shroud.utils.timeparse import parse_duration  # type: ignore
from shroud.utils.metrics import (  # type: ignore
    load_metrics,
    save_metrics,
    observe_attempt,
)

# --- Optional: a client hook (safe if missing) ---
try:
    # e.g., you have clients/silhouette.py with a run() function
    from clients.silhouette import run as run_silhouette  # type: ignore
except Exception:
    run_silhouette = None  # type: ignore


# ----------------------------
# Configuration & Data Models
# ----------------------------
ROOT = Path(__file__).resolve().parents[1]  # project root (folder that contains /shroud)
DEFAULT_METRICS_PATH = ROOT / "metrics.json"

@dataclass
class RunConfig:
    mode: str = "run"            # "run", "test", "ping"
    dry_run: bool = False
    interval: str = "5m"         # human-friendly (e.g. "30s", "5m", "1h")
    once: bool = True            # run once by default; set False to loop
    metrics_path: Path = DEFAULT_METRICS_PATH


# ----------------------------
# Core Task(s)
# ----------------------------
def do_one_job(cfg: RunConfig, logger) -> Dict[str, Any]:
    """
    One pass of whatever your agent should do.
    This is the place to call clients, handlers, etc.
    """
    with Stopwatch() as sw:
        result: Dict[str, Any] = {
            "ok": True,
            "took_ms": None,
            "details": {},
            "dry_run": cfg.dry_run,
            "mode": cfg.mode,
        }

        logger.info("Job start | mode=%s | dry_run=%s", cfg.mode, cfg.dry_run)

        # Example: call an external client if available
        if run_silhouette:
            try:
                payload = {"dry_run": cfg.dry_run, "mode": cfg.mode}
                details = run_silhouette(payload)  # your client decides what to do
                result["details"]["silhouette"] = details
            except Exception as e:
                logger.exception("Silhouette client error: %s", e)
                result["ok"] = False
        else:
            # Placeholder “work” so the pipeline is demonstrably alive
            time.sleep(0.05)  # simulate real work
            result["details"]["note"] = "silhouette client not present; did placeholder work"

        result["took_ms"] = int(sw.elapsed_ms)
        logger.info("Job done in %sms | ok=%s", result["took_ms"], result["ok"])
        return result


def run_loop(cfg: RunConfig, logger) -> None:
    """
    Single-run (default) or interval loop depending on cfg.once.
    Tracks attempts & durations in metrics.json via your utils.
    """
    # Load or initialize metrics
    metrics_path = cfg.metrics_path
    metrics: Dict[str, Any] = {}
    try:
        metrics = load_metrics(metrics_path)
    except Exception:
        logger.warning("No metrics file yet; will create on save. path=%s", metrics_path)

    attempt_info = observe_attempt(metrics)  # updates counters/timestamps inside the dict
    logger.debug("Observed attempt: %s", attempt_info)

    # Run once or loop:
    interval_seconds = int(parse_duration(cfg.interval).total_seconds())

    def _one():
        res = do_one_job(cfg, logger)
        # Update metrics
        attempt_info = observe_attempt(metrics, ok=res["ok"], took_ms=res["took_ms"])
        metrics.setdefault("last_result", {})["ok"] = res["ok"]
        metrics["last_result"]["took_ms"] = res["took_ms"]
        metrics["last_result"]["mode"] = res["mode"]
        try:
            save_metrics(metrics_path, metrics)
        except Exception as e:
            logger.warning("Failed to save metrics %s: %s", metrics_path, e)

    if cfg.once:
        _one()
    else:
        logger.info("Entering loop every %ss (Ctrl+C to stop)", interval_seconds)
        try:
            while True:
                _one()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Loop interrupted by user")


# ----------------------------
# CLI / Entry
# ----------------------------
def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="shroud", description="Shroud scheduler/runner")
    p.add_argument("--mode", choices=["run", "test", "ping"], default="run",
                   help="Operational mode for the agent/scheduler.")
    p.add_argument("--dry-run", action="store_true",
                   help="Do not perform side-effecting actions (safe simulation).")
    p.add_argument("--interval", default="5m",
                   help="Loop interval (e.g., '30s', '5m', '1h'). Used if --once is not set.")
    p.add_argument("--once", action="store_true",
                   help="Run exactly one cycle and exit (default).")
    p.add_argument("--loop", action="store_true",
                   help="Run continuously at the provided --interval.")
    p.add_argument("--metrics", default=str(DEFAULT_METRICS_PATH),
                   help="Path to metrics.json file.")
    p.add_argument("--log-level", default="INFO",
                   help="Python logging level (DEBUG, INFO, WARNING, ERROR).")
    return p


def make_config(args: argparse.Namespace) -> RunConfig:
    return RunConfig(
        mode=args.mode,
        dry_run=args.dry_run,
        interval=args.interval,
        once=not args.loop,  # --loop flips this off
        metrics_path=Path(args.metrics).resolve(),
    )


def main(argv: Optional[list[str]] = None) -> int:
    # Load env early
    load_dotenv()

    parser = build_argparser()
    ns = parser.parse_args(argv)

    logger = setup_logger("shroud")
    try:
        # Adjust log level if provided
        level_name = str(ns.log_level).upper()
        logger.setLevel(getattr(type(logger), "level", getattr(logger, "level", 20)))
        for h in getattr(logger, "handlers", []):
            h.setLevel(getattr(__import__("logging"), level_name, 20))
    except Exception:
        pass  # harmless if custom logger handles levels differently

    cfg = make_config(ns)

    logger.info("Shroud starting | mode=%s | dry_run=%s | once=%s | metrics=%s",
                cfg.mode, cfg.dry_run, cfg.once, cfg.metrics_path)

    if cfg.mode == "ping":
        logger.info("pong")
        return 0

    if cfg.mode == "test":
        # Minimal self-check
        try:
            _ = parse_duration("5m")
            logger.info("parse_duration OK")
        except Exception as e:
            logger.error("parse_duration failed: %s", e)
            return 2
        logger.info("test mode complete")
        return 0

    # mode == "run"
    run_loop(cfg, logger)
    logger.info("Shroud finished")
    return 0
