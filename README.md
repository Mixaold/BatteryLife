<div align="center">

# 🎧 BatteryLife

[![Download](https://img.shields.io/github/v/release/Mixaold/BatteryLife?label=Download%20.exe&style=for-the-badge&color=22c55e)](https://github.com/Mixaold/BatteryLife/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078d4?style=for-the-badge&logo=windows)](https://github.com/Mixaold/BatteryLife)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## 🇷🇺 Русский

### Зачем это

Купил я значит б/у наушники от Sony, сказали что были в использовании немного, но мне хотелось узнать точную цифру: сколько часов они реально работают от полного заряда, и сравнить это с 30 часами, которые заявляет Sony для новых?

Готового инструмента для этого не нашлось и поэтому я написал свой XDDD, да это ну мега конечно тупо, но мне было настолько нечего делать...

BatteryLife живёт в трее и тихо делает своё дело. Подключил наушники — пошёл таймер. Отключил на зарядку — сессия записалась. Через пару циклов видишь реальные числа: держат 24 часа? Или уже еле-еле 15? Без гаданий.

Работает с любым Bluetooth-устройством у которого Windows видит заряд — наушники, колонки, геймпады, True Wireless и т.д.

---

### Скачать

1. Открой [**Releases**](https://github.com/Mixaold/BatteryLife/releases/latest)
2. Скачай **`BatteryLife.exe`**
3. Запусти — всё

Никакого Python, никакой установки. Один файл `.exe` и готово.

> **Первый запуск:** выскочит окно настройки. Жми **"Найти устройства"** — покажет что сейчас подключено по Bluetooth. Выбирай своё и жми **Выбрать**.

---

### Как пользоваться

После настройки прячется в трей (правый нижний угол, рядом с часами).

| Действие | Что будет |
|---|---|
| **Двойной клик** по иконке | Окно со статистикой |
| **Правый клик** по иконке | Меню |

В окне статистики видно:
- сколько часов наушники проработали в этом цикле заряда
- текущий процент батареи
- прогресс-бар по сессиям
- номер цикла и количество сессий

Через меню можно:
- **Новый цикл заряда** — нажимаешь когда зарядил до 100% и хочешь начать новый отсчёт
- **История циклов** — смотришь как менялась батарея со временем
- **Автозапуск** — включить чтобы не запускать руками каждый раз
- Сменить устройство, язык, выйти

---

### Где лежат данные

В `%APPDATA%\BatteryLife\`, то есть примерно `C:\Users\ИмяПользователя\AppData\Roaming\BatteryLife\`.

- перетащи `.exe` куда угодно — данные не потеряются
- обнови приложение — данные останутся
- никуда не отправляется, всё локально

---

### Технически

- Каждые 5 секунд проверяет подключение через Windows Bluetooth API — без лишних процессов
- Заряд берёт из хранилища свойств устройства Windows, тот же источник что и "Параметры"
- Иконка в трее анимируется когда подключено и меняет цвет: 🟢 ≥60%, 🟡 30–59%, 🔴 <30%
- Данные в JSON — можно открыть блокнотом и посмотреть

---

### Запустить из исходников

> Это только если хочешь покопаться в коде. Обычному пользователю Python не нужен — скачай `.exe` из Releases и всё.

```
git clone https://github.com/Mixaold/BatteryLife
cd BatteryLife
pip install -r requirements.txt
pythonw main.py
```

Нужен Python 3.10+, Windows 10/11

Собрать `.exe` самому:
```
build.bat
```

---

---

## 🇺🇸 English

### What's this

So I bought some used Sony WH-1000XM4s. Guy said the battery was still good. But I wanted the actual number — how many hours do they really last on a full charge vs the 30 hours Sony claims for new ones?

Couldn't find any tool that just does that, so I made one.

BatteryLife sits in your system tray and tracks silently. Connect your headphones — timer starts. Disconnect to charge — session saved. After a couple cycles you've got real data: still at 24 hours or down to 15? No guessing.

Works with any Bluetooth device Windows can see the battery for — headphones, earbuds, speakers, controllers, whatever.

---

### Download

1. Go to [**Releases**](https://github.com/Mixaold/BatteryLife/releases/latest)
2. Grab **`BatteryLife.exe`**
3. Run it

No Python, no setup, no installer. Just a single `.exe`.

> **First run:** a setup window pops up. Click **"Detect devices"** to see what's connected via Bluetooth right now, pick your device, hit **Select**.

---

### How to use it

After setup it hides in the **system tray** (bottom-right corner, near the clock).

| Action | What it does |
|---|---|
| **Double-click** the icon | Opens the stats window |
| **Right-click** the icon | Opens the menu |

The stats window shows:
- total connected time this charge cycle
- current battery %
- a bar showing battery across sessions
- cycle number and session count

From the menu:
- **New charge cycle** — hit this after charging to 100% to start fresh
- **Cycle history** — see how your battery has changed over time
- **Autostart** — launch with Windows so you never miss a session
- Change device, switch language, exit

---

### Where's the data

Saved to `%APPDATA%\BatteryLife\` — something like `C:\Users\YourName\AppData\Roaming\BatteryLife\`.

- move the `.exe` anywhere, data stays
- update the app, data stays
- nothing gets sent anywhere, it's all local

---

### Tech stuff

- Polls Bluetooth connection every 5 seconds via Windows Bluetooth API — no background junk
- Battery level from the Windows device property store, same place Settings reads it from
- Tray icon glows when connected, color-coded: 🟢 ≥60%, 🟡 30–59%, 🔴 <30%
- Data's in JSON files — open in Notepad if you're curious

---

### Run from source

> Only if you want to dig into the code. Regular users don't need Python — just grab the `.exe` from Releases.

```
git clone https://github.com/Mixaold/BatteryLife
cd BatteryLife
pip install -r requirements.txt
pythonw main.py
```

Requires Python 3.10+, Windows 10/11

Build the exe yourself:
```
build.bat
```

---

## License

MIT
