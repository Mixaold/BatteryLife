import math
import queue
import threading
from datetime import datetime

import pystray
from PIL import Image, ImageDraw

import autostart
import i18n
import storage

_ANIM_FPS    = 12
_ANIM_PERIOD = 2.0
_TITLE_EVERY = 60


# ── Icon drawing ─────────────────────────────────────────────────────────────

def _color_for_battery(level: int | None) -> tuple[int, int, int]:
    if level is None or level >= 60:
        return (34, 197, 94)
    if level >= 30:
        return (250, 204, 21)
    return (239, 68, 68)


def _make_image(connected: bool, level: int | None = None, phase: float = 0.0) -> Image.Image:
    S   = 256
    pad = 12
    bbox = [pad, pad, S - pad, S - pad]
    rw   = 32

    img  = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse(bbox, fill=(22, 22, 22, 255))

    if not connected:
        draw.arc(bbox, start=-90, end=270, fill=(65, 65, 65, 200), width=rw)
        return img.resize((64, 64), Image.LANCZOS)

    r, g, b = _color_for_battery(level)
    breath  = (math.sin(phase * 2 * math.pi) + 1) / 2

    draw.arc(bbox, start=-90, end=270, fill=(42, 42, 42, 255), width=rw)

    arc_pct   = level if level is not None else 100
    end_angle = -90 + 360 * arc_pct / 100

    if arc_pct > 0:
        glow_alpha = int(30 + 60 * breath)
        glow_bbox  = [pad - 8, pad - 8, S - pad + 8, S - pad + 8]
        draw.arc(glow_bbox, start=-90, end=end_angle,
                 fill=(r, g, b, glow_alpha), width=rw + 20)

    bright = 0.78 + 0.22 * breath
    cr = min(255, int(r * bright))
    cg = min(255, int(g * bright))
    cb = min(255, int(b * bright))
    if arc_pct > 0:
        draw.arc(bbox, start=-90, end=end_angle, fill=(cr, cg, cb, 255), width=rw)

    return img.resize((64, 64), Image.LANCZOS)


# ── Tray app ─────────────────────────────────────────────────────────────────

class TrayApp:
    def __init__(self, device_name: str, data: dict, monitor, show_q: queue.Queue, bat=None):
        self._device_name  = device_name
        self._data         = data
        self._monitor      = monitor
        self._show_q       = show_q
        self._bat          = bat
        self._icon: pystray.Icon | None = None
        self._session_start: datetime | None = None
        self._anim_stop    = threading.Event()

    @property
    def monitor(self):
        return self._monitor

    def live_seconds(self) -> float:
        if self._session_start:
            return (datetime.now() - self._session_start).total_seconds()
        return 0.0

    def run_detached(self):
        self._monitor.on_connect    = self.on_connect
        self._monitor.on_disconnect = self.on_disconnect
        level = self._bat.level if self._bat else None
        self._icon = pystray.Icon(
            "BatteryLife",
            _make_image(self._monitor.is_connected, level),
            self._title(),
            pystray.Menu(self._menu_items),
        )
        if self._monitor.is_connected:
            self._start_animation()
        self._icon.run_detached()

    def stop(self):
        self._anim_stop.set()
        if self._icon:
            self._icon.stop()

    # ── Monitor callbacks ─────────────────────────────────────────────────────

    def on_connect(self):
        self._session_start = datetime.now()
        storage.start_session(self._data)
        self._start_animation()
        self._notify(
            f"{self._device_name} {i18n.t('device_connected')}",
            i18n.t("notif_started"),
        )

    def on_disconnect(self):
        self._stop_animation()
        self._session_start = None
        storage.end_session(self._data)
        if self._icon:
            self._icon.icon  = _make_image(False)
            self._icon.title = self._title()
        cycle = storage.active_cycle(self._data)
        total = i18n.fmt_time(cycle["total_seconds"]) if cycle else i18n.fmt_time(0)
        self._notify(
            f"{self._device_name} {i18n.t('device_disconnected')}",
            f"{i18n.t('notif_stopped')}: {total}",
        )

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _menu_items(self):
        connected = self._monitor.is_connected
        live      = self.live_seconds()
        level     = self._bat.level if self._bat else None
        cycle     = storage.active_cycle(self._data)

        if connected:
            status = f"{i18n.t('connected')}  {i18n.fmt_time(live)}"
        else:
            status = i18n.t("disconnected")

        bat_str = f"🔋 {level}%" if level is not None else f"🔋 {i18n.t('no_battery')}"

        if cycle:
            total      = storage.cycle_total_seconds(self._data, live)
            n          = len(cycle["sessions"])
            cycle_info = (f"{i18n.t('cycle')} {cycle['id']}: {i18n.fmt_time(total)}"
                          f"  ({n} {i18n.t('sessions_count')})")
        else:
            cycle_info = i18n.t("no_cycle")

        past = list(reversed(self._data.get("cycles", [])))
        if past:
            history_items = [
                pystray.MenuItem(
                    f"{i18n.t('cycle')} {c['id']}: {i18n.fmt_time(c['total_seconds'])}"
                    f" ({len([s for s in c['sessions'] if s['disconnected']])} {i18n.t('sessions_count')})",
                    None, enabled=False,
                )
                for c in past
            ]
        else:
            history_items = [pystray.MenuItem(i18n.t("no_history"), None, enabled=False)]

        as_label = i18n.t("autostart_on") if autostart.is_enabled() else i18n.t("autostart_off")

        yield pystray.MenuItem(i18n.t("show_timer"), self._on_show, default=True)
        yield pystray.Menu.SEPARATOR
        yield pystray.MenuItem(status,     None, enabled=False)
        yield pystray.MenuItem(bat_str,    None, enabled=False)
        yield pystray.MenuItem(cycle_info, None, enabled=False)
        yield pystray.Menu.SEPARATOR
        yield pystray.MenuItem(i18n.t("cycle_history"), pystray.Menu(*history_items))
        yield pystray.Menu.SEPARATOR
        yield pystray.MenuItem(i18n.t("new_cycle"),    self._on_new_cycle)
        yield pystray.MenuItem(i18n.t("reset_all"),    self._on_reset_all)
        yield pystray.MenuItem(as_label,               self._on_toggle_autostart)
        yield pystray.MenuItem(i18n.t("change_device"), self._on_change_device)
        yield pystray.MenuItem(i18n.t("lang_toggle"),  self._on_toggle_lang)
        yield pystray.Menu.SEPARATOR
        yield pystray.MenuItem(i18n.t("exit"), self._on_exit)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_show(self, icon, item):
        self._show_q.put("show")

    def _on_new_cycle(self, icon, item):
        self._show_q.put("confirm_new_cycle")

    def _on_reset_all(self, icon, item):
        self._show_q.put("confirm_reset_all")

    def _on_toggle_autostart(self, icon, item):
        autostart.disable() if autostart.is_enabled() else autostart.enable()

    def _on_change_device(self, icon, item):
        self._show_q.put("setup")

    def _on_toggle_lang(self, icon, item):
        self._show_q.put("lang")

    def _on_exit(self, icon, item):
        self._anim_stop.set()
        self._show_q.put("quit")
        icon.stop()

    def do_new_cycle(self):
        storage.new_cycle(self._data)
        if self._monitor.is_connected:
            self._session_start = datetime.now()
            storage.start_session(self._data)
        else:
            self._session_start = None
        self._update_static()

    def do_reset_all(self):
        storage.reset_all(self._data)
        self._session_start = None
        if self._monitor.is_connected:
            self._session_start = datetime.now()
            storage.start_session(self._data)
        self._update_static()

    # ── Animation ────────────────────────────────────────────────────────────

    def _start_animation(self):
        self._anim_stop.clear()
        frame_counter = [0]

        def _loop():
            phase = 0.0
            dt    = 1.0 / _ANIM_FPS
            while not self._anim_stop.wait(dt):
                phase = (phase + dt / _ANIM_PERIOD) % 1.0
                level = self._bat.level if self._bat else None
                if self._icon:
                    self._icon.icon = _make_image(True, level, phase)
                frame_counter[0] += 1
                if frame_counter[0] % _TITLE_EVERY == 0 and self._icon:
                    self._icon.title = self._title()

        threading.Thread(target=_loop, daemon=True, name="TrayAnim").start()

    def _stop_animation(self):
        self._anim_stop.set()

    def _update_static(self):
        if self._icon and not self._monitor.is_connected:
            self._icon.icon  = _make_image(False)
            self._icon.title = self._title()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _title(self) -> str:
        if self._monitor.is_connected:
            total = storage.cycle_total_seconds(self._data, self.live_seconds())
            level = self._bat.level if self._bat else None
            bat   = f" | {level}%" if level is not None else ""
            return f"{self._device_name}{bat} | {i18n.fmt_time(total)}"
        return f"{self._device_name} | {i18n.t('offline')}"

    def _notify(self, title: str, message: str):
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass
