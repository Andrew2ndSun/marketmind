"""Durable two-hour radar schedule for the single-process demo server."""
import copy
import json
import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .discovery import SCAN_INTERVAL_SECONDS

DATA_DIR = Path(__file__).resolve().parent.parent / ".cache" / "market-radar"
_lock = threading.Lock()
_state = {"running": False, "last_error": None, "last_attempt_at": None}
RETRY_SECONDS = 15 * 60


def utcnow():
    return datetime.now(timezone.utc)


def load_snapshot() -> dict | None:
    try:
        value = json.loads((DATA_DIR / "latest.json").read_text(encoding="utf-8"))
        from .discovery import MarketRadar, validate_radar
        payload = {key: value[key] for key in ("overview", "themes")}
        payload["stocks"] = [{k: v for k, v in stock.items() if k != "snapshot"} for stock in value["stocks"]]
        radar = MarketRadar.model_validate(payload)
        validate_radar(radar, [stock["snapshot"] for stock in value["stocks"]], value["evidence"])
        stamp = datetime.fromisoformat(value["created_at"])
        if stamp.tzinfo is None or stamp > utcnow() + timedelta(minutes=10):
            return None
        return value
    except (OSError, ValueError, KeyError, TypeError):
        return None


def read_snapshot() -> dict:
    snapshot = load_snapshot()
    if snapshot is None:
        return {"status": "pending", "stocks": [], "scan_interval_seconds": SCAN_INTERVAL_SECONDS,
                **copy.deepcopy(_state),
                "message": "The scheduled background scan is preparing the first list. You can research any ticker below."}
    age = max(0, int((utcnow() - datetime.fromisoformat(snapshot["created_at"])).total_seconds()))
    return {**snapshot, "status": "ready", "cached": True, "cache_age_seconds": age,
            "stale": age >= SCAN_INTERVAL_SECONDS,
            "next_scan_at": (datetime.fromisoformat(snapshot["created_at"]) + timedelta(seconds=SCAN_INTERVAL_SECONDS)).isoformat(),
            **copy.deepcopy(_state)}


def update_if_due() -> bool:
    """Publish atomically after validation. Retain the last good list on any failure."""
    if not _lock.acquire(blocking=False):
        return False
    try:
        snapshot = load_snapshot()
        if snapshot and (utcnow() - datetime.fromisoformat(snapshot["created_at"])).total_seconds() < SCAN_INTERVAL_SECONDS:
            return False
        if _state["last_attempt_at"] and (utcnow() - datetime.fromisoformat(_state["last_attempt_at"])).total_seconds() < RETRY_SECONDS:
            return False
        _state.update(running=True, last_attempt_at=utcnow().isoformat())
        from .discovery import build_scan
        result = build_scan()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temporary = DATA_DIR / "latest.tmp"
        temporary.write_text(json.dumps(result, ensure_ascii=True, allow_nan=False), encoding="utf-8")
        os.replace(temporary, DATA_DIR / "latest.json")
        _state["last_error"] = None
        return True
    except Exception:
        # Keep provider response bodies, credentials and untrusted error strings out of API/logs.
        _state["last_error"] = "The scheduled scan failed. The last successful list is retained; retry in 15 minutes."
        logging.getLogger(__name__).warning("Scheduled market scan failed; retaining previous snapshot.")
        return False
    finally:
        _state["running"] = False
        _lock.release()


def start_scheduler():
    """Start at application startup, including when no visitors are connected."""
    stop = threading.Event()
    def run():
        while not stop.is_set():
            update_if_due()
            stop.wait(30)
    worker = threading.Thread(target=run, name="market-radar-scheduler", daemon=True)
    worker.start()
    return stop, worker
