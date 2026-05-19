"""
Read Bluetooth device battery level using CfgMgr32.dll + WMI.
No subprocess — fully in-process, no console windows.
"""
import ctypes
import ctypes.wintypes as w
import threading
import uuid

import pythoncom
import wmi

_UPDATE_INTERVAL = 60  # seconds


class _GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_uint8 * 8),
    ]


class _DEVPROPKEY(ctypes.Structure):
    _fields_ = [("fmtid", _GUID), ("pid", ctypes.c_uint32)]


def _make_key(guid_str: str, pid: int) -> _DEVPROPKEY:
    u = uuid.UUID(guid_str)
    key = _DEVPROPKEY()
    key.fmtid.Data1 = u.time_low
    key.fmtid.Data2 = u.time_mid
    key.fmtid.Data3 = u.time_hi_version
    key.fmtid.Data4 = (ctypes.c_uint8 * 8)(*u.bytes[8:])
    key.pid = pid
    return key


_BATTERY_KEY = _make_key("{104EA319-6EE2-4701-BD47-8DDBF425BBE5}", 2)

try:
    _cm = ctypes.WinDLL("CfgMgr32.dll")
    _cm.CM_Locate_DevNodeW.restype  = ctypes.c_ulong
    _cm.CM_Locate_DevNodeW.argtypes = [
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_wchar_p,
        ctypes.c_ulong,
    ]
    _cm.CM_Get_DevNode_PropertyW.restype  = ctypes.c_ulong
    _cm.CM_Get_DevNode_PropertyW.argtypes = [
        ctypes.c_ulong,
        ctypes.POINTER(_DEVPROPKEY),
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_ulong,
    ]
    _CM_OK = True
except OSError:
    _CM_OK = False


def _battery_from_device_id(device_id: str) -> int | None:
    if not _CM_OK:
        return None
    devinst   = ctypes.c_ulong(0)
    prop_type = ctypes.c_ulong(0)
    buf       = (ctypes.c_ubyte * 4)()
    buf_size  = ctypes.c_ulong(4)
    if _cm.CM_Locate_DevNodeW(ctypes.byref(devinst), device_id, 0) != 0:
        return None
    if _cm.CM_Get_DevNode_PropertyW(
        devinst,
        ctypes.byref(_BATTERY_KEY),
        ctypes.byref(prop_type),
        ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)),
        ctypes.byref(buf_size),
        0,
    ) != 0:
        return None
    val = buf[0]
    return val if 0 < val <= 100 else None


def _read_now(name_substr: str) -> int | None:
    if not name_substr:
        return None
    # Escape WQL string literal to prevent injection via crafted device names
    safe_substr = name_substr.replace("'", "''")
    pythoncom.CoInitialize()
    try:
        c    = wmi.WMI()
        devs = c.query(
            f"SELECT DeviceID FROM Win32_PnPEntity "
            f"WHERE Name LIKE '%{safe_substr}%'"
        )
        for dev in devs:
            val = _battery_from_device_id(dev.DeviceID)
            if val is not None:
                return val
        return None
    except Exception:
        return None
    finally:
        pythoncom.CoUninitialize()


class BatteryMonitor:
    def __init__(self, name_substr: str = "", interval: int = _UPDATE_INTERVAL):
        self._name     = name_substr
        self._interval = interval
        self._level: int | None = None
        self._lock     = threading.Lock()
        self._stop     = threading.Event()
        self.on_change = None  # callback(new_level: int)

    def start(self):
        threading.Thread(target=self._loop, daemon=True, name="BatteryMonitor").start()

    def stop(self):
        self._stop.set()

    def set_device(self, new_substr: str):
        with self._lock:
            self._name  = new_substr
            self._level = None  # reset cached level

    @property
    def level(self) -> int | None:
        with self._lock:
            return self._level

    def _fetch(self):
        with self._lock:
            name = self._name
        val = _read_now(name)
        with self._lock:
            changed     = (val is not None) and (val != self._level)
            self._level = val
        if changed and self.on_change:
            self.on_change(val)

    def _loop(self):
        self._fetch()
        while not self._stop.wait(self._interval):
            self._fetch()
