<div align="center">

# 🎧 BatteryLife

**Track the real battery life of your Bluetooth headphones on Windows**

[![Download](https://img.shields.io/github/v/release/Mixaold/BatteryLife?label=Download%20.exe&style=for-the-badge&color=22c55e)](https://github.com/Mixaold/BatteryLife/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078d4?style=for-the-badge&logo=windows)](https://github.com/Mixaold/BatteryLife)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## 🇬🇧 English

### The story behind this app

I bought a pair of used Sony WH-1000XM4 headphones. The seller said the battery was fine — "holds a charge well." But I wanted to know the *real* number: how many hours do they actually last on a full charge, compared to the 30 hours Sony advertises for a new pair?

There was no ready-made tool for this. So I built one.

**BatteryLife** sits quietly in your system tray. Every time you connect your headphones to your PC, it starts a timer. When you disconnect (to charge), it stops and saves the session. After several charge cycles you get a clear picture: your headphones last 24 hours? 18? 12? No guesswork — just measured data from your own usage.

This works for **any Bluetooth device**: headphones, earbuds, speakers, game controllers — anything that connects via Bluetooth and has a battery level visible to Windows.

---

### Download & Run (no install needed)

1. Go to [**Releases**](https://github.com/Mixaold/BatteryLife/releases/latest)
2. Download **`BatteryLife.exe`**
3. Double-click it — that's it

No Python, no dependencies, no installer. Just one `.exe` file.

> **First launch:** A setup window will appear. Click **"Detect devices"** — the app will show all Bluetooth devices currently connected to your PC. Click on yours and press **Select**.

---

### How to use

After setup, the app hides in the **system tray** (bottom-right corner, near the clock).

| Action | What happens |
|---|---|
| **Double-click** tray icon | Open the stats window |
| **Right-click** tray icon | Open the menu |

**The stats window shows:**
- ⏱ Total connected time in the current charge cycle
- 🔋 Current battery level (%)
- 📊 A progress bar showing battery level over the last sessions
- Cycle number and session count

**The tray menu lets you:**
- Start a **new charge cycle** — do this after you fully charge your device
- View **cycle history** — compare previous cycles
- Enable **autostart with Windows** — so tracking never misses a session
- Change device, switch language (RU/EN), exit

**Typical workflow:**
1. Charge your headphones to 100%
2. Connect them to your PC
3. Use them as normal — BatteryLife tracks time automatically
4. When the battery dies (or you're done), disconnect and plug in to charge
5. Right-click tray → **New charge cycle**
6. Repeat 2–3 cycles — then you know the real battery life

---

### Where is my data stored?

All data is saved in `%APPDATA%\BatteryLife\` (that's `C:\Users\YourName\AppData\Roaming\BatteryLife\`).

This means:
- Moving or deleting the `.exe` **does not** lose your data
- Data survives app updates
- Nothing is sent anywhere — everything stays on your PC

---

### How it works (technical)

- Checks Bluetooth connection status every **5 seconds** using the Windows Bluetooth API (`BluetoothAPIs.dll`) — no background processes, no WMI polling
- Reads battery level from the **Windows device property store** (`CfgMgr32.dll`) — the same source Windows Settings uses
- Icon in the tray **animates** (breathing glow) when device is connected, and changes color based on battery level: 🟢 green (≥60%), 🟡 yellow (30–59%), 🔴 red (<30%)
- All session data is stored in JSON files — human-readable, easy to back up

---

### Run from source

```
git clone https://github.com/Mixaold/BatteryLife
cd BatteryLife
pip install -r requirements.txt
pythonw main.py
```

**Requirements:** Python 3.10+, Windows 10/11

**Build exe yourself:**
```
build.bat
```

---

---

## 🇷🇺 Русский

### Зачем это приложение

Я купил б/у наушники Sony WH-1000XM4. Продавец говорил, что батарея "держит нормально". Но мне хотелось знать точную цифру: сколько часов они реально работают от полного заряда, и сравнить это с 30 часами, которые заявляет Sony для новых?

Готового инструмента для этого не нашлось. Поэтому я написал свой.

**BatteryLife** тихо работает в трее. Каждый раз, когда ты подключаешь наушники к ПК по Bluetooth — стартует таймер. Когда отключаешь (на зарядку) — таймер останавливается и сессия сохраняется. Через несколько циклов заряда у тебя есть точная картина: твои наушники держат 24 часа? 18? 12? Никакого угадывания — только реальные данные от твоего использования.

Работает с **любым Bluetooth-устройством**: наушники, колонки, геймпады, True Wireless — всё что подключается по Bluetooth и имеет уровень заряда, видимый Windows.

---

### Скачать и запустить (установка не нужна)

1. Перейди в [**Releases**](https://github.com/Mixaold/BatteryLife/releases/latest)
2. Скачай **`BatteryLife.exe`**
3. Запусти двойным кликом — всё

Никакого Python, никаких зависимостей, никакого установщика. Просто один файл `.exe`.

> **Первый запуск:** появится окно настройки. Нажми **"Найти устройства"** — приложение покажет все Bluetooth-устройства, подключённые к ПК прямо сейчас. Кликни на своё и нажми **Выбрать**.

---

### Как пользоваться

После настройки приложение скрывается в **системный трей** (правый нижний угол, рядом с часами).

| Действие | Что происходит |
|---|---|
| **Двойной клик** по иконке в трее | Открыть окно статистики |
| **Правый клик** по иконке в трее | Открыть меню |

**В окне статистики:**
- ⏱ Суммарное время подключения в текущем цикле заряда
- 🔋 Текущий уровень заряда (%)
- 📊 Прогресс-бар с историей заряда по сессиям
- Номер цикла и количество сессий

**Через меню трея:**
- **Новый цикл заряда** — нажать после того как полностью зарядил устройство
- **История циклов** — сравнить прошлые циклы между собой
- **Автозапуск с Windows** — чтобы приложение всегда стартовало вместе с ПК
- Сменить устройство, переключить язык (RU/EN), выйти

**Типичный сценарий:**
1. Зарядил наушники до 100%
2. Подключил к ПК
3. Пользуешься как обычно — BatteryLife считает время автоматически
4. Когда батарея садится (или хочешь зарядить), отключаешь и ставишь на зарядку
5. Правый клик по трею → **Новый цикл заряда**
6. Повторить 2–3 цикла — и ты знаешь реальный ресурс батареи

---

### Где хранятся данные?

Все данные сохраняются в `%APPDATA%\BatteryLife\` (то есть `C:\Users\ИмяПользователя\AppData\Roaming\BatteryLife\`).

Это значит:
- Перемещение или удаление `.exe` **не удаляет** данные
- Данные сохраняются при обновлении приложения
- Никуда не отправляется — всё остаётся на твоём ПК

---

### Как это работает (технически)

- Каждые **5 секунд** проверяет статус Bluetooth-подключения через Windows Bluetooth API (`BluetoothAPIs.dll`) — никаких фоновых процессов, никакого WMI
- Уровень заряда читается из хранилища свойств устройства Windows (`CfgMgr32.dll`) — тот же источник, что использует "Параметры Windows"
- Иконка в трее **анимируется** (плавное свечение) когда устройство подключено, и меняет цвет в зависимости от заряда: 🟢 зелёный (≥60%), 🟡 жёлтый (30–59%), 🔴 красный (<30%)
- Все данные хранятся в JSON-файлах — читаемый текст, легко сделать резервную копию

---

### Запуск из исходников

```
git clone https://github.com/Mixaold/BatteryLife
cd BatteryLife
pip install -r requirements.txt
pythonw main.py
```

**Требования:** Python 3.10+, Windows 10/11

**Собрать exe самому:**
```
build.bat
```

---

## License / Лицензия

MIT — используй свободно, в том числе в коммерческих проектах.
