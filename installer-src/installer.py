import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
import threading
import glob
import ctypes
import subprocess
import time

# ── Theme ─────────────────────────────────────────────────────────────────────
BG       = "#1e1e2e"
BG2      = "#181825"
BG3      = "#313244"
ACCENT   = "#7c6af7"
ACCENT2  = "#6c5ce7"
TEXT     = "#cdd6f4"
DIM      = "#6c7086"
SUCCESS  = "#a6e3a1"
ERROR    = "#f38ba8"
WARNING  = "#fab387"
WIDTH, HEIGHT = 620, 460

STEPS = ["Welcome", "Checks", "Options", "Install", "Done"]

INSTALL_DIR_DEFAULT = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Claisum")

CONFLICTING = {
    "Vencord":       [os.path.join(os.environ.get("APPDATA",""), "Vencord"),
                      os.path.join(os.environ.get("LOCALAPPDATA",""),
                                   "Programs","Vencord")],
    "BetterDiscord": [os.path.join(os.environ.get("APPDATA",""),
                                   "BetterDiscord")],
    "Moonlight":     [os.path.join(os.environ.get("APPDATA",""), "Moonlight")],
    "Powercord":     [os.path.join(os.environ.get("APPDATA",""), "powercord")],
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def resource(name):
    """Locate a bundled file (works in PyInstaller .exe and dev mode)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def find_discord_exe():
    local = os.environ.get("LOCALAPPDATA", "")
    patterns = [
        os.path.join(local, "Discord", "app-*", "Discord.exe"),
        os.path.join(local, "DiscordPTB", "app-*", "DiscordPTB.exe"),
        os.path.join(local, "DiscordCanary", "app-*", "DiscordCanary.exe"),
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat), reverse=True)
        if hits:
            return hits[0]
    return None


def add_to_path_registry(directory):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Environment", 0, winreg.KEY_ALL_ACCESS)
        current, _ = winreg.QueryValueEx(key, "PATH")
        if directory.lower() not in current.lower():
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ,
                              current + ";" + directory)
        winreg.CloseKey(key)
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None)
        return True
    except Exception:
        return False


def register_uninstaller(install_dir):
    try:
        import winreg
        key_path = (r"Software\Microsoft\Windows\CurrentVersion"
                    r"\Uninstall\Claisum")
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "DisplayName",        0, winreg.REG_SZ, "Claisum")
        winreg.SetValueEx(key, "DisplayVersion",     0, winreg.REG_SZ, "0.1.0")
        winreg.SetValueEx(key, "Publisher",          0, winreg.REG_SZ, "Claisum")
        winreg.SetValueEx(key, "InstallLocation",    0, winreg.REG_SZ, install_dir)
        uninstaller = os.path.join(install_dir, "uninstall.bat")
        winreg.SetValueEx(key, "UninstallString",    0, winreg.REG_SZ, uninstaller)
        winreg.SetValueEx(key, "NoModify",           0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair",           0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except Exception:
        pass


def write_uninstaller(install_dir):
    content = (
        "@echo off\n"
        f'rmdir /s /q "{install_dir}"\n'
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion'
        '\\Uninstall\\Claisum" /f\n'
        'echo Claisum uninstalled.\npause\n'
    )
    try:
        with open(os.path.join(install_dir, "uninstall.bat"), "w") as f:
            f.write(content)
    except Exception:
        pass


# ── App ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Claisum Setup")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center(WIDTH, HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.step       = 0
        self.conflicts  = []
        self.install_dir = tk.StringVar(value=INSTALL_DIR_DEFAULT)
        self.restart_discord = tk.BooleanVar(value=True)

        self._build_chrome()
        self._goto(0)

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _close(self):
        if self.step == 3:
            if not messagebox.askyesno("Cancel?",
                    "Installation is running. Quit anyway?"):
                return
        self.destroy()

    # ── Chrome ────────────────────────────────────────────────────────────────
    def _build_chrome(self):
        # Sidebar
        sb = tk.Frame(self, bg=BG2, width=170)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="CLAISUM", bg=BG2, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(pady=(30, 2))
        tk.Label(sb, text="Setup v0.1.0", bg=BG2, fg=DIM,
                 font=("Segoe UI", 8)).pack()
        tk.Frame(sb, bg=BG3, height=1).pack(fill="x", padx=18, pady=18)

        self._step_lbls = []
        for name in STEPS:
            lbl = tk.Label(sb, text=f"  {name}", bg=BG2, fg=DIM,
                           font=("Segoe UI", 10), anchor="w")
            lbl.pack(fill="x", padx=8, pady=2)
            self._step_lbls.append(lbl)

        # Content
        self.canvas = tk.Frame(self, bg=BG)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bottom
        bot = tk.Frame(self, bg=BG2, height=54)
        bot.pack(side="bottom", fill="x")
        bot.pack_propagate(False)

        self.btn_back = tk.Button(
            bot, text="← Back", bg=BG, fg=DIM, relief="flat",
            font=("Segoe UI", 10), activebackground=BG,
            activeforeground=TEXT, command=self._back, padx=16, pady=6)
        self.btn_back.pack(side="left", padx=14, pady=10)

        self.btn_next = tk.Button(
            bot, text="Next →", bg=ACCENT, fg="#fff", relief="flat",
            font=("Segoe UI", 10, "bold"), activebackground=ACCENT2,
            activeforeground="#fff", command=self._next, padx=20, pady=6)
        self.btn_next.pack(side="right", padx=14, pady=10)

    def _refresh_steps(self):
        for i, lbl in enumerate(self._step_lbls):
            if i < self.step:
                lbl.config(fg=SUCCESS, text=f"  ✓ {STEPS[i]}",
                           font=("Segoe UI", 10))
            elif i == self.step:
                lbl.config(fg=ACCENT, text=f"  ▶ {STEPS[i]}",
                           font=("Segoe UI", 10, "bold"))
            else:
                lbl.config(fg=DIM, text=f"  {STEPS[i]}",
                           font=("Segoe UI", 10))

    def _clear(self):
        for w in self.canvas.winfo_children():
            w.destroy()

    def _goto(self, n):
        self.step = n
        self._refresh_steps()
        self._clear()
        [self._p_welcome, self._p_checks, self._p_options,
         self._p_install, self._p_done][n]()

    def _next(self):
        if self.step == 0:
            self._goto(1)
            self._run_checks()
        elif self.step == 1:
            if self.conflicts:
                if not messagebox.askyesno("Conflicts found",
                        f"Found: {', '.join(self.conflicts)}\n\n"
                        "These mods may conflict with Claisum.\n"
                        "Continue anyway?"):
                    return
            self._goto(2)
        elif self.step == 2:
            self._goto(3)
            self._do_install()
        elif self.step == 4:
            self.destroy()

    def _back(self):
        if self.step in (1, 2):
            self._goto(self.step - 1)

    # ── Page 0 — Welcome ─────────────────────────────────────────────────────
    def _p_welcome(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="normal", text="Next →", bg=ACCENT, fg="#fff")

        f = self._frame()
        tk.Label(f, text="Welcome to Claisum Setup", bg=BG, fg=TEXT,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(f, text="Discord Theme & Plugin Manager  •  No dependencies required",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 22))

        for line in [
            "This installer will:",
            "  • Copy claisum.exe to your computer",
            "  • Add it to your PATH automatically",
            "  • Register it in Add/Remove Programs",
            "  • Restart Discord when done",
            "",
            "You do not need Python, Git or any other tool.",
            "Just click Next.",
        ]:
            tk.Label(f, text=line, bg=BG,
                     fg=TEXT if line and not line.startswith("  ") else
                        (DIM if line == "" else SUCCESS),
                     font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=1)

    # ── Page 1 — Checks ──────────────────────────────────────────────────────
    def _p_checks(self):
        self.btn_back.config(state="normal")
        self.btn_next.config(state="disabled", bg=DIM)

        f = self._frame()
        tk.Label(f, text="System check", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(f, text="Checking your system before installation…",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(3,18))

        self._chk = {}
        for key in ["No conflicting mods", "Discord is installed",
                     "Installer files OK"]:
            row = tk.Frame(f, bg=BG)
            row.pack(fill="x", pady=5)
            dot = tk.Label(row, text="○", bg=BG, fg=DIM,
                           font=("Segoe UI", 12))
            dot.pack(side="left", padx=(0,10))
            tk.Label(row, text=key, bg=BG, fg=TEXT,
                     font=("Segoe UI", 10)).pack(side="left")
            note = tk.Label(row, text="…", bg=BG, fg=DIM,
                            font=("Segoe UI", 9))
            note.pack(side="right")
            self._chk[key] = (dot, note)

        self._chk_note = tk.Label(f, text="", bg=BG, fg=WARNING,
                                  font=("Segoe UI", 9),
                                  wraplength=380, justify="left")
        self._chk_note.pack(anchor="w", pady=(16,0))

    def _set_chk(self, key, ok, note=""):
        dot, lbl = self._chk[key]
        dot.config(text="✓" if ok else "⚠",
                   fg=SUCCESS if ok else WARNING)
        lbl.config(text=note, fg=SUCCESS if ok else WARNING)

    def _run_checks(self):
        def worker():
            msgs = []

            # Conflicts
            found = [m for m, paths in CONFLICTING.items()
                     if any(os.path.isdir(p) for p in paths)]
            self.conflicts = found
            if found:
                self.after(0, self._set_chk, "No conflicting mods", False,
                           ", ".join(found))
                msgs.append(f"⚠ Detected: {', '.join(found)}")
            else:
                self.after(0, self._set_chk, "No conflicting mods", True, "Clear")

            # Discord
            disc = find_discord_exe()
            if disc:
                self.after(0, self._set_chk, "Discord is installed",
                           True, os.path.basename(os.path.dirname(disc)))
            else:
                self.after(0, self._set_chk, "Discord is installed",
                           False, "Not found")
                msgs.append("⚠ Discord not found — install it first.")

            # Bundled EXE
            bundled = resource("claisum.exe")
            if os.path.isfile(bundled):
                size = os.path.getsize(bundled)
                self.after(0, self._set_chk, "Installer files OK",
                           True, f"{size//1024} KB")
            else:
                self.after(0, self._set_chk, "Installer files OK",
                           False, "claisum.exe missing from bundle")
                msgs.append("⚠ Installer bundle is incomplete.")

            self.after(0, self._chk_note.config,
                       {"text": "\n".join(msgs)})
            self.after(0, self.btn_next.config,
                       {"state": "normal", "bg": ACCENT})

        threading.Thread(target=worker, daemon=True).start()

    # ── Page 2 — Options ─────────────────────────────────────────────────────
    def _p_options(self):
        self.btn_back.config(state="normal")
        self.btn_next.config(state="normal", text="Install →",
                             bg=ACCENT, fg="#fff")

        f = self._frame()
        tk.Label(f, text="Installation options", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(f, text="Choose where to install Claisum.",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(3,20))

        # Install path
        tk.Label(f, text="Install location", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row = tk.Frame(f, bg=BG)
        row.pack(fill="x", pady=(4, 16))
        entry = tk.Entry(row, textvariable=self.install_dir,
                         bg=BG2, fg=TEXT, insertbackground=TEXT,
                         relief="flat", font=("Segoe UI", 9))
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))
        tk.Button(row, text="Browse", bg=BG3, fg=TEXT, relief="flat",
                  font=("Segoe UI", 9),
                  command=self._browse).pack(side="right", padx=0, ipady=4, ipadx=8)

        # Options
        tk.Label(f, text="Options", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        cb = tk.Checkbutton(f, text="Restart Discord after installation",
                            variable=self.restart_discord,
                            bg=BG, fg=TEXT, selectcolor=BG2,
                            activebackground=BG, activeforeground=TEXT,
                            font=("Segoe UI", 10))
        cb.pack(anchor="w", pady=(6, 4))

        tk.Label(f,
                 text="claisum.exe will be placed in the selected folder\n"
                      "and added to your PATH automatically.",
                 bg=BG, fg=DIM, font=("Segoe UI", 9),
                 justify="left").pack(anchor="w", pady=(14, 0))

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.install_dir.get())
        if d:
            self.install_dir.set(d)

    # ── Page 3 — Install ─────────────────────────────────────────────────────
    def _p_install(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="disabled", bg=DIM)

        f = self._frame()
        tk.Label(f, text="Installing…", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self._st = tk.Label(f, text="Starting…", bg=BG, fg=DIM,
                            font=("Segoe UI", 9))
        self._st.pack(anchor="w", pady=(4, 12))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("C.Horizontal.TProgressbar",
                        troughcolor=BG2, background=ACCENT,
                        thickness=6)
        self._pb = ttk.Progressbar(f, style="C.Horizontal.TProgressbar",
                                   mode="indeterminate", length=400)
        self._pb.pack(fill="x")
        self._pb.start(10)

        self._log = tk.Text(f, bg=BG2, fg=DIM, font=("Consolas", 8),
                            relief="flat", height=11, state="disabled",
                            wrap="word")
        self._log.pack(fill="x", pady=(14, 0))

    def _log_line(self, text, tag="d"):
        def _do():
            self._log.config(state="normal")
            self._log.tag_config("ok",  foreground=SUCCESS)
            self._log.tag_config("err", foreground=ERROR)
            self._log.tag_config("w",   foreground=WARNING)
            self._log.tag_config("d",   foreground=DIM)
            self._log.insert("end", text + "\n", tag)
            self._log.see("end")
            self._log.config(state="disabled")
        self.after(0, _do)

    def _setstatus(self, t):
        self.after(0, self._st.config, {"text": t})

    def _do_install(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            idir = self.install_dir.get()
            self._setstatus("Creating install directory…")
            self._log_line(f"→ Install location: {idir}")
            os.makedirs(idir, exist_ok=True)

            # Copy claisum.exe
            self._setstatus("Copying claisum.exe…")
            src = resource("claisum.exe")
            dst = os.path.join(idir, "claisum.exe")
            self._log_line(f"→ Copying claisum.exe to {dst}")
            shutil.copy2(src, dst)
            self._log_line(f"✓ Copied ({os.path.getsize(dst)//1024} KB)", "ok")

            # Write uninstaller
            write_uninstaller(idir)
            self._log_line("✓ Uninstaller written", "ok")

            # Register in Add/Remove Programs
            register_uninstaller(idir)
            self._log_line("✓ Registered in Add/Remove Programs", "ok")

            # Add to PATH
            self._setstatus("Updating PATH…")
            self._log_line(f"→ Adding {idir} to user PATH")
            ok = add_to_path_registry(idir)
            self._log_line("✓ PATH updated" if ok
                           else "⚠ Could not update PATH — add manually",
                           "ok" if ok else "w")

            # Restart Discord
            if self.restart_discord.get():
                self._setstatus("Restarting Discord…")
                self._log_line("→ Closing Discord…")
                subprocess.run(["taskkill", "/F", "/IM", "Discord.exe"],
                               capture_output=True)
                subprocess.run(["taskkill", "/F", "/IM", "DiscordPTB.exe"],
                               capture_output=True)
                time.sleep(2)
                disc_exe = find_discord_exe()
                if disc_exe:
                    subprocess.Popen([disc_exe])
                    self._log_line("✓ Discord restarted", "ok")
                else:
                    self._log_line("⚠ Discord not found — start manually", "w")

            self._setstatus("Done!")
            self._log_line("─────────────────────────", "ok")
            self._log_line("  claisum.exe is ready!   ", "ok")
            self._log_line(f"  Location: {dst}", "ok")
            self._log_line("  Open a NEW terminal and run: claisum --help", "ok")
            self.after(0, self._pb.stop)
            self.after(0, self._pb.config,
                       {"mode": "determinate", "value": 100})
            self.after(800, self._goto, 4)

        except Exception as e:
            self._log_line(f"✗ {e}", "err")
            self._setstatus("Installation failed.")
            self.after(0, self._pb.stop)
            self.after(0, messagebox.showerror, "Error",
                       f"Installation failed:\n{e}\n\n"
                       "Try running as Administrator.")

    # ── Page 4 — Done ────────────────────────────────────────────────────────
    def _p_done(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="normal", text="Finish",
                             bg=SUCCESS, fg=BG)

        f = self._frame()
        tk.Label(f, text="✓", bg=BG, fg=SUCCESS,
                 font=("Segoe UI", 42)).pack(pady=(0, 8))
        tk.Label(f, text="Claisum installed successfully!", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(f, text="Open a NEW terminal window and run:",
                 bg=BG, fg=DIM, font=("Segoe UI", 10)).pack(pady=(14, 6))

        cb = tk.Frame(f, bg=BG2)
        cb.pack(pady=2)
        tk.Label(cb, text="claisum --help", bg=BG2, fg=ACCENT,
                 font=("Consolas", 12), pady=8, padx=24).pack()

        for cmd in ["claisum discord themes list",
                    "claisum discord plugins available"]:
            tk.Label(f, text=cmd, bg=BG, fg=DIM,
                     font=("Consolas", 9)).pack(pady=2)

        tk.Label(f,
                 text="Discord was restarted.  "
                      "Uninstall via Add/Remove Programs.",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(pady=(18, 0))

    # ── Utility ───────────────────────────────────────────────────────────────
    def _frame(self):
        f = tk.Frame(self.canvas, bg=BG)
        f.pack(fill="both", expand=True, padx=38, pady=26)
        return f


if __name__ == "__main__":
    app = App()
    app.mainloop()
