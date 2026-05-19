import ctypes
import ctypes.wintypes as w
import threading
import time

BLUETOOTH_MAX_NAME_SIZE = 248


class _SYSTEMTIME(ctypes.Structure):
    _fields_ = [
        ("wYear", w.WORD), ("wMonth", w.WORD), ("wDayOfWeek", w.WORD),
        ("wDay", w.WORD), ("wHour", w.WORD), ("wMinute", w.WORD),
        ("wSecond", w.WORD), ("wMilliseconds", w.WORD),
    ]


class BLUETOOTH_DEVICE_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize",          w.DWORD),
        ("Address",         ctypes.c_ulonglong),
        ("ulClassofDevice", ctypes.c_ulong),
        ("fConnected",      w.BOOL),
        ("fRemembered",     w.BOOL),
        ("fAuthenticated",  w.BOOL),
        ("stLastSeen",      _SYSTEMTIME),
        ("stLastUsed",      _SYSTEMTIME),
        ("szName",          ctypes.c_wchar * BLUETOOTH_MAX_NAME_SIZE),
    ]

    def __init__(self):
        super().__init__()
        self.dwSize = ctypes.sizeof(BLUETOOTH_DEVICE_INFO)


class BLUETOOTH_DEVICE_SEARCH_PARAMS(ctypes.Structure):
    _fields_ = [
        ("dwSize",               w.DWORD),
        ("fReturnAuthenticated", w.BOOL),
        ("fReturnRemembered",    w.BOOL),
        ("fReturnUnknown",       w.BOOL),
        ("fReturnConnected",     w.BOOL),
        ("fIssueInquiry",        w.BOOL),
        ("cTimeoutMultiplier",   ctypes.c_ubyte),
        ("hRadio",               w.HANDLE),
    ]

    def __init__(self):
        super().__init__()
        self.dwSize               = ctypes.sizeof(BLUETOOTH_DEVICE_SEARCH_PARAMS)
        self.fReturnAuthenticated = False
        self.fReturnRemembered    = False
        self.fReturnUnknown       = False
        self.fReturnConnected     = True
        self.fIssueInquiry        = False
        self.cTimeoutMultiplier   = 1
        self.hRadio               = None


_HBLUETOOTH = ctypes.c_void_p
try:
    _btdll = ctypes.WinDLL("BluetoothAPIs.dll")
    _btdll.BluetoothFindFirstDevice.restype  = _HBLUETOOTH
    _btdll.BluetoothFindFirstDevice.argtypes = [
        ctypes.POINTER(BLUETOOTH_DEVICE_SEARCH_PARAMS),
        ctypes.POINTER(BLUETOOTH_DEVICE_INFO),
    ]
    _btdll.BluetoothFindNextDevice.restype   = w.BOOL
    _btdll.BluetoothFindNextDevice.argtypes  = [_HBLUETOOTH, ctypes.POINTER(BLUETOOTH_DEVICE_INFO)]
    _btdll.BluetoothFindDeviceClose.restype  = w.BOOL
    _btdll.BluetoothFindDeviceClose.argtypes = [_HBLUETOOTH]
    _BT_AVAILABLE = True
except OSError:
    _BT_AVAILABLE = False


def _iter_connected(callback):
    """Call callback(name) for every currently-connected BT device. Handles open/close."""
    if not _BT_AVAILABLE:
        return
    params = BLUETOOTH_DEVICE_SEARCH_PARAMS()
    info   = BLUETOOTH_DEVICE_INFO()
    handle = _btdll.BluetoothFindFirstDevice(ctypes.byref(params), ctypes.byref(info))
    if not handle:
        return
    try:
        while True:
            callback(info.szName)
            info = BLUETOOTH_DEVICE_INFO()
            if not _btdll.BluetoothFindNextDevice(handle, ctypes.byref(info)):
                break
    finally:
        _btdll.BluetoothFindDeviceClose(handle)


def list_connected_bt_devices() -> list[str]:
    """Return names of all currently connected Bluetooth devices."""
    names: list[str] = []
    _iter_connected(lambda n: names.append(n) if n else None)
    return names


def _bt_device_connected(name_substr: str) -> bool:
    needle = name_substr.lower()
    found  = [False]

    def check(name):
        if not found[0] and needle in name.lower():
            found[0] = True

    _iter_connected(check)
    return found[0]


POLL_INTERVAL = 5  # seconds


class BluetoothMonitor:
    def __init__(self, device_substr: str = "", poll_interval: int = POLL_INTERVAL):
        self._device_substr = device_substr
        self.poll_interval  = poll_interval
        self.on_connect     = None
        self.on_disconnect  = None
        self._connected     = None
        self._lock          = threading.Lock()
        self._running       = False

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True, name="BTMonitor").start()

    def stop(self):
        self._running = False

    def set_device(self, new_substr: str):
        with self._lock:
            self._device_substr = new_substr
            self._connected     = None  # force re-detection on next poll

    @property
    def is_connected(self) -> bool:
        with self._lock:
            return bool(self._connected)

    def _loop(self):
        while self._running:
            # Read device name under lock, then poll BT (slow call) without lock
            with self._lock:
                substr = self._device_substr

            connected = _bt_device_connected(substr) if substr else False

            fire_connect = fire_disconnect = False
            with self._lock:
                # Only apply result if device name hasn't changed while we were polling
                if self._device_substr == substr:
                    if self._connected is None:
                        self._connected  = connected
                        fire_connect     = connected
                    elif connected != self._connected:
                        self._connected  = connected
                        fire_connect     = connected
                        fire_disconnect  = not connected

            if fire_connect and self.on_connect:
                self.on_connect()
            elif fire_disconnect and self.on_disconnect:
                self.on_disconnect()

            time.sleep(self.poll_interval)
