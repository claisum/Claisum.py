"""Claisum Installer v1.0.0.1"""
import sys, os, glob, shutil, threading, subprocess, urllib.request, webbrowser
import tkinter as tk
from tkinter import ttk

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
PRELOAD = "// [Claisum Injected]"

EULA = (
    "End-User License Agreement for Claisum\n\n"
    "PLEASE READ THIS AGREEMENT CAREFULLY.\n\n"
    "By installing Claisum you agree to the following terms:\n\n"
    "1. Claisum is free, open-source software provided \"as is\" without warranty.\n"
    "2. You may not redistribute Claisum for commercial purposes.\n"
    "3. Claisum modifies Discord's local files; use at your own risk.\n"
    "4. The authors are not responsible for any Discord account actions.\n"
    "5. You may uninstall Claisum at any time using this installer.\n"
    "6. Auto-updates are downloaded from GitHub and applied on Discord restart.\n\n"
    "This software is not affiliated with Discord Inc.\n"
    "Source code: https://github.com/claisum/Claisum.py"
)


def find_discord():
    for base in [
        os.path.expandvars(r"%LOCALAPPDATA%\Discord"),
        os.path.expandvars(r"%LOCALAPPDATA%\discordptb"),
        os.path.expandvars(r"%LOCALAPPDATA%\discordcanary"),
    ]:
        hits = glob.glob(os.path.join(base, "app-*", "modules",
            "discord_desktop_core-*", "discord_desktop_core", "index.js"))
        if hits:
            return sorted(hits)[-1]
    return None


def get_inject_src():
    for p in [
        os.path.join(os.path.dirname(sys.executable if getattr(sys,"frozen",False)
                     else __file__), "claisum_inject.js"),
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..",
                         "claisum", "discord", "claisum_inject.js")),
    ]:
        if os.path.exists(p):
            return p
    return None


def build_loader():
    return (f"{PRELOAD}\n"
    ";(function(){\n"
    "  const _fs=require('fs'),_path=require('path'),_https=require('https');\n"
    f"  const VER='{VERSION}',REPO='{REPO}';\n"
    "  const jsFile=_path.join(__dirname,'claisum_inject.js');\n"
    "  function run(c){const go=()=>{try{eval(c);}catch(e){console.error('[Claisum]',e);}};\n"
    "    if(document.readyState==='loading')\n"
    "      window.addEventListener('DOMContentLoaded',()=>setTimeout(go,1500));\n"
    "    else setTimeout(go,1500);}\n"
    "  let base='';try{base=_fs.readFileSync(jsFile,'utf8');}catch(e){}\n"
    "  if(base)run(base);\n"
    "  try{const req=_https.get({hostname:'api.github.com',\n"
    "    path:'/repos/'+REPO+'/releases/latest',\n"
    "    headers:{'User-Agent':'Claisum-'+VER,'Accept':'application/vnd.github+json'}},res=>{\n"
    "    let d='';res.on('data',c=>d+=c);res.on('end',()=>{try{\n"
    "      const t=(JSON.parse(d).tag_name||'').replace(/^v/,'');\n"
    "      if(t&&t!==VER){_https.get({hostname:'raw.githubusercontent.com',\n"
    "        path:'/'+REPO+'/main/claisum/discord/claisum_inject.js',\n"
    "        headers:{'User-Agent':'Claisum-'+VER}},r=>{\n"
    "        let js='';r.on('data',c=>js+=c);\n"
    "        r.on('end',()=>{try{_fs.writeFileSync(jsFile,js,'utf8');}catch(e){}});\n"
    "      }).on('error',()=>{});}\n"
    "    }catch(e){}});});\n"
    "    req.setTimeout(8000,()=>req.destroy());req.on('error',()=>{});\n"
    "  }catch(e){}\n"
    "})();\n")


def kill_discord():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "Discord.exe"], capture_output=True)
    except Exception:
        pass


def do_inject(idx, dest):
    with open(idx, "r", encoding="utf-8") as f:
        content = f.read()
    if PRELOAD in content:
        do_remove(idx)
        with open(idx, "r", encoding="utf-8") as f:
            content = f.read()
    with open(idx, "w", encoding="utf-8") as f:
        f.write(build_loader() + "\n" + content)


def do_remove(idx):
    with open(idx, "r", encoding="utf-8") as f:
        content = f.read()
    if PRELOAD not in content:
        return False
    lines = content.split("\n")
    i = next((n for n, l in enumerate(lines) if PRELOAD in l), None)
    if i is None:
        return False
    end = i + 1
    while end < len(lines) and lines[end].strip():
        end += 1
    with open(idx, "w", encoding="utf-8") as f:
        f.write("\n".join(lines[end:]).lstrip("\n"))
    return True


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Claisum Installer  v{VERSION}")
        self.geometry("555x420")
        self.minsize(555, 420)
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._dark_titlebar()
        self._setup_style()
        self.action = tk.StringVar(value="install")
        self._page  = None
        self._rows  = {}
        self._accepted = False
        self._build_chrome()
        self.show_license()

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

    def _setup_style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('Dark.Vertical.TScrollbar',
                    background=BG3, troughcolor=BG2,
                    arrowcolor=DIM, bordercolor=BG2,
                    relief='flat', arrowsize=12)
        s.map('Dark.Vertical.TScrollbar',
              background=[('active', BG4), ('disabled', BG2)])

    # ── Chrome: header + footer packed FIRST (bottom) ─────────────────────
    def _build_chrome(self):
        # Header (top)
        hdr = tk.Frame(self, bg=BG2, height=50)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚡", bg=BG2, fg=ACCENT,
                 font=("Segoe UI Emoji", 20)).pack(side="left", padx=(14,6), pady=10)
        tk.Label(hdr, text=f"Claisum Installer  v{VERSION}", bg=BG2, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side="left", pady=10)
        tk.Frame(self, bg="#0a0a0c", height=1).pack(side="top", fill="x")

        # Footer (PACKED BEFORE CONTENT so it stays at bottom)
        tk.Frame(self, bg=BG4, height=1).pack(side="bottom", fill="x")
        foot = tk.Frame(self, bg=BG2, height=54)
        foot.pack(side="bottom", fill="x")
        foot.pack_propagate(False)

        for icon, url in [
            ("🌐", "https://github.com/claisum/Claisum.py"),
            ("🐙", "https://github.com/claisum/Claisum.py"),
            ("❤",  "https://github.com/claisum/Claisum.py/stargazers"),
        ]:
            lbl = tk.Label(foot, text=icon, bg=BG2, fg=DIM,
                           font=("Segoe UI Emoji", 13), cursor="hand2")
            lbl.pack(side="left", padx=(12,2), pady=14)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        # Next button — always normal state; command swapped to block when locked
        self.btn_next = tk.Button(
            foot, text="Next", bg="#3a3c40", fg=DIM, bd=0, relief="flat",
            font=("Segoe UI", 10, "bold"), padx=22, pady=6, cursor="hand2",
            activebackground=ACCENT, activeforeground="#fff",
            command=lambda: None)
        self.btn_next.pack(side="right", padx=(4, 14), pady=10)

        self.btn_back = tk.Button(
            foot, text="Back", bg=BG3, fg=TEXT, bd=0, relief="flat",
            font=("Segoe UI", 10, "bold"), padx=22, pady=6, cursor="hand2",
            activebackground=BG4, activeforeground=TEXT,
            command=self.go_back)
        self.btn_back.pack(side="right", padx=4, pady=10)

        # Content (fills the remaining space between header and footer)
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="top", fill="both", expand=True, padx=24, pady=14)

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _hdr(self, icon, title):
        f = tk.Frame(self.content, bg=BG)
        f.pack(fill="x", pady=(0, 10))
        tk.Label(f, text=icon, bg=BG, fg=TEXT,
                 font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, 10))
        tk.Label(f, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left", anchor="s", pady=(4, 0))

    def _set_next(self, active):
        if active:
            self.btn_next.configure(bg=ACCENT, fg="#ffffff", command=self.go_next)
        else:
            self.btn_next.configure(bg="#3a3c40", fg=DIM, command=lambda: None)

    # ── License page ───────────────────────────────────────────────────────
    def show_license(self):
        self._page = "license"
        self._accepted = False
        self._clear()
        self.btn_back.configure(state="disabled", fg=DIM)
        self._set_next(False)

        self._hdr("🏛", "License Agreement")

        # Scrollable text box
        txt_frame = tk.Frame(self.content, bg=BG3)
        txt_frame.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(txt_frame, orient="vertical", style='Dark.Vertical.TScrollbar')
        txt = tk.Text(
            txt_frame, bg=BG3, fg=DIM,
            font=("Segoe UI", 9), bd=0, relief="flat",
            wrap="word", padx=12, pady=8,
            yscrollcommand=sb.set,
            cursor="arrow",
        )
        sb.configure(command=txt.yview)
        sb.pack(side="right", fill="y", pady=1, padx=(0,1))
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", EULA)
        txt.configure(state="disabled")

        # Mouse wheel scrolling
        def _scroll(event):
            txt.yview_scroll(int(-1*(event.delta/120)), "units")
        txt.bind("<MouseWheel>", _scroll)

        # Checkbox row
        chk_row = tk.Frame(self.content, bg=BG)
        chk_row.pack(fill="x", pady=(10, 0))

        chk_var = tk.IntVar(value=0)

        def on_toggle():
            self._accepted = bool(chk_var.get())
            self._set_next(self._accepted)

        tk.Checkbutton(
            chk_row,
            text="  I accept the license agreement.",
            variable=chk_var, onvalue=1, offvalue=0,
            bg=BG, fg=TEXT,
            selectcolor=BG3,
            activebackground=BG, activeforeground=TEXT,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            command=on_toggle,
        ).pack(anchor="w")

    # ── Action page ────────────────────────────────────────────────────────
    def show_action(self):
        self._page = "action"
        self._clear()
        self.btn_back.configure(state="normal", fg=TEXT)
        self._set_next(True)
        self._hdr("↔", "Choose an Action")
        self._rows = {}

        for val, icon, label, sub in [
            ("install",   "⬇", "Install Claisum",   "Inject Claisum into your Discord"),
            ("repair",    "🔧", "Repair Claisum",    "Re-inject if Claisum stopped working"),
            ("uninstall", "🗑", "Uninstall Claisum", "Completely remove Claisum from Discord"),
        ]:
            row = tk.Frame(self.content, bg=BG3, cursor="hand2")
            row.pack(fill="x", pady=3)
            inner = tk.Frame(row, bg=BG3)
            inner.pack(fill="both", padx=12, pady=10)
            ik = tk.Label(inner, text=icon, bg=BG3, fg=TEXT,
                          font=("Segoe UI Emoji", 16), width=2)
            ik.pack(side="left", padx=(0, 10))
            tf = tk.Frame(inner, bg=BG3)
            tf.pack(side="left", fill="x", expand=True)
            nl = tk.Label(tf, text=label, bg=BG3, fg=TEXT,
                          font=("Segoe UI", 11, "bold"), anchor="w")
            nl.pack(anchor="w")
            sl = tk.Label(tf, text=sub, bg=BG3, fg=DIM,
                          font=("Segoe UI", 9), anchor="w")
            sl.pack(anchor="w")
            self._rows[val] = (row, inner, ik, tf, nl, sl)
            for w in [row, inner, ik, tf, nl, sl]:
                w.bind("<Button-1>", lambda e, v=val: self._select(v))
        self._select("install")

    def _select(self, val):
        self.action.set(val)
        for v, (row, inner, ik, tf, nl, sl) in self._rows.items():
            on = v == val
            bg  = ACCENT if on else BG3
            fg  = "#ffffff" if on else TEXT
            dfg = "#c5caff" if on else DIM
            for w in [row, inner, ik, tf]:
                w.configure(bg=bg)
            nl.configure(bg=bg, fg=fg)
            sl.configure(bg=bg, fg=dfg)

    # ── Installing page ────────────────────────────────────────────────────
    def show_installing(self):
        self._page = "installing"
        self._clear()
        self.btn_back.configure(state="disabled", fg=DIM)
        self._set_next(False)

        act = self.action.get()
        titles = {"install": "Installing…", "repair": "Repairing…", "uninstall": "Uninstalling…"}
        self._hdr("⚡", titles.get(act, "Working…"))

        self.status_lbl = tk.Label(self.content, text="Preparing…",
                                   bg=BG, fg=DIM, font=("Segoe UI", 9))
        self.status_lbl.pack(anchor="w", pady=(0, 10))

        pb_bg = tk.Frame(self.content, bg=BG3, height=6)
        pb_bg.pack(fill="x")
        self.pb = tk.Frame(pb_bg, bg=ACCENT, height=6)
        self.pb.place(relwidth=0.0, relheight=1)

        threading.Thread(target=self._run, daemon=True).start()

    def _upd(self, msg, p=None):
        self.after(0, lambda: self.status_lbl.configure(text=msg))
        if p is not None:
            self.after(0, lambda: self.pb.place(relwidth=p, relheight=1))

    def _run(self):
        try:
            if self.action.get() in ("install", "repair"):
                self._install()
            else:
                self._uninstall()
        except Exception as ex:
            self.after(0, lambda: self.show_done(False, str(ex)))

    def _install(self):
        self._upd("Closing Discord…", 0.1)
        kill_discord()
        self._upd("Finding Discord installation…", 0.30)
        idx = find_discord()
        if not idx:
            raise RuntimeError("Discord not found. Please install Discord first.")
        core = os.path.dirname(idx)
        dest = os.path.join(core, "claisum_inject.js")
        self._upd("Copying Claisum files…", 0.55)
        src = get_inject_src()
        if src:
            shutil.copy2(src, dest)
        else:
            urllib.request.urlretrieve(
                f"https://raw.githubusercontent.com/{REPO}/main/claisum/discord/claisum_inject.js",
                dest)
        self._upd("Patching Discord core…", 0.82)
        do_inject(idx, dest)
        self._upd("Done!", 1.0)
        self.after(350, lambda: self.show_done(True,
            "Claisum installed successfully!\n\n"
            "Restart Discord — the ⚡ button will appear in the bottom-left corner.\n\n"
            "Claisum auto-updates on every Discord start."))

    def _uninstall(self):
        self._upd("Closing Discord…", 0.1)
        kill_discord()
        self._upd("Finding Discord…", 0.35)
        idx = find_discord()
        if not idx:
            raise RuntimeError("Discord not found.")
        dest = os.path.join(os.path.dirname(idx), "claisum_inject.js")
        self._upd("Removing injection…", 0.65)
        do_remove(idx)
        self._upd("Removing files…", 0.85)
        try:
            os.remove(dest)
        except FileNotFoundError:
            pass
        self._upd("Done!", 1.0)
        self.after(350, lambda: self.show_done(True,
            "Claisum removed from Discord.\n\n"
            "Your themes and plugin data were kept in Discord's local storage."))

    # ── Done page ──────────────────────────────────────────────────────────
    def show_done(self, ok, msg):
        self._page = "done"
        self._clear()
        self.btn_back.configure(state="disabled", fg=DIM)
        self.btn_next.configure(text="Finish")
        self._set_next(True)
        self._hdr("✅" if ok else "❌", "Done!" if ok else "Error")
        tk.Label(self.content, text=msg, bg=BG,
                 fg=TEXT if ok else ERR,
                 font=("Segoe UI", 10),
                 wraplength=490, justify="left").pack(anchor="w")

    # ── Navigation ─────────────────────────────────────────────────────────
    def go_back(self):
        if self._page == "action":
            self.show_license()
        elif self._page == "done":
            self.show_action()

    def go_next(self):
        if self._page == "license":
            self.show_action()
        elif self._page == "action":
            self.show_installing()
        elif self._page == "done":
            self.destroy()


if __name__ == "__main__":
    App().mainloop()
