import json
import sys
from pathlib import Path


def _root() -> Path:
    # When packaged with PyInstaller --onefile, store data next to the exe
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


_PATH = _root() / "data" / "config.json"

DEFAULTS: dict = {
    "device_name":      "",
    "poll_interval":    5,
    "battery_interval": 60,
    "language":         "auto",
}


def load() -> dict:
    _PATH.parent.mkdir(exist_ok=True)
    if not _PATH.exists():
        cfg = DEFAULTS.copy()
        _save(cfg)
        return cfg
    try:
        with open(_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        if not isinstance(cfg, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError, OSError):
        cfg = {}
    for k, v in DEFAULTS.items():
        cfg.setdefault(k, v)
    # Clamp numeric fields to sane ranges
    if not isinstance(cfg["poll_interval"], int) or cfg["poll_interval"] < 1:
        cfg["poll_interval"] = DEFAULTS["poll_interval"]
    if not isinstance(cfg["battery_interval"], int) or cfg["battery_interval"] < 10:
        cfg["battery_interval"] = DEFAULTS["battery_interval"]
    if cfg["language"] not in ("ru", "en", "auto"):
        cfg["language"] = DEFAULTS["language"]
    if not isinstance(cfg["device_name"], str):
        cfg["device_name"] = ""
    return cfg


def save(cfg: dict) -> None:
    _PATH.parent.mkdir(exist_ok=True)
    with open(_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


_save = save
