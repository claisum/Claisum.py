"""Claisum Installer v1.0.0.1"""
import sys, os, glob, shutil, threading, subprocess, urllib.request, webbrowser, traceback
import tkinter as tk
from tkinter import ttk, messagebox

VERSION = "1.0.0.1"
REPO    = "claisum/Claisum.py"
BG      = "#1a1b1e"
BG2     = "#111214"
BG3     = "#2d2f32"
BG4     = "#3a3c41"
ACCENT  = "#5865F2"
TEXT    = "#dbdee1"
DIM     = "#80848e"
ERR     = "#f04747"

# Injection marker — MUST appear in every injected index.js line
MARKER = "claisum_inject"

# The single line we write to index.js (two lines: comment + require)
INJECT = (
    "// [Claisum] Remove this line and the next to uninstall\n"
    "try{require('./claisum_inject.js');}catch(e){console.error('[Claisum]',e);}\n"
)

EULA = (
    "End-User License Agreement for Claisum\n\n"
    "By installing Claisum you agree to:\n\n"
    "1. Free open-source software, no warranty.\n"
    "2. Not for commercial redistribution.\n"
    "3. Modifies Discord local files - use at your own risk.\n"
    "4. Authors not responsible for Discord account actions.\n"
    "5. Auto-updates from GitHub on every Discord start.\n\n"
    "Not affiliated with Discord Inc.\n"
    "https://github.com/claisum/Claisum.py"
)


def find_discord():
    for base in [
        os.path.expandvars(r"%LOCALAPPDATA%\\Discord"),
        os.path.expandvars(r"%LOCALAPPDATA%\\discordptb"),
        os.path.expandvars(r"%LOCALAPPDATA%\\discordcanary"),
    ]:
        hits = glob.glob(os.path.join(
            base, "app-*", "modules",
            "discord_desktop_core-*", "discord_desktop_core", "index.js"))
        if hits:
            return sorted(hits)[-1]
    return None


def get_inject_src():
    exe_dir = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__)
    for p in [
        os.path.join(exe_dir, "claisum_inject.js"),
        os.path.normpath(os.path.join(
            os.path.dirname(__file__), "..", "claisum", "discord", "claisum_inject.js")),
    ]:
        if os.path.exists(p):
            return p
    return None


def do_inject(idx):
    with open(idx, "r", encoding="utf-8") as f:
        raw = f.read()
    # Remove any existing injection first
    raw = do_remove_str(raw)
    with open(idx, "w", encoding="utf-8") as f:
        f.write(INJECT + raw)


def do_remove_str(content):
    """Return content with ALL claisum-related lines stripped out."""
    lines = content.splitlines(keepends=True)
    cleaned = [l for l in lines if MARKER not in l and "[Claisum]" not in l]
    return "".join(cleaned).lstrip("\n")


def do_remove(idx):
    with open(idx, "r", encoding="utf-8") as f:
        raw = f.read()
    if MARKER not in raw and "[Claisum]" not in raw:
        return False
    cleaned = do_remove_str(raw)
    with open(idx, "w", encoding="utf-8") as f:
        f.write(cleaned)
    return True


def kill_discord():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "Discord.exe"], capture_output=True)
    except Exception:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Claisum Installer  v{VERSION}")
        self.geometry("555x420")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._dark_titlebar()
        self._setup_styles()
        self.action = tk.StringVar(value="install")
        self._page  = ""
        self._rows  = {}
        self._build_chrome()
        self._show("license")

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"555x420+{(sw-555)//2}+{(sh-420)//2}")

    def _dark_titlebar(self):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        except Exception:
            pass

    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('D.Vertical.TScrollbar',
                    background=BG4, troughcolor=BG2,
                    arrowcolor=DIM, bordercolor=BG2, relief='flat')
        s.map('D.Vertical.TScrollbar', background=[('active', '#555860')])

    def _build_chrome(self):
        hdr = tk.Frame(self, bg=BG2, height=50)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=" CL ", bg=ACCENT, fg="#fff",
                 font=("Courier", 12, "bold")).pack(side="left", padx=14, pady=12)
        tk.Label(hdr, text=f"Claisum Installer  v{VERSION}",
                 bg=BG2, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Frame(self, bg="#0a0a0c", height=1).pack(side="top", fill="x")

        tk.Frame(self, bg=BG4, height=1).pack(side="bottom", fill="x")
        self.foot = tk.Frame(self, bg=BG2, height=56)
        self.foot.pack(side="bottom", fill="x")
        self.foot.pack_propagate(False)

        for txt, url in [("Web", "https://github.com/claisum/Claisum.py"),
                          ("GitHub", "https://github.com/claisum/Claisum.py"),
                          ("Star", "https://github.com/claisum/Claisum.py/stargazers")]:
            lbl = tk.Label(self.foot, text=txt, bg=BG2, fg=DIM,
                           font=("Segoe UI", 8), cursor="hand2")
            lbl.pack(side="left", padx=(10, 2), pady=18)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        self.btn_next = tk.Button(
            self.foot, text="Next", bg=ACCENT, fg="#fff",
            bd=0, relief="flat", font=("Segoe UI", 10, "bold"),
            padx=24, pady=7, cursor="hand2", command=self._next)
        self.btn_next.pack(side="right", padx=(4, 14), pady=10)

        self.btn_back = tk.Button(
            self.foot, text="Back", bg=BG3, fg=TEXT,
            bd=0, relief="flat", font=("Segoe UI", 10, "bold"),
            padx=24, pady=7, cursor="hand2", state="disabled",
            command=self._back)
        self.btn_back.pack(side="right", padx=4, pady=10)

        self.body = tk.Frame(self, bg=BG)
        self.body.pack(side="top", fill="both", expand=True)

    def _show(self, page):
        try:
            for w in self.body.winfo_children():
                w.destroy()
            self.body.update()
            self._page = page
            {"license": self._page_license,
             "action":  self._page_action,
             "progress":self._page_progress,
             "done":    self._page_done}[page]()
            self.body.update()
        except Exception:
            messagebox.showerror("Installer Error", traceback.format_exc())

    def _next(self):
        try:
            nxt = {"license":"action","action":"progress","done":"_exit"}.get(self._page)
            if nxt == "_exit":
                self.destroy(); return
            if nxt:
                self._show(nxt)
        except Exception:
            messagebox.showerror("Installer Error", traceback.format_exc())

    def _back(self):
        try:
            prv = {"action":"license","done":"action"}.get(self._page)
            if prv:
                self._show(prv)
        except Exception:
            messagebox.showerror("Installer Error", traceback.format_exc())

    def _hdr(self, badge, title):
        f = tk.Frame(self.body, bg=BG, padx=24)
        f.pack(fill="x", pady=(14, 8))
        tk.Label(f, text=f" {badge} ", bg=ACCENT, fg="#fff",
                 font=("Courier", 9, "bold")).pack(side="left", padx=(0, 10))
        tk.Label(f, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")

    def _page_license(self):
        self.btn_back.configure(state="disabled", fg=DIM)
        self.btn_next.configure(text="Next", bg=ACCENT, fg="#fff",
                                state="normal", command=self._next)
        self._hdr("EULA", "License Agreement")

        wrap = tk.Frame(self.body, bg=BG3)
        wrap.pack(fill="both", expand=True, padx=24, pady=(0, 0))
        sb = ttk.Scrollbar(wrap, orient="vertical", style='D.Vertical.TScrollbar')
        txt = tk.Text(wrap, bg=BG3, fg="#adb1b8", font=("Segoe UI", 9),
                      bd=0, relief="flat", wrap="word", padx=12, pady=10,
                      yscrollcommand=sb.set, cursor="arrow", selectbackground=BG4)
        sb.configure(command=txt.yview)
        sb.pack(side="right", fill="y", pady=1, padx=(0, 1))
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", EULA)
        txt.configure(state="disabled")
        txt.bind("<MouseWheel>",
                 lambda e: txt.yview_scroll(int(-1*(e.delta/120)), "units"))

        note = tk.Frame(self.body, bg=BG, padx=24)
        note.pack(fill="x", pady=(8, 14))
        tk.Label(note, text="Click Next to accept and continue.",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w")

    def _page_action(self):
        self.btn_back.configure(state="normal", fg=TEXT)
        self.btn_next.configure(text="Next", bg=ACCENT, fg="#fff",
                                state="normal", command=self._next)
        self._hdr("ACT", "Choose an Action")

        self._rows = {}
        actions = [
            ("install",   "+", "Install Claisum",   "Inject Claisum into your Discord"),
            ("repair",    "~", "Repair Claisum",    "Re-inject if Claisum stopped working"),
            ("uninstall", "x", "Uninstall Claisum", "Remove Claisum completely"),
        ]
        for val, badge, label, sub in actions:
            row = tk.Frame(self.body, bg=BG3, cursor="hand2")
            row.pack(fill="x", padx=24, pady=3)
            inner = tk.Frame(row, bg=BG3)
            inner.pack(fill="both", padx=12, pady=10)
            bw = tk.Label(inner, text=f"[{badge}]", bg=BG4, fg=DIM,
                          font=("Courier", 11, "bold"), width=4)
            bw.pack(side="left", padx=(0, 10))
            tf = tk.Frame(inner, bg=BG3)
            tf.pack(side="left", fill="x", expand=True)
            nl = tk.Label(tf, text=label, bg=BG3, fg=TEXT,
                          font=("Segoe UI", 11, "bold"), anchor="w")
            nl.pack(anchor="w")
            sl = tk.Label(tf, text=sub, bg=BG3, fg=DIM,
                          font=("Segoe UI", 9), anchor="w")
            sl.pack(anchor="w")
            self._rows[val] = (row, inner, bw, tf, nl, sl)
            for w in [row, inner, bw, tf, nl, sl]:
                w.bind("<Button-1>", lambda e, v=val: self._sel(v))

        self._sel("install")

    def _sel(self, val):
        self.action.set(val)
        for v, (row, inner, bw, tf, nl, sl) in self._rows.items():
            on  = (v == val)
            bg  = ACCENT if on else BG3
            fg  = "#fff"   if on else TEXT
            dfg = "#c5caff" if on else DIM
            bbg = "#4752c4" if on else BG4
            bfg = "#fff"   if on else DIM
            for w in [row, inner, tf]:
                w.configure(bg=bg)
            bw.configure(bg=bbg, fg=bfg)
            nl.configure(bg=bg, fg=fg)
            sl.configure(bg=bg, fg=dfg)

    def _page_progress(self):
        self.btn_back.configure(state="disabled", fg=DIM)
        self.btn_next.configure(bg="#3a3c40", fg=DIM, state="disabled")
        act = self.action.get()
        titles = {"install":"Installing...","repair":"Repairing...","uninstall":"Uninstalling..."}
        self._hdr(">>", titles.get(act, "Working..."))
        self._status_lbl = tk.Label(self.body, text="Starting...",
                                    bg=BG, fg=DIM, font=("Segoe UI", 9), padx=24)
        self._status_lbl.pack(anchor="w", pady=(0, 8))
        pb_wrap = tk.Frame(self.body, bg=BG3, height=6)
        pb_wrap.pack(fill="x", padx=24)
        self._pb = tk.Frame(pb_wrap, bg=ACCENT, height=6)
        self._pb.place(relwidth=0.0, relheight=1)
        threading.Thread(target=self._worker, daemon=True).start()

    def _upd(self, msg, p=None):
        def _do():
            try:
                self._status_lbl.configure(text=msg)
                if p is not None:
                    self._pb.place(relwidth=p, relheight=1)
            except Exception:
                pass
        self.after(0, _do)

    def _worker(self):
        try:
            if self.action.get() in ("install", "repair"):
                self._do_install()
            else:
                self._do_uninstall()
        except Exception as ex:
            err = traceback.format_exc()
            self.after(0, lambda: self._finish(False, str(ex) + "\n\n" + err[:300]))

    def _do_install(self):
        self._upd("Closing Discord...", 0.08); kill_discord()
        self._upd("Locating Discord...", 0.25)
        idx = find_discord()
        if not idx:
            raise RuntimeError(
                "Discord not found.\n"
                "Please install Discord from https://discord.com first.")
        core = os.path.dirname(idx)
        dest = os.path.join(core, "claisum_inject.js")
        self._upd("Copying files...", 0.50)
        src = get_inject_src()
        if src:
            shutil.copy2(src, dest)
        else:
            urllib.request.urlretrieve(
                f"https://raw.githubusercontent.com/{REPO}"
                "/main/claisum/discord/claisum_inject.js", dest)
        self._upd("Patching Discord...", 0.80)
        do_inject(idx)
        self._upd("Done!", 1.0)
        self.after(400, lambda: self._finish(True,
            "Claisum installed!\n\n"
            "Restart Discord. You will see a \u26a1 button in the\n"
            "bottom-left corner. Click it to open Claisum settings.\n\n"
            "Claisum auto-updates on every Discord start."))

    def _do_uninstall(self):
        self._upd("Closing Discord...", 0.10); kill_discord()
        self._upd("Locating Discord...", 0.35)
        idx = find_discord()
        if not idx:
            raise RuntimeError("Discord not found.")
        dest = os.path.join(os.path.dirname(idx), "claisum_inject.js")
        self._upd("Removing injection...", 0.65)
        do_remove(idx)                 # removes all lines mentioning claisum
        self._upd("Removing files...", 0.85)
        try:
            os.remove(dest)
        except FileNotFoundError:
            pass
        self._upd("Done!", 1.0)
        self.after(400, lambda: self._finish(True,
            "Claisum removed.\n\n"
            "Discord has been restored to its original state.\n"
            "Your theme and plugin preferences are kept in Discord's\n"
            "local storage and will not affect Discord without Claisum."))

    def _finish(self, ok, msg):
        self._done_ok  = ok
        self._done_msg = msg
        self._show("done")

    def _page_done(self):
        ok  = getattr(self, "_done_ok",  True)
        msg = getattr(self, "_done_msg", "")
        self.btn_back.configure(state="disabled", fg=DIM)
        self.btn_next.configure(text="Finish", bg=ACCENT, fg="#fff",
                                state="normal", command=self._next)
        self._hdr("OK" if ok else "!!", "Done!" if ok else "Error")
        tk.Label(self.body, text=msg,
                 bg=BG, fg=TEXT if ok else ERR,
                 font=("Segoe UI", 9),
                 wraplength=490, justify="left", padx=24).pack(anchor="w", pady=4)


if __name__ == "__main__":
    App().mainloop()
