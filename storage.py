import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def _root() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


_BASE_DIR     = _root() / "data"
_DEFAULT_FILE = _BASE_DIR / "sessions.json"   # legacy path
DATA_FILE     = _DEFAULT_FILE


def safe_name(name: str) -> str:
    s = "".join(c if c.isalnum() or c in "-_. " else "_" for c in name).strip()
    return s[:64] or "default"


# Keep private alias for internal backwards compat
_safe_name = safe_name


def set_device(name: str) -> None:
    """Switch active data file to the per-device path. Migrates legacy file only once."""
    global DATA_FILE
    if not name:
        DATA_FILE = _DEFAULT_FILE
        return
    device_file   = _BASE_DIR / safe_name(name) / "sessions.json"
    migrated_flag = _BASE_DIR / ".migrated"
    if not device_file.exists():
        device_file.parent.mkdir(parents=True, exist_ok=True)
        if _DEFAULT_FILE.exists() and not migrated_flag.exists():
            shutil.copy2(_DEFAULT_FILE, device_file)
            migrated_flag.touch()
    DATA_FILE = device_file


def list_known_devices() -> list[str]:
    """Return safe folder names for every device that has stored session data."""
    result: list[str] = []
    if _BASE_DIR.exists():
        for d in _BASE_DIR.iterdir():
            if d.is_dir() and (d / "sessions.json").exists():
                result.append(d.name)
    return result


def _now_iso():
    return datetime.now().isoformat()


def fmt_seconds(seconds: int, h: str = "h", m: str = "m", s: str = "s") -> str:
    seconds = int(seconds)
    hv = seconds // 3600
    mv = (seconds % 3600) // 60
    sv = seconds % 60
    if hv > 0:
        return f"{hv}{h} {mv:02d}{m}"
    if mv > 0:
        return f"{mv}{m} {sv:02d}{s}"
    return f"{sv}{s}"


def _backup_corrupt() -> None:
    try:
        if DATA_FILE.exists():
            shutil.copy2(DATA_FILE, DATA_FILE.with_suffix(".bak"))
    except Exception:
        pass


def load():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        data = {"cycles": [], "active_cycle_id": None}
        _save(data)
        return data
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("corrupt data")
        data.setdefault("cycles", [])
        data.setdefault("active_cycle_id", None)
        if not isinstance(data["cycles"], list):
            data["cycles"] = []
            data["active_cycle_id"] = None
    except (json.JSONDecodeError, ValueError, OSError):
        _backup_corrupt()
        data = {"cycles": [], "active_cycle_id": None}
        _save(data)
    return data


def _save(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def active_cycle(data):
    cid = data.get("active_cycle_id")
    if cid is None:
        return None
    return next((c for c in data["cycles"] if c["id"] == cid), None)


def ensure_cycle(data):
    cycle = active_cycle(data)
    if cycle is None:
        cycle = new_cycle(data)
    return cycle


def new_cycle(data):
    current = active_cycle(data)
    if current:
        if current["sessions"] and current["sessions"][-1]["disconnected"] is None:
            current["sessions"][-1]["disconnected"] = _now_iso()
            _recalc(current)
        current["ended_at"] = _now_iso()

    new_id = max((c["id"] for c in data["cycles"]), default=0) + 1
    cycle = {
        "id":          new_id,
        "label":       f"Cycle {new_id}",
        "started_at":  _now_iso(),
        "ended_at":    None,
        "sessions":    [],
        "total_seconds": 0,
    }
    data["cycles"].append(cycle)
    data["active_cycle_id"] = new_id
    _save(data)
    return cycle


def start_session(data):
    cycle = ensure_cycle(data)
    if cycle["sessions"] and cycle["sessions"][-1]["disconnected"] is None:
        return
    cycle["sessions"].append({"connected": _now_iso(), "disconnected": None})
    _save(data)


def end_session(data):
    cycle = active_cycle(data)
    if not cycle:
        return
    if not cycle["sessions"] or cycle["sessions"][-1]["disconnected"] is not None:
        return
    cycle["sessions"][-1]["disconnected"] = _now_iso()
    _recalc(cycle)
    _save(data)


def _recalc(cycle):
    total = 0
    for s in cycle["sessions"]:
        if s["connected"] and s["disconnected"]:
            t0 = datetime.fromisoformat(s["connected"])
            t1 = datetime.fromisoformat(s["disconnected"])
            total += max(0, (t1 - t0).total_seconds())
    cycle["total_seconds"] = int(total)


def cycle_total_seconds(data, extra_seconds: float = 0) -> int:
    cycle = active_cycle(data)
    if not cycle:
        return 0
    return cycle["total_seconds"] + int(extra_seconds)


def grand_total_seconds(data, extra_seconds: float = 0) -> int:
    total = sum(c["total_seconds"] for c in data.get("cycles", []))
    return total + int(extra_seconds)


def reset_all(data):
    data["cycles"] = []
    data["active_cycle_id"] = None
    _save(data)
    return new_cycle(data)


def log_battery(data, level: int):
    log = data.setdefault("battery_log", [])
    if log and log[-1]["level"] // 10 == level // 10:
        return
    log.append({"time": _now_iso(), "level": level})
    if len(log) > 500:
        data["battery_log"] = log[-500:]
    _save(data)


def get_battery_log(data, n: int = 15) -> list:
    return data.get("battery_log", [])[-n:]


def cycle_summary(cycle) -> str:
    completed = [s for s in cycle["sessions"] if s["disconnected"] is not None]
    return f"{cycle['label']}: {fmt_seconds(cycle['total_seconds'])} ({len(completed)} sessions)"
