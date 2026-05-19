import sys
import winreg
from pathlib import Path

_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "BatteryLife"
_OLD_NAME = "WH1000XM4Tracker"  # previous name — migrated on first call


def _command() -> str:
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle — point directly to the exe
        return f'"{Path(sys.executable)}"'
    pythonw = Path(sys.executable).parent / "pythonw.exe"
    main    = Path(__file__).parent / "main.py"
    return f'"{pythonw}" "{main}"'


def _migrate_old_key():
    """One-time migration: rename old registry entry if it exists."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY_PATH, 0,
                            winreg.KEY_READ | winreg.KEY_SET_VALUE) as k:
            try:
                winreg.QueryValueEx(k, _OLD_NAME)
                winreg.SetValueEx(k, _APP_NAME, 0, winreg.REG_SZ, _command())
                winreg.DeleteValue(k, _OLD_NAME)
            except FileNotFoundError:
                pass
    except Exception:
        pass


_migrate_old_key()


def enable():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY_PATH, 0,
                        winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, _APP_NAME, 0, winreg.REG_SZ, _command())


def disable():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY_PATH, 0,
                            winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, _APP_NAME)
    except FileNotFoundError:
        pass


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY_PATH) as k:
            winreg.QueryValueEx(k, _APP_NAME)
        return True
    except FileNotFoundError:
        return False
