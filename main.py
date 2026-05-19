import ctypes
import queue
import re
import sys
import tkinter as tk
import tkinter.messagebox
from datetime import datetime

import autostart  # noqa: F401 — triggers old-key migration
import config
import i18n
import storage
from battery import BatteryMonitor
from monitor import BluetoothMonitor, list_connected_bt_devices
from tray import TrayApp

_MUTEX_NAME = "Global\\BatteryLifeApp"
_stats_win: tk.Toplevel | None = None
_refresh_lang_cb: list = [None]


# ── Single-instance guard ─────────────────────────────────────────────────────

def _acquire_single_instance():
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, _MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183:
        sys.exit(0)
    return mutex


# ── Dark titlebar ─────────────────────────────────────────────────────────────

def _dark_titlebar(win):
    try:
        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20,
            ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


# ── Fade helper ───────────────────────────────────────────────────────────────

def _fade(win, start: float, end: float, steps: int, step_ms: int, on_done=None):
    delta   = (end - start) / steps
    current = [start]

    def tick():
        current[0] += delta
        alpha = max(0.0, min(1.0, current[0]))
        try:
            win.attributes("-alpha", alpha)
        except tk.TclError:
            return
        if (delta > 0 and alpha >= end) or (delta < 0 and alpha <= end):
            win.attributes("-alpha", end)
            if on_done:
                on_done()
        else:
            win.after(step_ms, tick)

    tick()


# ── Device-picker page (shared by onboarding + change-device dialog) ──────────

def _build_device_page(container: tk.Widget, win: tk.Toplevel, result: list,
                       current: str = ""):
    tk.Label(container, text=i18n.t("setup_header"),
             font=("Segoe UI", 14, "bold"), bg="#1e1e1e", fg="#ffffff",
             ).pack(pady=(28, 4))

    tk.Label(container, text=i18n.t("setup_hint"),
             font=("Segoe UI", 9), bg="#1e1e1e", fg="#666666",
             wraplength=320, justify="center",
             ).pack(pady=(0, 10))

    lb = tk.Listbox(container, height=5,
                    bg="#141414", fg="#cccccc",
                    font=("Segoe UI", 10), relief="flat", bd=0,
                    selectbackground="#22c55e", selectforeground="#000000",
                    activestyle="none", cursor="hand2")
    lb.pack(fill="x", padx=24)

    selected = [current]

    def refresh():
        lb.delete(0, "end")
        names = list_connected_bt_devices()
        for n in names:
            lb.insert("end", f"  {n}")
            if n == selected[0]:
                lb.selection_set("end")
        if not names:
            lb.insert("end", f"  {i18n.t('setup_no_devices')}")

    def on_select(event):
        sel = lb.curselection()
        if sel:
            name = lb.get(sel[0]).strip()
            if not name.startswith("("):
                selected[0] = name

    lb.bind("<<ListboxSelect>>", on_select)

    def on_start():
        name = selected[0]
        if not name:
            orig = lb.cget("bg")
            lb.config(bg="#3a1a1a")
            win.after(500, lambda: lb.config(bg=orig))
            return
        result[0] = name
        win.destroy()

    btn_frame = tk.Frame(container, bg="#1e1e1e")
    btn_frame.pack(fill="x", padx=24, pady=(14, 0))

    tk.Button(btn_frame, text=i18n.t("setup_detect"),
              font=("Segoe UI", 9), bg="#2a2a2a", fg="#888888",
              relief="flat", bd=0, cursor="hand2",
              activebackground="#333333", activeforeground="#aaaaaa",
              command=refresh, padx=10, pady=6,
              ).pack(side="left")

    tk.Button(btn_frame, text=i18n.t("setup_start"),
              font=("Segoe UI", 10, "bold"), bg="#22c55e", fg="#000000",
              relief="flat", bd=0, cursor="hand2",
              activebackground="#16a34a", activeforeground="#000000",
              command=on_start, padx=14, pady=6,
              ).pack(side="right")

    win.bind("<Return>", lambda e: on_start())
    win.bind("<Escape>", lambda e: win.destroy())

    # ── Auto-refresh device list every 2 seconds ──────────────────────────────
    _auto_job = [None]

    def _auto_refresh():
        try:
            refresh()
            _auto_job[0] = win.after(2000, _auto_refresh)
        except tk.TclError:
            pass  # window was destroyed

    def _cancel_auto_refresh(event=None):
        if _auto_job[0]:
            try:
                win.after_cancel(_auto_job[0])
            except Exception:
                pass
            _auto_job[0] = None

    win.bind("<Destroy>", _cancel_auto_refresh, add="+")
    _auto_refresh()  # initial populate + start periodic refresh


# ── Onboarding (first-run) ────────────────────────────────────────────────────

def _run_onboarding(root: tk.Tk) -> str | None:
    W, H = 380, 340
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

    win = tk.Toplevel(root)
    win.title("BatteryLife")
    win.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")
    win.configure(bg="#1e1e1e")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.attributes("-alpha", 0.0)
    win.update()
    _dark_titlebar(win)

    result = [None]

    # Page 1 — Welcome
    p1 = tk.Frame(win, bg="#1e1e1e")

    tk.Label(p1, text="BatteryLife",
             font=("Segoe UI", 28, "bold"), bg="#1e1e1e", fg="#ffffff",
             ).pack(pady=(52, 10))

    tk.Label(p1, text=i18n.t("welcome_desc"),
             font=("Segoe UI", 11), bg="#1e1e1e", fg="#777777",
             justify="center",
             ).pack()

    tk.Frame(p1, bg="#1e1e1e").pack(expand=True)

    def go_to_p2():
        def after_out():
            p1.pack_forget()
            p2 = tk.Frame(win, bg="#1e1e1e")
            _build_device_page(p2, win, result)
            p2.pack(fill="both", expand=True)
            win.update_idletasks()
            _fade(win, 0.0, 1.0, 14, 16)

        _fade(win, 1.0, 0.0, 14, 16, after_out)

    tk.Button(p1, text=i18n.t("welcome_btn"),
              font=("Segoe UI", 12, "bold"), bg="#22c55e", fg="#000000",
              relief="flat", bd=0, cursor="hand2",
              activebackground="#16a34a", activeforeground="#000000",
              padx=0, pady=14,
              command=go_to_p2,
              ).pack(fill="x", padx=32, pady=(0, 36))

    p1.pack(fill="both", expand=True)
    _fade(win, 0.0, 1.0, 14, 16)

    root.wait_window(win)
    return result[0]


# ── Change-device dialog ──────────────────────────────────────────────────────

def _show_setup_dialog(root: tk.Tk, current: str = "") -> str | None:
    W, H = 380, 300
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

    win = tk.Toplevel(root)
    win.title("BatteryLife")
    win.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")
    win.configure(bg="#1e1e1e")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.update()
    _dark_titlebar(win)

    result = [None]
    _build_device_page(win, win, result, current=current)

    root.wait_window(win)
    return result[0]


# ── Handle drawing ────────────────────────────────────────────────────────────

def _draw_handle(canvas: tk.Canvas, expanded: bool, hover: bool = False,
                 phase: float | None = None):
    """Animated chevron. phase 0.0=∧ collapsed (points up), 1.0=∨ expanded (points down)."""
    canvas.delete("all")
    cx  = 150
    cy  = 22
    col = "#909090" if hover else "#606060"

    if phase is None:
        phase = 1.0 if expanded else 0.0
    # phase=0 → ∧ (peak above sides);  phase=1 → ∨ (peak below sides)
    spread = 10
    height = 6
    peak_y = cy - height / 2 + phase * height
    side_y = cy + height / 2 - phase * height
    pts    = [cx - spread, side_y, cx, peak_y, cx + spread, side_y]
    canvas.create_line(pts, fill=col, width=1.8, capstyle="round", joinstyle="round")


# ── Stats window ──────────────────────────────────────────────────────────────

def _open_stats(root: tk.Tk, app: TrayApp, data: dict, bat: BatteryMonitor, cfg: dict,
                fade_in: bool = False, pos: tuple | None = None):
    global _stats_win

    if _stats_win is not None and _stats_win.winfo_exists():
        _stats_win.lift()
        _stats_win.focus_force()
        return

    win = tk.Toplevel(root)
    win.title("BatteryLife")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    if fade_in:
        win.attributes("-alpha", 0.0)
    win.focus_force()
    win.update()
    _dark_titlebar(win)

    W           = 300
    H_COLLAPSED = 255
    H_EXPANDED  = 400

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    if pos:
        init_x, init_y = pos
    else:
        init_x = sw - W - 24
        init_y = sh - H_COLLAPSED - 64

    win.geometry(f"{W}x{H_COLLAPSED}+{init_x}+{init_y}")
    win.configure(bg="#1e1e1e")

    status_var  = tk.StringVar()
    total_var   = tk.StringVar()
    battery_var = tk.StringVar()
    session_var = tk.StringVar()
    cycle_var   = tk.StringVar()

    tk.Label(win, textvariable=status_var,
             font=("Segoe UI", 12), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(14, 0))

    tk.Label(win, textvariable=total_var,
             font=("Segoe UI", 42, "bold"), bg="#1e1e1e", fg="#ffffff").pack()

    battery_lbl = tk.Label(win, textvariable=battery_var,
                           font=("Segoe UI", 13), bg="#1e1e1e", fg="#facc15")
    battery_lbl.pack(pady=(2, 0))

    tk.Label(win, textvariable=session_var,
             font=("Segoe UI", 10), bg="#1e1e1e", fg="#666666").pack(pady=(3, 0))

    tk.Label(win, textvariable=cycle_var,
             font=("Segoe UI", 9), bg="#1e1e1e", fg="#555555").pack(pady=(2, 0))

    # Language toggle — top-right
    lang_btn = tk.Button(
        win, text=i18n.get_lang().upper(),
        font=("Segoe UI", 8), bg="#1e1e1e", fg="#444444",
        relief="flat", bd=0, cursor="hand2",
        activebackground="#2a2a2a", activeforeground="#888888",
        padx=6, pady=4,
    )
    lang_btn.place(relx=1.0, rely=0.0, x=-6, y=6, anchor="ne")

    # ── Battery history ───────────────────────────────────────────────────────
    history_expanded = [False]

    log_frame = tk.Frame(win, bg="#1e1e1e")

    _log_wrap = tk.Frame(log_frame, bg="#141414")
    _log_wrap.pack(fill="x", padx=12, pady=(0, 10))

    log_text = tk.Text(
        _log_wrap, height=7, bg="#141414", fg="#888888",
        font=("Consolas", 8), relief="flat", bd=0,
        state="disabled", cursor="arrow", padx=6, pady=5,
        wrap="none",
    )
    log_text.pack(side="left", fill="both", expand=True)

    sb_canvas    = tk.Canvas(_log_wrap, width=6, bg="#141414", highlightthickness=0)
    sb_canvas.pack(side="right", fill="y", padx=(0, 3), pady=4)

    _sb_pos     = [0.0, 1.0]
    _sb_hide_id = [None]

    def _sb_render():
        first, last = _sb_pos
        h = sb_canvas.winfo_height()
        sb_canvas.delete("all")
        if h < 4 or (last - first) >= 1.0:
            return
        y0 = max(0, int(h * first))
        y1 = min(h, max(y0 + 14, int(h * last)))
        sb_canvas.create_rectangle(1, y0, 5, y1, fill="#666666", outline="")

    def _sb_yscroll(first, last):
        _sb_pos[0], _sb_pos[1] = float(first), float(last)

    def _sb_wheel(event):
        log_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        _sb_render()
        if _sb_hide_id[0]:
            sb_canvas.after_cancel(_sb_hide_id[0])
        def _hide():
            sb_canvas.delete("all")
        _sb_hide_id[0] = sb_canvas.after(1500, _hide)

    log_text.config(yscrollcommand=_sb_yscroll)
    log_text.bind("<MouseWheel>", _sb_wheel)

    for tag, fg in [("green", "#22c55e"), ("yellow", "#facc15"),
                    ("red", "#ef4444"), ("dim", "#555555"), ("time", "#666666")]:
        log_text.tag_configure(tag, foreground=fg)

    # iOS-style handle — taller for easier clicking
    handle = tk.Canvas(win, width=W, height=44, bg="#1e1e1e",
                       highlightthickness=0, cursor="hand2")
    handle.pack(fill="x", pady=(4, 0))

    _anim_lock = [False]

    def toggle_history():
        if _anim_lock[0]:
            return

        expanding = not history_expanded[0]

        # Read position from geometry string — same coord system as geometry() calls,
        # avoids winfo_x/y which use physical pixels while geometry uses logical on HiDPI
        _m = re.match(r'\d+x\d+([+-]\d+)([+-]\d+)', win.geometry())
        cur_x = int(_m.group(1)) if _m else init_x
        cur_y = int(_m.group(2)) if _m else win.winfo_y()

        if expanding:
            from_h, to_h = H_COLLAPSED, H_EXPANDED
            from_y = cur_y
            to_y   = cur_y - (H_EXPANDED - H_COLLAPSED)  # grow upward
        else:
            # Hide content BEFORE shrinking so no layout jump
            log_frame.pack_forget()
            win.update_idletasks()
            from_h, to_h = H_EXPANDED, H_COLLAPSED
            from_y = cur_y
            to_y   = cur_y + (H_EXPANDED - H_COLLAPSED)

        STEPS   = 22
        STEP_MS = 11   # ~250 ms total

        _anim_lock[0] = True

        def tick(step):
            t_lin = (step + 1) / STEPS
            t     = t_lin * t_lin * (3 - 2 * t_lin)   # smoothstep
            h     = int(from_h + (to_h - from_h) * t)
            y_pos = int(from_y + (to_y - from_y) * t)
            ph    = t if expanding else (1.0 - t)
            try:
                win.geometry(f"{W}x{h}+{cur_x}+{y_pos}")
            except tk.TclError:
                _anim_lock[0] = False
                return
            _draw_handle(handle, expanding, phase=ph)
            if step + 1 >= STEPS:
                win.geometry(f"{W}x{to_h}+{cur_x}+{to_y}")
                history_expanded[0] = expanding
                if expanding:
                    log_frame.pack(fill="x")
                _draw_handle(handle, history_expanded[0])
                _anim_lock[0] = False
            else:
                win.after(STEP_MS, lambda: tick(step + 1))

        tick(0)

    handle.bind("<Button-1>", lambda e: toggle_history())
    handle.bind("<Enter>",    lambda e: _draw_handle(handle, history_expanded[0], hover=True))
    handle.bind("<Leave>",    lambda e: _draw_handle(handle, history_expanded[0], hover=False))
    win.after(30, lambda: _draw_handle(handle, False))

    # ── Static label refresh (language switch) ────────────────────────────────
    def refresh_static():
        lang_btn.config(text=i18n.get_lang().upper())
        _draw_handle(handle, history_expanded[0])

    _refresh_lang_cb[0] = refresh_static

    def on_lang_toggle():
        new_lang = "en" if i18n.get_lang() == "ru" else "ru"
        i18n.set_lang(new_lang)
        cfg["language"] = new_lang
        config.save(cfg)
        refresh_static()

    lang_btn.config(command=on_lang_toggle)

    # ── Live update ───────────────────────────────────────────────────────────
    after_id = [None]

    def update():
        live      = app.live_seconds()
        connected = app.monitor.is_connected
        cycle     = storage.active_cycle(data)
        level     = bat.level

        status_var.set(i18n.t("connected") if connected else i18n.t("disconnected"))
        total_var.set(i18n.fmt_time(storage.grand_total_seconds(data, live)))

        if level is not None:
            filled = round(level / 10)
            battery_var.set(f"🔋 {'█' * filled}{'░' * (10 - filled)}  {level}%")
            battery_lbl.config(
                fg="#22c55e" if level >= 60 else "#facc15" if level >= 30 else "#ef4444"
            )
        else:
            battery_var.set(f"🔋 {i18n.t('no_battery')}")
            battery_lbl.config(fg="#555555")

        if connected and live > 1:
            session_var.set(f"{i18n.t('session')}: {i18n.fmt_time(live)}")
        else:
            session_var.set("")

        if cycle:
            n = len(cycle["sessions"])
            cycle_var.set(
                f"{i18n.t('cycle')} {cycle['id']}: "
                f"{i18n.fmt_time(storage.cycle_total_seconds(data, live))}"
                f"  ·  {n} {i18n.t('sessions_count')}"
            )

        if history_expanded[0]:
            raw = storage.get_battery_log(data, 50)
            # Deduplicate: keep only entries where the 10% decade changes
            entries: list = []
            for e in raw:
                if not entries or entries[-1]["level"] // 10 != e["level"] // 10:
                    entries.append(e)
            entries = entries[-10:]   # show last 10 threshold crossings

            log_text.config(state="normal")
            log_text.delete("1.0", "end")
            if entries:
                for idx, e in enumerate(entries):
                    t_   = datetime.fromisoformat(e["time"])
                    lvl  = e["level"]
                    filled = round(lvl / 10)
                    bar  = "█" * filled + "░" * (10 - filled)
                    dstr = ""
                    if idx > 0:
                        prev_t = datetime.fromisoformat(entries[idx - 1]["time"])
                        dstr   = f"  +{i18n.fmt_time((t_ - prev_t).total_seconds())}"
                    color = "green" if lvl >= 60 else "yellow" if lvl >= 30 else "red"
                    log_text.insert("end", f"{t_.strftime('%d.%m  %H:%M')}  ", "time")
                    log_text.insert("end", bar,            color)
                    log_text.insert("end", f"  {lvl:>3}%", color)
                    log_text.insert("end", f"{dstr}\n",    "dim")
            else:
                log_text.insert("end", i18n.t("no_history_data"), "dim")
            log_text.config(state="disabled")

        after_id[0] = win.after(1000, update)

    def on_close():
        global _stats_win
        _refresh_lang_cb[0] = None
        if after_id[0]:
            win.after_cancel(after_id[0])
        win.destroy()
        _stats_win = None

    win.protocol("WM_DELETE_WINDOW", on_close)
    _stats_win = win
    update()
    if fade_in:
        _fade(win, 0.0, 1.0, 14, 16)


# ── Auto-detect currently connected known device ──────────────────────────────

def _auto_detect_device(cfg: dict) -> bool:
    """
    If the configured device is not connected but another known (previously tracked)
    device is connected, silently switch to it. Returns True if switched.
    """
    if not cfg["device_name"]:
        return False

    connected_devs = list_connected_bt_devices()
    if not connected_devs:
        return False

    # Check whether the configured device is among the connected ones
    cfg_lower = cfg["device_name"].lower()
    if any(cfg_lower in d.lower() for d in connected_devs):
        return False  # configured device is connected — nothing to do

    # Configured device is NOT connected; look for a known device that IS connected
    known = set(storage.list_known_devices())  # safe folder names
    for dev in connected_devs:
        if storage.safe_name(dev) in known:
            cfg["device_name"] = dev
            config.save(cfg)
            return True

    return False


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    _mutex = _acquire_single_instance()  # noqa: F841

    # Migrate data from old location (data/ next to exe) to %APPDATA%\BatteryLife
    storage.migrate_from_exe_dir()

    cfg = config.load()

    lang = cfg["language"]
    if lang == "auto":
        lang = i18n.detect_system_lang()
    i18n.set_lang(lang)

    data = storage.load()
    storage.ensure_cycle(data)

    show_q: queue.Queue = queue.Queue()
    root = tk.Tk()
    root.withdraw()

    first_run = not cfg["device_name"]

    if first_run:
        device_name = _run_onboarding(root)
        if not device_name:
            sys.exit(0)
        cfg["device_name"] = device_name
        cfg["language"]    = i18n.get_lang()
        config.save(cfg)
    else:
        # Auto-switch to whichever known device is currently connected
        _auto_detect_device(cfg)

    # Init per-device storage (also migrates legacy sessions.json on first use)
    storage.set_device(cfg["device_name"])
    data.clear()
    data.update(storage.load())
    storage.ensure_cycle(data)

    monitor = BluetoothMonitor(cfg["device_name"], cfg["poll_interval"])
    bat     = BatteryMonitor(cfg["device_name"], cfg["battery_interval"])
    app     = TrayApp(cfg["device_name"], data, monitor, show_q, bat=bat)

    bat.on_change = lambda level: storage.log_battery(data, level)

    monitor.start()
    bat.start()
    app.run_detached()

    # Auto-open stats after first-run setup
    if first_run:
        show_q.put("show")

    def poll_queue():
        try:
            while True:
                cmd = show_q.get_nowait()

                if cmd == "show":
                    _open_stats(root, app, data, bat, cfg)

                elif cmd == "confirm_new_cycle":
                    if tkinter.messagebox.askyesno(
                        i18n.t("confirm_nc_title"), i18n.t("confirm_nc_msg"), parent=root,
                    ):
                        app.do_new_cycle()

                elif cmd == "confirm_reset_all":
                    if tkinter.messagebox.askyesno(
                        i18n.t("confirm_reset_title"), i18n.t("confirm_reset_msg"),
                        icon="warning", parent=root,
                    ):
                        app.do_reset_all()

                elif cmd == "setup":
                    new_name = _show_setup_dialog(root, current=cfg["device_name"])
                    if new_name:
                        # Save position and close stats window
                        saved_pos = None
                        stats_was_open = _stats_win is not None and _stats_win.winfo_exists()
                        if stats_was_open:
                            _m = re.match(r'\d+x\d+([+-]\d+)([+-]\d+)', _stats_win.geometry())
                            if _m:
                                saved_pos = (int(_m.group(1)), int(_m.group(2)))
                            _stats_win.destroy()

                        if new_name != cfg["device_name"]:
                            # End live session for old device
                            if app.monitor.is_connected:
                                storage.end_session(data)

                            cfg["device_name"] = new_name
                            config.save(cfg)

                            # Switch to per-device storage for new device
                            storage.set_device(new_name)
                            new_data = storage.load()
                            storage.ensure_cycle(new_data)
                            data.clear()
                            data.update(new_data)

                            monitor.set_device(new_name)
                            bat.set_device(new_name)
                            app._device_name   = new_name
                            app._session_start = None
                            app._update_static()

                        # Always reopen stats with fade-in at saved position
                        _open_stats(root, app, data, bat, cfg, fade_in=True, pos=saved_pos)

                elif cmd == "lang":
                    new_lang = "en" if i18n.get_lang() == "ru" else "ru"
                    i18n.set_lang(new_lang)
                    cfg["language"] = new_lang
                    config.save(cfg)
                    if _refresh_lang_cb[0]:
                        _refresh_lang_cb[0]()

                elif cmd == "quit":
                    bat.stop()
                    monitor.stop()
                    root.quit()
                    return

        except queue.Empty:
            pass
        root.after(200, poll_queue)

    poll_queue()
    root.mainloop()
    app.stop()


if __name__ == "__main__":
    main()
