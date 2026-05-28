import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, sys, shutil, threading, glob, ctypes, subprocess, time

BG      = "#1e1e2e"
BG2     = "#181825"
BG3     = "#313244"
ACCENT  = "#7c6af7"
ACCENT2 = "#6c5ce7"
TEXT    = "#cdd6f4"
DIM     = "#6c7086"
OK      = "#a6e3a1"
ERR     = "#f38ba8"
WARN    = "#fab387"

W, H    = 620, 460
STEPS   = ["Welcome", "Checks", "Options", "Install", "Done"]

INSTALL_DEFAULT = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Claisum")

CONFLICTS = {
    "Vencord":       [os.path.join(os.environ.get("APPDATA",""), "Vencord"),
                      os.path.join(os.environ.get("LOCALAPPDATA",""),
                                   "Programs", "Vencord")],
    "BetterDiscord": [os.path.join(os.environ.get("APPDATA",""), "BetterDiscord")],
    "Moonlight":     [os.path.join(os.environ.get("APPDATA",""), "Moonlight")],
}


def resource(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def find_discord():
    local = os.environ.get("LOCALAPPDATA", "")
    for pat in [os.path.join(local, "Discord", "app-*", "Discord.exe"),
                os.path.join(local, "DiscordPTB", "app-*", "DiscordPTB.exe"),
                os.path.join(local, "DiscordCanary", "app-*", "DiscordCanary.exe")]:
        hits = sorted(glob.glob(pat), reverse=True)
        if hits:
            return hits[0]
    return None


def find_discord_core():
    """Find Discord's core index.js to patch."""
    local = os.environ.get("LOCALAPPDATA", "")
    for variant in ["Discord", "DiscordPTB", "DiscordCanary"]:
        base = os.path.join(local, variant)
        if not os.path.isdir(base):
            continue
        for app_dir in sorted(glob.glob(os.path.join(base, "app-*")), reverse=True):
            core = os.path.join(app_dir, "modules",
                                "discord_desktop_core-1",
                                "discord_desktop_core", "index.js")
            if os.path.isfile(core):
                return core
    return None


def inject_claisum(inject_js_path):
    """Patch Discord's index.js to load claisum_inject.js."""
    marker = "// [Claisum Injected]"
    core = find_discord_core()
    if not core:
        return False, "Discord core not found"

    try:
        with open(core, "r", encoding="utf-8") as f:
            content = f.read()
        if marker in content:
            return True, "already injected"

        core_dir = os.path.dirname(core)
        inject_dst = os.path.join(core_dir, "claisum_inject.js")
        shutil.copy2(inject_js_path, inject_dst)

        loader = f"""
{marker}
try {{
  const fs = require('fs');
  const path = require('path');
  const js = fs.readFileSync(path.join(__dirname, 'claisum_inject.js'), 'utf8');
  window.addEventListener('load', () => {{
    setTimeout(() => {{ try {{ eval(js); }} catch(e) {{ console.error('[Claisum]', e); }} }}, 2000);
  }});
}} catch(e) {{ console.error('[Claisum preload]', e); }}
"""
        with open(core, "a", encoding="utf-8") as f:
            f.write(loader)
        return True, core
    except PermissionError:
        return False, "Permission denied — run as Administrator"
    except Exception as e:
        return False, str(e)


def add_to_path(directory):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Environment", 0, winreg.KEY_ALL_ACCESS)
        cur, _ = winreg.QueryValueEx(key, "PATH")
        if directory.lower() not in cur.lower():
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ,
                              cur + ";" + directory)
        winreg.CloseKey(key)
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None)
        return True
    except Exception:
        return False


def register_uninstall(idir):
    try:
        import winreg
        k = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Claisum")
        for name, typ, val in [
            ("DisplayName",     winreg.REG_SZ,    "Claisum"),
            ("DisplayVersion",  winreg.REG_SZ,    "0.2.0"),
            ("Publisher",       winreg.REG_SZ,    "Claisum"),
            ("InstallLocation", winreg.REG_SZ,    idir),
            ("UninstallString", winreg.REG_SZ,    os.path.join(idir, "uninstall.bat")),
            ("NoModify",        winreg.REG_DWORD,  1),
            ("NoRepair",        winreg.REG_DWORD,  1),
        ]:
            winreg.SetValueEx(k, name, 0, typ, val)
        winreg.CloseKey(k)
    except Exception:
        pass
    try:
        with open(os.path.join(idir, "uninstall.bat"), "w") as f:
            f.write(f'@echo off\nrmdir /s /q "{idir}"\n'
                    r'reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion'
                    r'\Uninstall\Claisum" /f' + '\npause\n')
    except Exception:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Claisum Setup")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.step         = 0
        self.conflicts    = []
        self.install_dir  = tk.StringVar(value=INSTALL_DEFAULT)
        self.restart_disc = tk.BooleanVar(value=True)
        self._labels      = []
        self._build()
        self._goto(0)

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _close(self):
        if self.step == 3 and not messagebox.askyesno(
                "Cancel?", "Installation is running. Quit anyway?"):
            return
        self.destroy()

    def _build(self):
        bot = tk.Frame(self, bg=BG2, height=56)
        bot.pack(side="bottom", fill="x")
        bot.pack_propagate(False)

        self.btn_back = tk.Button(bot, text="← Back", bg=BG2, fg=DIM, relief="flat",
            font=("Segoe UI", 10), activebackground=BG2, activeforeground=TEXT,
            command=self._back, padx=16, pady=6, bd=0, cursor="hand2")
        self.btn_back.pack(side="left", padx=16, pady=10)

        self.btn_next = tk.Button(bot, text="Next →", bg=ACCENT, fg="#ffffff", relief="flat",
            font=("Segoe UI", 10, "bold"), activebackground=ACCENT2, activeforeground="#ffffff",
            command=self._next, padx=22, pady=6, bd=0, cursor="hand2")
        self.btn_next.pack(side="right", padx=16, pady=10)

        sb = tk.Frame(self, bg=BG2, width=168)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="CLAISUM", bg=BG2, fg=ACCENT,
                 font=("Segoe UI", 15, "bold")).pack(pady=(28, 2))
        tk.Label(sb, text="Setup v0.2.0", bg=BG2, fg=DIM,
                 font=("Segoe UI", 8)).pack()
        tk.Frame(sb, bg=BG3, height=1).pack(fill="x", padx=18, pady=16)

        for name in STEPS:
            lbl = tk.Label(sb, text=f"  {name}", bg=BG2, fg=DIM,
                           font=("Segoe UI", 10), anchor="w")
            lbl.pack(fill="x", padx=8, pady=2)
            self._labels.append(lbl)

        self.area = tk.Frame(self, bg=BG)
        self.area.pack(side="left", fill="both", expand=True)

    def _refresh_sidebar(self):
        for i, lbl in enumerate(self._labels):
            if i < self.step:
                lbl.config(fg=OK, text=f"  ✓ {STEPS[i]}", font=("Segoe UI", 10))
            elif i == self.step:
                lbl.config(fg=ACCENT, text=f"  ▶ {STEPS[i]}", font=("Segoe UI", 10, "bold"))
            else:
                lbl.config(fg=DIM, text=f"  {STEPS[i]}", font=("Segoe UI", 10))

    def _clear(self):
        for w in self.area.winfo_children():
            w.destroy()

    def _goto(self, n):
        self.step = n
        self._refresh_sidebar()
        self._clear()
        [self._welcome, self._checks, self._page_options,
         self._installing, self._done][n]()

    def _next(self):
        if self.step == 0:
            self._goto(1); self._run_checks()
        elif self.step == 1:
            if self.conflicts and not messagebox.askyesno(
                    "Conflicts found",
                    f"Found: {', '.join(self.conflicts)}\n\nThese may conflict with Claisum.\nContinue anyway?"):
                return
            self._goto(2)
        elif self.step == 2:
            self._goto(3); self._do_install()
        elif self.step == 4:
            self.destroy()

    def _back(self):
        if self.step in (1, 2):
            self._goto(self.step - 1)

    def _frame(self):
        f = tk.Frame(self.area, bg=BG)
        f.pack(fill="both", expand=True, padx=36, pady=24)
        return f

    def _heading(self, parent, title, sub=""):
        tk.Label(parent, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        if sub:
            tk.Label(parent, text=sub, bg=BG, fg=DIM,
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 18))

    def _welcome(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="normal", text="Next →", bg=ACCENT)
        f = self._frame()
        self._heading(f, "Welcome to Claisum Setup", "Discord Theme & Plugin Manager")
        for text, color, weight in [
            ("This installer will:", TEXT, "bold"),
            ("  • Inject Claisum into Discord", OK, ""),
            ("  • Add Themes and Plugins tabs to Discord Settings", OK, ""),
            ("  • Let you install, create and publish themes & plugins", OK, ""),
            ("  • Restart Discord when done", OK, ""),
            ("", DIM, ""),
            ("No Python, Git or anything else required.", TEXT, ""),
            ("Just double-clicked and done!", DIM, ""),
        ]:
            font = ("Segoe UI", 10, weight) if weight else ("Segoe UI", 10)
            tk.Label(f, text=text, bg=BG, fg=color, font=font, anchor="w").pack(fill="x", pady=1)

    def _checks(self):
        self.btn_back.config(state="normal")
        self.btn_next.config(state="disabled", bg=BG3, text="Next →")
        f = self._frame()
        self._heading(f, "System Check", "Checking your system before installation…")
        self._chk = {}
        for key in ["No conflicting mods", "Discord is installed", "Installer files OK"]:
            row = tk.Frame(f, bg=BG); row.pack(fill="x", pady=6)
            dot = tk.Label(row, text="○", bg=BG, fg=DIM, font=("Segoe UI", 13))
            dot.pack(side="left", padx=(0, 12))
            tk.Label(row, text=key, bg=BG, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
            note = tk.Label(row, text="…", bg=BG, fg=DIM, font=("Segoe UI", 9))
            note.pack(side="right")
            self._chk[key] = (dot, note)
        self._chk_msg = tk.Label(f, text="", bg=BG, fg=WARN, font=("Segoe UI", 9),
                                  wraplength=370, justify="left")
        self._chk_msg.pack(anchor="w", pady=(14, 0))

    def _set_chk(self, key, good, note=""):
        dot, lbl = self._chk[key]
        dot.config(text="✓" if good else "⚠", fg=OK if good else WARN)
        lbl.config(text=note, fg=OK if good else WARN)

    def _run_checks(self):
        def worker():
            msgs = []
            found = [m for m, paths in CONFLICTS.items()
                     if any(os.path.isdir(p) for p in paths)]
            self.conflicts = found
            if found:
                self.after(0, self._set_chk, "No conflicting mods", False, ", ".join(found))
                msgs.append(f"⚠ Detected: {', '.join(found)}")
            else:
                self.after(0, self._set_chk, "No conflicting mods", True, "Clear")
            disc = find_discord()
            if disc:
                self.after(0, self._set_chk, "Discord is installed", True,
                           os.path.basename(os.path.dirname(disc)))
            else:
                self.after(0, self._set_chk, "Discord is installed", False, "Not found")
                msgs.append("⚠ Discord not found — install Discord first.")
            bundled = resource("claisum_inject.js")
            if os.path.isfile(bundled):
                self.after(0, self._set_chk, "Installer files OK", True, "Ready")
            else:
                self.after(0, self._set_chk, "Installer files OK", False, "claisum_inject.js missing")
                msgs.append("⚠ Installer bundle is incomplete.")
            self.after(0, self._chk_msg.config, {"text": "\n".join(msgs)})
            self.after(0, self.btn_next.config, {"state": "normal", "bg": ACCENT})
        threading.Thread(target=worker, daemon=True).start()

    def _page_options(self):
        self.btn_back.config(state="normal")
        self.btn_next.config(state="normal", text="Install →", bg=ACCENT)
        f = self._frame()
        self._heading(f, "Installation Options", "Choose where to save Claisum files.")
        tk.Label(f, text="Install location", bg=BG, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row = tk.Frame(f, bg=BG); row.pack(fill="x", pady=(4, 16))
        tk.Entry(row, textvariable=self.install_dir, bg=BG2, fg=TEXT,
                 insertbackground=TEXT, relief="flat",
                 font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))
        tk.Button(row, text="Browse…", bg=BG3, fg=TEXT, relief="flat",
                  font=("Segoe UI", 9), bd=0, cursor="hand2",
                  command=self._browse).pack(side="right", ipady=4, ipadx=10)
        tk.Checkbutton(f, text="Restart Discord after installation",
                       variable=self.restart_disc, bg=BG, fg=TEXT,
                       selectcolor=BG2, activebackground=BG, activeforeground=TEXT,
                       font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 4))

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.install_dir.get())
        if d:
            self.install_dir.set(d)

    def _installing(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="disabled", bg=BG3)
        f = self._frame()
        self._heading(f, "Installing…")
        self._st = tk.Label(f, text="Starting…", bg=BG, fg=DIM, font=("Segoe UI", 9))
        self._st.pack(anchor="w", pady=(0, 10))
        style = ttk.Style(self); style.theme_use("clam")
        style.configure("C.Horizontal.TProgressbar",
                        troughcolor=BG2, background=ACCENT, thickness=6)
        self._pb = ttk.Progressbar(f, style="C.Horizontal.TProgressbar",
                                    mode="indeterminate", length=400)
        self._pb.pack(fill="x"); self._pb.start(10)
        self._log = tk.Text(f, bg=BG2, fg=DIM, font=("Consolas", 8),
                             relief="flat", height=10, state="disabled", wrap="word")
        self._log.pack(fill="x", pady=(12, 0))

    def _log_line(self, text, tag="d"):
        def _do():
            self._log.config(state="normal")
            for t, c in [("ok", OK), ("er", ERR), ("w", WARN), ("d", DIM)]:
                self._log.tag_config(t, foreground=c)
            self._log.insert("end", text + "\n", tag)
            self._log.see("end"); self._log.config(state="disabled")
        self.after(0, _do)

    def _setstatus(self, t):
        self.after(0, self._st.config, {"text": t})

    def _do_install(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            idir = self.install_dir.get()
            self._setstatus("Creating install directory…")
            os.makedirs(idir, exist_ok=True)
            self._log_line(f"→ Location: {idir}")

            self._setstatus("Copying Claisum files…")
            for fname in ["claisum_inject.js"]:
                src = resource(fname)
                dst = os.path.join(idir, fname)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    self._log_line(f"✓ Copied {fname}", "ok")

            self._setstatus("Injecting into Discord…")
            inject_js = os.path.join(idir, "claisum_inject.js")
            ok, msg = inject_claisum(inject_js)
            if ok:
                self._log_line("✓ Claisum injected into Discord", "ok")
                self._log_line("  → Themes & Plugins tabs added to Discord Settings", "ok")
            else:
                self._log_line(f"⚠ Injection: {msg}", "w")

            register_uninstall(idir)
            self._log_line("✓ Registered in Add/Remove Programs", "ok")

            if self.restart_disc.get():
                self._setstatus("Restarting Discord…")
                self._log_line("→ Restarting Discord…")
                for proc in ("Discord.exe", "DiscordPTB.exe", "DiscordCanary.exe"):
                    subprocess.run(["taskkill", "/F", "/IM", proc], capture_output=True)
                time.sleep(2)
                disc = find_discord()
                if disc:
                    subprocess.Popen([disc])
                    self._log_line("✓ Discord restarted", "ok")
                else:
                    self._log_line("⚠ Start Discord manually", "w")

            self._log_line("─────────────────────────────────────", "ok")
            self._log_line("  Claisum is ready!", "ok")
            self._log_line("  Open Discord → Settings → Themes or Plugins", "ok")
            self.after(0, self._pb.stop)
            self.after(0, self._pb.config, {"mode": "determinate", "value": 100})
            self._setstatus("Installation complete!")
            self.after(800, self._goto, 4)
        except Exception as e:
            self._log_line(f"✗ {e}", "er")
            self._setstatus("Installation failed.")
            self.after(0, self._pb.stop)
            self.after(0, messagebox.showerror, "Error", f"Failed:\n{e}\n\nTry running as Administrator.")

    def _done(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="normal", text="Finish", bg=OK, fg=BG)
        f = self._frame()
        tk.Label(f, text="✓", bg=BG, fg=OK, font=("Segoe UI", 44)).pack(pady=(0, 8))
        tk.Label(f, text="Claisum installed!", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(f, text="Open Discord and go to Settings", bg=BG, fg=DIM,
                 font=("Segoe UI", 11)).pack(pady=(14, 4))
        tk.Label(f, text="You'll find  🎨 Themes  and  🔌 Plugins  tabs there.", bg=BG, fg=TEXT,
                 font=("Segoe UI", 11)).pack()
        tk.Label(f, text="Browse themes, enable plugins, create your own and publish for others!",
                 bg=BG, fg=DIM, font=("Segoe UI", 9), wraplength=360).pack(pady=(10, 0))
        tk.Label(f, text="Uninstall anytime via Add/Remove Programs.",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(pady=(14, 0))


if __name__ == "__main__":
    app = App()
    app.mainloop()
