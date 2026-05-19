import locale

_STRINGS: dict[str, dict[str, str]] = {
    "ru": {
        "connected":              "● подключено",
        "disconnected":           "○ не подключено",
        "offline":                "не в сети",
        "session":                "сессия",
        "no_cycle":               "нет активного цикла",
        "sessions_count":         "сессий",
        "cycle":                  "Цикл",
        "no_battery":             "—",
        "battery_history":        "история заряда",
        "no_history_data":        "(пока нет данных — ожидаем первого замера)",
        "show_timer":             "Показать таймер",
        "new_cycle":              "Новый цикл заряда",
        "reset_all":              "Сбросить всю историю",
        "autostart_on":           "Автозапуск: ВКЛ",
        "autostart_off":          "Автозапуск: ВЫКЛ",
        "change_device":          "Сменить устройство",
        "cycle_history":          "История циклов",
        "no_history":             "Нет истории",
        "exit":                   "Выход",
        "lang_toggle":            "Язык: RU → EN",
        "h":                      "ч",
        "m":                      "м",
        "s":                      "с",
        "notif_started":          "Таймер запущен",
        "notif_stopped":          "Итого в цикле",
        "device_connected":       "подключено",
        "device_disconnected":    "отключено",
        "welcome_desc":           "Отслеживает реальное время работы\nBluetooth-устройств от батареи.",
        "welcome_btn":            "Понял!",
        "setup_header":           "Найти устройство",
        "setup_hint":             "Выбери своё Bluetooth-устройство из списка\nили подключи его и нажми «Определить»",
        "setup_detect":           "Определить",
        "setup_start":            "Начать →",
        "setup_cancel":           "Отмена",
        "setup_no_devices":       "(нет подключённых устройств)",
        "setup_devices_label":    "Подключённые устройства:",
        "confirm_nc_title":       "BatteryLife",
        "confirm_nc_msg":         "Начать новый цикл заряда?\n\nТекущий цикл будет завершён.\nИспользуй это после полной зарядки.",
        "confirm_reset_title":    "BatteryLife",
        "confirm_reset_msg":      "Сбросить ВСЮ историю?\n\nВсе циклы и сессии будут удалены безвозвратно.",
    },
    "en": {
        "connected":              "● connected",
        "disconnected":           "○ disconnected",
        "offline":                "offline",
        "session":                "session",
        "no_cycle":               "no active cycle",
        "sessions_count":         "sessions",
        "cycle":                  "Cycle",
        "no_battery":             "—",
        "battery_history":        "battery history",
        "no_history_data":        "(no data yet — waiting for first reading)",
        "show_timer":             "Show timer",
        "new_cycle":              "New charge cycle",
        "reset_all":              "Reset all data",
        "autostart_on":           "Autostart: ON",
        "autostart_off":          "Autostart: OFF",
        "change_device":          "Change device",
        "cycle_history":          "Charge cycles",
        "no_history":             "No history",
        "exit":                   "Exit",
        "lang_toggle":            "Language: EN → RU",
        "h":                      "h",
        "m":                      "m",
        "s":                      "s",
        "notif_started":          "Timer started",
        "notif_stopped":          "Total this cycle",
        "device_connected":       "connected",
        "device_disconnected":    "disconnected",
        "welcome_desc":           "Tracks real battery life of your\nBluetooth headphones.",
        "welcome_btn":            "Got it!",
        "setup_header":           "Find your device",
        "setup_hint":             "Enter your Bluetooth device name (or part of it):",
        "setup_detect":           "Detect",
        "setup_start":            "Start →",
        "setup_cancel":           "Cancel",
        "setup_no_devices":       "(no connected devices found)",
        "setup_devices_label":    "Connected devices:",
        "confirm_nc_title":       "BatteryLife",
        "confirm_nc_msg":         "Start a new charge cycle?\n\nCurrent cycle will be closed.\nUse this after fully charging your device.",
        "confirm_reset_title":    "BatteryLife",
        "confirm_reset_msg":      "Reset ALL history?\n\nAll cycles and sessions will be permanently deleted.",
    },
}

_current = "ru"


def detect_system_lang() -> str:
    try:
        code = locale.getdefaultlocale()[0] or ""
        return "ru" if code.lower().startswith("ru") else "en"
    except Exception:
        return "en"


def set_lang(lang: str) -> None:
    global _current
    if lang in _STRINGS:
        _current = lang


def get_lang() -> str:
    return _current


def t(key: str) -> str:
    return _STRINGS.get(_current, _STRINGS["en"]).get(key, key)


def fmt_time(seconds: int) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    th, tm, ts = t("h"), t("m"), t("s")
    if h > 0:
        return f"{h}{th} {m:02d}{tm}"
    if m > 0:
        return f"{m}{tm} {s:02d}{ts}"
    return f"{s}{ts}"
