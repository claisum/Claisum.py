"""Claisum macOS GUI Installer — v1.0.0.1  (GUI parity with Windows installer)"""
import sys, os, glob, shutil, threading, subprocess, urllib.request, webbrowser, traceback, time
import tkinter as tk
from tkinter import ttk, messagebox

VERSION = "1.0.0.1"
REPO    = "claisum/Claisum.py"

BG   = "#1a1b1e"
BG2  = "#111214"
BG3  = "#2d2f32"
BG4  = "#3a3c41"
ACC  = "#5865F2"
ACC2 = "#4752c4"
TXT  = "#dbdee1"
DIM  = "#80848e"
ERR  = "#f04747"
OK   = "#43b581"

MARKER = "claisum_inject"
INJECT = (
    "// [Claisum] Do NOT remove — uninstall via Claisum_macOS_Setup\n"
    "try{require('./claisum_inject.js');}catch(e){console.error('[Claisum load]',e);}\n"
)

EULA = """\
END-USER LICENSE AGREEMENT — Claisum v{ver}

By clicking "Next" you agree to the following terms:

1. LICENSE
   Claisum is free, open-source software released under the MIT licence.
   You may use, copy, and distribute it freely for non-commercial purposes.

2. DISCLAIMER
   Claisum modifies Discord's local application files. It is provided
   "as is", without warranty of any kind. Use at your own risk.

3. DISCORD ACCOUNT
   The authors are not responsible for any action Discord Inc. may take
   against accounts that use third-party modification tools.

4. AUTO-UPDATES
   Claisum downloads updates from GitHub automatically when Discord starts.
   No personal data is collected or transmitted.

5. UNINSTALLATION
   You may remove Claisum at any time by running this installer and
   choosing "Uninstall".

Claisum is not affiliated with or endorsed by Discord Inc.
Source code: https://github.com/{repo}
""".format(ver=VERSION, repo=REPO)


# ══ Helpers ════════════════════════════════════════════════════════════════

def find_all_discord() -> list[str]:
    """Return ALL discord_desktop_core index.js paths — all versions & flavours.
    Patching every one means Discord updates don't silently break Claisum."""
    lib = os.path.expanduser("~/Library/Application Support")
    candidates = []
    for name in ("discord", "discordptb", "discordcanary", "discorddev"):
        base = os.path.join(lib, name)
        for pat in (
            "*/modules/discord_desktop_core-*/discord_desktop_core/index.js",
            "app-*/modules/discord_desktop_core-*/discord_desktop_core/index.js",
            "modules/discord_desktop_core-*/discord_desktop_core/index.js",
        ):
            candidates.extend(glob.glob(os.path.join(base, pat)))
    return sorted(set(candidates))


def find_discord() -> str | None:
    c = find_all_discord()
    return c[-1] if c else None


def discord_running() -> bool:
    try:
        result = subprocess.run(["pgrep", "-x", "Discord"], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False


def kill_discord() -> None:
    subprocess.run(
        ["osascript", "-e", 'tell application "Discord" to quit'],
        capture_output=True)
    time.sleep(0.8)
    for name in ("Discord", "Discord PTB", "Discord Canary"):
        subprocess.run(["pkill", "-f", name], capture_output=True)
    time.sleep(0.5)


def open_discord() -> bool:
    for app in (
        "/Applications/Discord.app",
        os.path.expanduser("~/Applications/Discord.app"),
        "/Applications/Discord PTB.app",
        "/Applications/Discord Canary.app",
    ):
        if os.path.isdir(app):
            subprocess.Popen(["open", app],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    return False


def get_inject_src() -> str | None:
    exe_dir = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__)
    candidates = [
        os.path.join(exe_dir, "claisum_inject.js"),
        os.path.normpath(os.path.join(
            os.path.dirname(__file__), "..", "claisum", "discord", "claisum_inject.js")),
    ]
    return next((p for p in candidates if os.path.exists(p)), None)


def _strip_claisum(content: str) -> str:
    return "".join(
        line for line in content.splitlines(keepends=True)
        if MARKER not in line and "[Claisum]" not in line
    ).lstrip("\n")


def do_inject(idx: str) -> None:
    core = os.path.dirname(idx)
    dest = os.path.join(core, "claisum_inject.js")
    src  = get_inject_src()
    if src:
        shutil.copy2(src, dest)
    else:
        urllib.request.urlretrieve(
            f"https://raw.githubusercontent.com/{REPO}"
            "/main/claisum/discord/claisum_inject.js", dest)
    with open(idx, "r", encoding="utf-8") as f:
        raw = f.read()
    cleaned = _strip_claisum(raw)
    with open(idx, "w", encoding="utf-8") as f:
        f.write(INJECT + cleaned)


def do_remove(idx: str) -> bool:
    with open(idx, "r", encoding="utf-8") as f:
        raw = f.read()
    if MARKER not in raw and "[Claisum]" not in raw:
        return False
    dest = os.path.join(os.path.dirname(idx), "claisum_inject.js")
    with open(idx, "w", encoding="utf-8") as f:
        f.write(_strip_claisum(raw))
    try:
        os.remove(dest)
    except FileNotFoundError:
        pass
    return True


# ══ GUI ════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    PAGES = ("license", "action", "progress", "done")

    def __init__(self) -> None:
        super().__init__()
        self.title(f"Claisum Installer  v{VERSION}")
        self.geometry("560x430")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._init_styles()

        self.action     = tk.StringVar(value="install")
        self._page      = ""
        self._sel_rows  : dict = {}
        self._done_ok   = True
        self._done_msg  = ""
        self._done_detail = ""

        self._build_chrome()
        self._nav("license")

    def _center(self) -> None:
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"560x430+{(sw-560)//2}+{(sh-430)//2}")

    def _init_styles(self) -> None:
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("CL.Vertical.TScrollbar",
                    background=BG4, troughcolor=BG2,
                    arrowcolor=DIM, bordercolor=BG2, relief="flat")
        s.map("CL.Vertical.TScrollbar", background=[("active", "#55585e")])

    def _build_chrome(self) -> None:
        hdr = tk.Frame(self, bg=BG2, height=52)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=" CL ", bg=ACC, fg="#fff",
                 font=("Courier", 13, "bold")).pack(side="left", padx=16, pady=12)
        tk.Label(hdr, text=f"Claisum Installer  v{VERSION}",
                 bg=BG2, fg=TXT, font=("Menlo", 11, "bold")).pack(side="left")
        tk.Frame(self, bg="#08090b", height=1).pack(side="top", fill="x")

        tk.Frame(self, bg=BG4, height=1).pack(side="bottom", fill="x")
        foot = tk.Frame(self, bg=BG2, height=56)
        foot.pack(side="bottom", fill="x")
        foot.pack_propagate(False)

        for label, url in [
            ("GitHub",     f"https://github.com/{REPO}"),
            ("Releases",   f"https://github.com/{REPO}/releases"),
            ("Bug Report", f"https://github.com/{REPO}/issues"),
        ]:
            lbl = tk.Label(foot, text=label, bg=BG2, fg=DIM,
                           font=("Helvetica", 8), cursor="hand2")
            lbl.pack(side="left", padx=(12, 2), pady=18)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        self.btn_next = tk.Button(
            foot, text="Next", bg=ACC, fg="#fff",
            bd=0, relief="flat", font=("Helvetica", 10, "bold"),
            padx=26, pady=7, cursor="hand2", command=self._on_next)
        self.btn_next.pack(side="right", padx=(4, 14), pady=10)
        self._bind_hover(self.btn_next, ACC, ACC2)

        self.btn_back = tk.Button(
            foot, text="Back", bg=BG3, fg=TXT,
            bd=0, relief="flat", font=("Helvetica", 10, "bold"),
            padx=26, pady=7, cursor="hand2", state="disabled",
            command=self._on_back)
        self.btn_back.pack(side="right", padx=4, pady=10)
        self._bind_hover(self.btn_back, BG3, BG4)

        self.body = tk.Frame(self, bg=BG)
        self.body.pack(side="top", fill="both", expand=True)

    def _bind_hover(self, btn: tk.Button, normal: str, hover: str) -> None:
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover)
                 if btn["state"] != "disabled" else None)
        btn.bind("<Leave>", lambda e: btn.configure(bg=normal)
                 if btn["state"] != "disabled" else None)

    def _on_next(self) -> None:
        if getattr(self, "_nav_locked", False):
            return
        try:
            flow = {"license": "action", "action": "progress", "done": None}
            nxt = flow.get(self._page)
            if self._page == "done":
                self.destroy()
            elif nxt:
                self._nav(nxt)
        except Exception:
            messagebox.showerror("Error", traceback.format_exc())

    def _on_back(self) -> None:
        if getattr(self, "_nav_locked", False):
            return
        try:
            flow = {"action": "license", "done": "action"}
            prv = flow.get(self._page)
            if prv:
                self._nav(prv)
        except Exception:
            messagebox.showerror("Error", traceback.format_exc())

    def _nav(self, page: str) -> None:
        try:
            for w in self.body.winfo_children():
                w.destroy()
            self._page = page
            self._nav_locked = (page == "progress")
            can_back = page in ("action", "done")
            self.btn_back.configure(
                state="normal" if can_back else "disabled",
                fg=TXT if can_back else DIM)
            is_finish = (page == "done")
            is_locked = (page == "progress")
            self.btn_next.configure(
                text="Finish" if is_finish else "Next",
                bg=ACC if not is_locked else "#38393d",
                fg="#fff" if not is_locked else DIM,
                state="disabled" if is_locked else "normal")
            {
                "license":  self._render_license,
                "action":   self._render_action,
                "progress": self._render_progress,
                "done":     self._render_done,
            }[page]()
            self.body.update_idletasks()
        except Exception:
            messagebox.showerror("Installer Error", traceback.format_exc())

    def _section_hdr(self, badge: str, title: str) -> None:
        row = tk.Frame(self.body, bg=BG, padx=24)
        row.pack(fill="x", pady=(14, 10))
        tk.Label(row, text=f" {badge} ", bg=ACC, fg="#fff",
                 font=("Courier", 9, "bold")).pack(side="left", padx=(0, 10))
        tk.Label(row, text=title, bg=BG, fg=TXT,
                 font=("Helvetica", 13, "bold")).pack(side="left")

    def _render_license(self) -> None:
        self._section_hdr("EULA", "License Agreement")
        frame = tk.Frame(self.body, bg=BG3)
        frame.pack(fill="both", expand=True, padx=24)
        sb = ttk.Scrollbar(frame, orient="vertical", style="CL.Vertical.TScrollbar")
        txt = tk.Text(frame, bg=BG3, fg="#adb1b8", font=("Menlo", 9),
                      bd=0, relief="flat", wrap="word", padx=12, pady=10,
                      yscrollcommand=sb.set, cursor="arrow",
                      selectbackground=BG4, exportselection=False)
        sb.configure(command=txt.yview)
        sb.pack(side="right", fill="y", pady=1, padx=(0, 1))
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", EULA)
        txt.configure(state="disabled")
        note = tk.Frame(self.body, bg=BG, padx=24)
        note.pack(fill="x", pady=(8, 14))
        tk.Label(note, text="Click → Next to accept the terms and continue.",
                 bg=BG, fg=DIM, font=("Helvetica", 9)).pack(anchor="w")

    def _render_action(self) -> None:
        try:
            idx = find_discord()
            if idx:
                with open(idx, "r", encoding="utf-8") as f:
                    installed = MARKER in f.read()
                default = "repair" if installed else "install"
            else:
                default = "install"
        except Exception:
            default = "install"
        self.action.set(default)
        self._section_hdr("ACT", "Choose an Action")
        self._sel_rows = {}
        actions = [
            ("install",   "+", "Install Claisum",
             "Inject Claisum into Discord for the first time"),
            ("repair",    "~", "Repair / Re-install",
             "Re-inject if Claisum stopped working after a Discord update"),
            ("uninstall", "×", "Uninstall Claisum",
             "Completely remove Claisum and restore Discord to stock"),
        ]
        for val, badge, name, desc in actions:
            self._make_action_row(val, badge, name, desc)
        self._apply_action_sel(default)

    def _make_action_row(self, val, badge, name, desc) -> None:
        row = tk.Frame(self.body, bg=BG3, cursor="hand2")
        row.pack(fill="x", padx=24, pady=3)
        inner = tk.Frame(row, bg=BG3)
        inner.pack(fill="both", padx=12, pady=10)
        badge_lbl = tk.Label(inner, text=f" {badge} ", bg=BG4, fg=DIM,
                             font=("Courier", 12, "bold"), width=3)
        badge_lbl.pack(side="left", padx=(0, 12))
        text_col = tk.Frame(inner, bg=BG3)
        text_col.pack(side="left", fill="x", expand=True)
        name_lbl = tk.Label(text_col, text=name, bg=BG3, fg=TXT,
                            font=("Helvetica", 11, "bold"), anchor="w")
        name_lbl.pack(anchor="w")
        desc_lbl = tk.Label(text_col, text=desc, bg=BG3, fg=DIM,
                            font=("Helvetica", 9), anchor="w",
                            wraplength=380, justify="left")
        desc_lbl.pack(anchor="w")
        widgets = (row, inner, badge_lbl, text_col, name_lbl, desc_lbl)
        self._sel_rows[val] = widgets
        for w in widgets:
            w.bind("<Button-1>", lambda e, v=val: self._apply_action_sel(v))

    def _apply_action_sel(self, val) -> None:
        self.action.set(val)
        for v, (row, inner, badge_lbl, text_col, name_lbl, desc_lbl) in \
                self._sel_rows.items():
            on = (v == val)
            bg  = ACC if on else BG3
            fg  = "#fff" if on else TXT
            dfg = "#c5d0ff" if on else DIM
            bbg = ACC2 if on else BG4
            bfg = "#fff" if on else DIM
            for w in (row, inner, text_col):
                w.configure(bg=bg)
            badge_lbl.configure(bg=bbg, fg=bfg)
            name_lbl.configure(bg=bg, fg=fg)
            desc_lbl.configure(bg=bg, fg=dfg)

    def _render_progress(self) -> None:
        act = self.action.get()
        label = {"install": "Installing…",
                 "repair": "Repairing…",
                 "uninstall": "Uninstalling…"}.get(act, "Working…")
        self._section_hdr(">>", label)
        self._status_var = tk.StringVar(value="Preparing…")
        tk.Label(self.body, textvariable=self._status_var,
                 bg=BG, fg=DIM, font=("Helvetica", 9),
                 anchor="w", padx=24).pack(fill="x", pady=(0, 10))
        pb_bg = tk.Frame(self.body, bg=BG3, height=8)
        pb_bg.pack(fill="x", padx=24)
        self._pb = tk.Frame(pb_bg, bg=ACC, height=8)
        self._pb.place(relwidth=0.0, relheight=1.0)
        log_frame = tk.Frame(self.body, bg=BG2)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(12, 0))
        self._log = tk.Text(log_frame, bg=BG2, fg="#6a7080",
                            font=("Menlo", 8), bd=0, relief="flat",
                            wrap="word", padx=8, pady=6,
                            state="disabled", cursor="arrow", height=6)
        self._log.pack(fill="both", expand=True)
        threading.Thread(target=self._worker, daemon=True).start()

    def _upd(self, msg: str, progress: float | None = None) -> None:
        def _apply():
            try:
                self._status_var.set(msg)
                if progress is not None:
                    self._pb.place(relwidth=max(0.0, min(1.0, progress)), relheight=1.0)
                self._log.configure(state="normal")
                self._log.insert("end", f"▶ {msg}\n")
                self._log.see("end")
                self._log.configure(state="disabled")
            except Exception:
                pass
        self.after(0, _apply)

    def _worker(self) -> None:
        try:
            if self.action.get() in ("install", "repair"):
                self._do_install()
            else:
                self._do_uninstall()
        except Exception as exc:
            tb = traceback.format_exc()
            self.after(0, lambda: self._finish(False, str(exc), tb))

    def _do_install(self) -> None:
        if discord_running():
            self._upd("Closing Discord…", 0.05)
            kill_discord()

        self._upd("Locating Discord installations…", 0.15)
        indices = find_all_discord()
        if not indices:
            raise RuntimeError(
                "Discord not found.\n\n"
                "Install Discord from https://discord.com/download\n"
                "and launch it at least once, then try again.")
        self._upd(f"Found {len(indices)} Discord installation(s).", 0.22)

        self._upd("Downloading Claisum inject script…", 0.35)
        src = get_inject_src()
        js_content: bytes | None = None
        if not src:
            urllib_req = urllib.request.urlopen(
                f"https://raw.githubusercontent.com/{REPO}"
                "/main/claisum/discord/claisum_inject.js")
            js_content = urllib_req.read()

        step = 0.55 / max(len(indices), 1)
        for i, idx in enumerate(indices):
            self._upd(f"Patching [{i+1}/{len(indices)}]…", 0.40 + i * step)
            core = os.path.dirname(idx)
            dest = os.path.join(core, "claisum_inject.js")
            if src:
                shutil.copy2(src, dest)
            else:
                with open(dest, "wb") as f:
                    f.write(js_content)
            inject_into(idx)

        self._upd("Verifying patches…", 0.95)
        for idx in indices:
            with open(idx, "r", encoding="utf-8") as f:
                if MARKER not in f.read():
                    raise RuntimeError(f"Patch verification failed:\n{idx}")

        self._upd("Done!", 1.0)
        self.after(500, lambda: self._finish(
            True,
            "Claisum installed successfully!\n\n"
            "⚡ Click the glowing ⚡ button in the bottom-left of Discord\n"
            "   to open the Claisum panel — or press F8.\n\n"
            "🔁 Claisum updates automatically every time Discord starts."))

    def _do_uninstall(self) -> None:
        if discord_running():
            self._upd("Closing Discord…", 0.08)
            kill_discord()

        self._upd("Locating Discord installations…", 0.20)
        indices = find_all_discord()
        if not indices:
            raise RuntimeError("Discord installation not found.")

        step = 0.70 / max(len(indices), 1)
        for i, idx in enumerate(indices):
            self._upd(f"Removing [{i+1}/{len(indices)}]…", 0.25 + i * step)
            do_remove(idx)
            dest = os.path.join(os.path.dirname(idx), "claisum_inject.js")
            try:
                os.remove(dest)
            except FileNotFoundError:
                pass

        self._upd("Verifying removal…", 0.95)
        for idx in indices:
            with open(idx, "r", encoding="utf-8") as f:
                if MARKER in f.read():
                    raise RuntimeError(f"Removal failed — traces remain:\n{idx}")

        self._upd("Done!", 1.0)
        self.after(500, lambda: self._finish(
            True,
            "Claisum removed successfully!\n\n"
            "Discord has been fully restored to its original state.\n"
            "Start Discord to confirm it opens normally."))

    def _finish(self, ok: bool, msg: str, detail: str = "") -> None:
        self._done_ok     = ok
        self._done_msg    = msg
        self._done_detail = detail
        self._nav("done")

    def _render_done(self) -> None:
        ok     = getattr(self, "_done_ok", True)
        msg    = getattr(self, "_done_msg", "")
        detail = getattr(self, "_done_detail", "")
        self._section_hdr("OK" if ok else "!!", "Done!" if ok else "Error")
        col = TXT if ok else ERR
        tk.Label(self.body, text=msg, bg=BG, fg=col,
                 font=("Helvetica", 10), wraplength=500,
                 justify="left", padx=24).pack(anchor="w", pady=(4, 0))
        if not ok and detail:
            det_frame = tk.Frame(self.body, bg=BG2)
            det_frame.pack(fill="x", padx=24, pady=(10, 0))
            tb_txt = tk.Text(det_frame, bg=BG2, fg="#6a7080",
                             font=("Menlo", 8), bd=0, relief="flat",
                             wrap="word", padx=8, pady=6, height=6,
                             state="disabled", cursor="arrow")
            tb_txt.pack(fill="both", expand=True)
            tb_txt.configure(state="normal")
            tb_txt.insert("1.0", detail)
            tb_txt.configure(state="disabled")
        if ok and self.action.get() in ("install", "repair"):
            restart_frame = tk.Frame(self.body, bg=BG, padx=24)
            restart_frame.pack(fill="x", pady=(14, 0))
            tk.Button(
                restart_frame, text="▶  Launch Discord",
                bg=OK, fg="#fff", bd=0, relief="flat",
                font=("Helvetica", 10, "bold"), padx=18, pady=7,
                cursor="hand2",
                command=lambda: (open_discord(), self.destroy())
            ).pack(side="left")


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
