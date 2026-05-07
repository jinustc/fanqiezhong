"""JSON file persistence for settings, tasks, and statistics."""

import json
import os
from datetime import date
from pathlib import Path
from typing import Any


def _data_dir() -> Path:
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    path = Path(appdata) / "pomodoro"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_json(filename: str, default: Any) -> Any:
    filepath = _data_dir() / filename
    if not filepath.exists():
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def _write_json(filename: str, data: Any):
    filepath = _data_dir() / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --- Settings ---

DEFAULT_SETTINGS = {
    "work_duration": 25,
    "short_break_duration": 5,
    "long_break_duration": 15,
    "sessions_before_long_break": 4,
    "always_on_top": False,
    "sound_enabled": True,
}


def load_settings() -> dict:
    stored = _read_json("settings.json", {})
    return {**DEFAULT_SETTINGS, **stored}


def save_settings(settings: dict):
    _write_json("settings.json", settings)


# --- Tasks ---

def load_tasks() -> list[dict]:
    return _read_json("tasks.json", [])


def save_tasks(tasks: list[dict]):
    _write_json("tasks.json", tasks)


# --- Statistics ---

def load_stats() -> dict:
    return _read_json("stats.json", {})


def save_stats(stats: dict):
    _write_json("stats.json", stats)


def record_work_session(duration_minutes: int):
    today = date.today().isoformat()
    stats = load_stats()

    if today not in stats:
        stats[today] = {"work_sessions": 0, "focus_minutes": 0}

    stats[today]["work_sessions"] += 1
    stats[today]["focus_minutes"] += duration_minutes

    save_stats(stats)


def get_today_stats() -> dict:
    today = date.today().isoformat()
    stats = load_stats()
    return stats.get(today, {"work_sessions": 0, "focus_minutes": 0})


def get_weekly_stats() -> dict:
    from datetime import timedelta

    today = date.today()
    stats = load_stats()

    weekly = {}
    for i in range(7):
        d = (today - timedelta(days=i)).isoformat()
        if d in stats:
            weekly[d] = stats[d]

    total_sessions = sum(v["work_sessions"] for v in weekly.values())
    total_minutes = sum(v["focus_minutes"] for v in weekly.values())

    return {
        "days": weekly,
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
    }
