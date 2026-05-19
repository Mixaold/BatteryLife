# BatteryLife

Track real battery life of any Bluetooth headphones (or any Bluetooth device) on Windows.

BatteryLife runs silently in the system tray, detects when your device connects and disconnects via Bluetooth, and accumulates the total connected time per charge cycle. At the end of a charge you get the real, measured battery life for your specific device.

![screenshot placeholder](docs/screenshot.png)

---

## Features

- **Any Bluetooth device** — headphones, speakers, earbuds, etc.
- **System tray icon** with animated battery ring (color-coded by charge level)
- **Popup stats window** — total time, current session, battery %, charge cycle info
- **Battery level history** — logs every % change with timestamps and deltas
- **Charge cycles** — start a new cycle after each full charge; compare cycles over time
- **Autostart with Windows** — toggle from the tray menu
- **RU / EN UI** — auto-detected from system locale, switchable in-app

---

## Requirements

- Windows 10 / 11
- Python 3.10+
- Bluetooth adapter

---

## Installation

```
git clone https://github.com/your-username/BatteryLife
cd BatteryLife
pip install -r requirements.txt
```

---

## Running

```
pythonw main.py
```

On first launch a setup wizard appears — enter the name (or part of the name) of your Bluetooth device (e.g. `WH-1000XM4`, `QuietComfort`, `H9`). Click **Detect** to auto-scan connected devices.

To start automatically with Windows, right-click the tray icon → **Autostart: OFF** to enable it.

---

## Usage

| Action | Result |
|---|---|
| Left-click / double-click tray icon | Open stats window |
| Right-click tray icon | Context menu |
| **New charge cycle** | Close current cycle, start fresh (do this after fully charging) |
| **Reset all data** | Wipe all cycles and sessions |
| **Change device** | Re-run device setup |
| **Autostart** | Toggle Windows startup entry |
| **Language** | Switch RU ↔ EN |

---

## How it works

- Polls the **Windows Bluetooth API** (`BluetoothAPIs.dll`) every 5 seconds to detect connect / disconnect events — no WMI, no subprocess
- Battery level is read from the **Windows device property store** via `CfgMgr32.dll` in-process — no console windows ever appear
- All data is stored locally in `data/sessions.json`

**Note:** Only counts time the device is connected to *this PC*. If you also use your headphones with a phone or another computer, that time isn't tracked.

---

## Data

Sessions and cycles are stored in `data/sessions.json`. This file is excluded from git (see `.gitignore`) so your personal usage data is never committed.

---

## Русский

**Установка:** `pip install -r requirements.txt`, затем `pythonw main.py`.

При первом запуске появится мастер настройки — введи название своего Bluetooth-устройства. Язык определяется автоматически по системным настройкам. Переключить язык можно через меню в трее или кнопкой в окне статистики.

---

## License

MIT
