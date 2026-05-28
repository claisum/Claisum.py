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
PRELOAD = "// [Claisum Injected]"

EULA = (
    "End-User License Agreement for Claisum\n\n"
    "PLEASE READ THIS AGREEMENT CAREFULLY.\n\n"
    "By installing Claisum you agree to the following terms:\n\n"
    "1. Claisum is free, open-source software without warranty.\n"
    "2. You may not redistribute Claisum for commercial purposes.\n"
    "3. Claisum modifies Discord local files; use at your own risk.\n"
    "4. The authors are not responsible for any Discord account actions.\n"
    "5. You may uninstall Claisum at any time using this installer.\n"
    "6. Auto-updates are downloaded from GitHub on every Discord start.\n\n"
    "This software is not affiliated with Discord Inc.\n"
    "Source: https://github.com/claisum/Claisum.py"
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
        os.path.join(os.path.dirname(
            sys.executable if getattr(sys, "frozen", False) else __file__),
            "claisum_inject.js"),
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..",
            "claisum", "discord", "claisum_inject.js")),
    ]:
        if os.path.exists(p):
            return p
    return None


def build_loader():
    return (
        f"{PRELOAD}\n"
        ";(function(){\n"
        "  const _fs=require('fs'),_path=require('path'),_https=require('https');\n"
        f"  const VER='{VERSION}',REPO='{REPO}';\n"
        "  const jsFile=_path.join(__dirname,'claisum_inject.js');\n"
        "  function run(c){\n"
        "    const go=()=>{try{eval(c);}catch(e){console.error('[Claisum]',e);}};\n"
        "    if(document.readyState==='loading')\n"
        "      window.addEventListener('DOMContentLoaded',()=>setTimeout(go,1500));\n"
        "    else setTimeout(go,1500);\n"
        "  }\n"
        "  try{run(_fs.readFileSync(jsFile,'utf8'));}catch(e){}\n"
        "  try{\n"
        "    const req=_https.get({hostname:'api.github.com',\n"
        "      path:'/repos/'+REPO+'/releases/latest',\n"
        "      headers:{'User-Agent':'Claisum-'+VER,'Accept':'application/vnd.github+json'}},\n"
        "    res=>{let d='';res.on('data',c=>d+=c);res.on('end',()=>{\n"
        "      try{const t=(JSON.parse(d).tag_name||'').replace(/^v/,'');\n"
        "        if(t&&t!==VER){\n"
        "          _https.get({hostname:'raw.githubusercontent.com',\n"
        "            path:'/'+REPO+'/main/claisum/discord/claisum_inject.js',\n"
        "            headers:{'User-Agent':'Claisum-'+VER}},r=>{\n"
        "            let js='';r.on('data',c=>js+=c);\n"
        "            r.on('end',()=>{try{_fs.writeFileSync(jsFile,js,'utf8');}catch(e){}});\n"
        "          }).on('error',()=>{});\n"
        "        }\n"
        "      }catch(e){}\n"
        "    });});\n"
        "    req.setTimeout(8000,()=>req.destroy());\n"
        "    req.on('error',()=>{});\n"
        "  }catch(e){}\n"
        "})();\n"
    )


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


# ── Main window ────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Claisum Installer  v{VERSION}")
        self.geometry("555x420")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._dark_titlebar()
        self._setup_scrollbar_style()
        self.action    = tk.StringVar(value="install")
        self._page     = None
        self._rows     = {}
        self._chk_var  = tk.IntVar(value=0)
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

    def _setup_scrollbar_style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('D.Vertical.TScrollbar',
                    background=BG4, troughcolor=BG2,
                    arrowcolor=DIM, bordercolor=BG2, relief='flat')
        s.map('D.Vertical.TScrollbar', background=[('active', '#555860')])

    def _build_chrome(self):
        # Header (top)
        hdr = tk.Frame(self, bg=BG2, height=50)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="CL", bg=ACCENT, fg="#fff",
                 font=("Segoe UI", 12, "bold"),
                 width=3, relief="flat").pack(side="left", padx=14, pady=12)
        tk.Label(hdr, text=f"Claisum Installer  v{VERSION}",
                 bg=BG2, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Frame(self, bg="#0a0a0c", height=1).pack(side="top", fill="x")

        # Footer packed BEFORE content so it always stays at the bottom
        tk.Frame(self, bg=BG4, height=1).pack(side="bottom", fill="x")
        foot = tk.Frame(self, bg=BG2, height=56)
        foot.pack(side="bottom", fill="x")
        foot.pack_propagate(False)

        # Social icons
        for txt, url in [
            ("Web",  "https://github.com/claisum/Claisum.py"),
            ("Git",  "https://github.com/claisum/Claisum.py"),
            ("Star", "https://github.com/claisum/Claisum.py/stargazers"),
        ]:
            lbl = tk.Label(foot, text=txt, bg=BG2, fg=DIM,
                           font=("Segoe UI", 9), cursor="hand2")
            lbl.pack(side="left", padx=(10, 2), pady=18)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        # Next button — styled blue when active, gray when locked
        self.btn_next = tk.Button(
            foot, text="Next",
            bg="#3a3c40", fg=DIM,
            bd=0, relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=24, pady=7,
            cursor="hand2",
            command=self._on_next)
        self.btn_next.pack(side="right", padx=(4, 14), pady=10)

        self.btn_back = tk.Button(
            foot, text="Back",
            bg=BG3, fg=TEXT,
            bd=0, relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=24, pady=7,
            cursor="hand2",
            command=self._on_back)
        self.btn_back.pack(side="right", padx=4, pady=10)

        # Content fills the space between header and footer
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="top", fill="both", expand=True, padx=24, pady=14)

    # ── Navigation handlers with error protection ──────────────────────────
    def _on_next(self):
        try:
            self._go_next()
        except Exception:
            messagebox.showerror("Error", traceback.format_exc())

    def _on_back(self):
        try:
            self._go_back()
        except Exception:
            messagebox.showerror("Error", traceback.format_exc())

    def _go_next(self):
        if self._page == "license":
            if not self._chk_var.get():
                # Flash the checkbox label to tell user to accept first
                if hasattr(self, '_chk_lbl'):
                    self._chk_lbl.configure(fg=ERR)
                    self.after(1200, lambda: self._chk_lbl.configure(fg=TEXT))
                return
            self.show_action()
        elif self._page == "action":
            self.show_installing()
        elif self._page == "done":
            self.destroy()

    def _go_back(self):
        if self._page == "action":
            self.show_license()
        elif self._page == "done":
            self.show_action()

    def _set_next_active(self, active):
        if active:
            self.btn_next.configure(bg=ACCENT, fg="#ffffff")
        else:
            self.btn_next.configure(bg="#3a3c40", fg=DIM)

    # ── Helpers ────────────────────────────────────────────────────────────
    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _section_title(self, icon_text, title):
        """Plain-text icon + title — no emoji fonts needed."""
        f = tk.Frame(self.content, bg=BG)
        f.pack(fill="x", pady=(0, 10))
        tk.Label(f, text=icon_text, bg=ACCENT, fg="#fff",
                 font=("Segoe UI", 10, "bold"),
                 padx=6, pady=2).pack(side="left", padx=(0, 10))
        tk.Label(f, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left", anchor="s", pady=(2, 0))

    # ── Page: License ──────────────────────────────────────────────────────
    def show_license(self):
        self._page = "license"
        self._chk_var.set(0)
        self._clear()
        self.btn_back.configure(state="disabled", fg=DIM, bg=BG3)
        self._set_next_active(False)

        self._section_title("EULA", "License Agreement")

        # Text area with dark scrollbar
        txt_frame = tk.Frame(self.content, bg=BG3)
        txt_frame.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(txt_frame, orient="vertical", style='D.Vertical.TScrollbar')
        txt = tk.Text(
            txt_frame,
            bg=BG3, fg="#adb1b8",
            font=("Segoe UI", 9),
            bd=0, relief="flat",
            wrap="word",
            padx=12, pady=10,
            yscrollcommand=sb.set,
            cursor="arrow",
            selectbackground=BG4,
        )
        sb.configure(command=txt.yview)
        sb.pack(side="right", fill="y", padx=(0, 1), pady=1)
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", EULA)
        txt.configure(state="disabled")
        txt.bind("<MouseWheel>", lambda e: txt.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Accept checkbox
        chk_row = tk.Frame(self.content, bg=BG)
        chk_row.pack(fill="x", pady=(10, 0))

        def on_toggle():
            self._set_next_active(bool(self._chk_var.get()))
            if hasattr(self, '_chk_lbl') and self._chk_var.get():
                self._chk_lbl.configure(fg=TEXT)

        chk = tk.Checkbutton(
            chk_row,
            text="  I accept the license agreement",
            variable=self._chk_var,
            onvalue=1, offvalue=0,
            bg=BG, fg=TEXT,
            selectcolor=BG3,
            activebackground=BG, activeforeground=TEXT,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            command=on_toggle,
        )
        chk.pack(side="left", anchor="w")
        self._chk_lbl = chk

    # ── Page: Choose Action ────────────────────────────────────────────────
    def show_action(self):
        self._page = "action"
        self._clear()
        self.btn_back.configure(state="normal", fg=TEXT, bg=BG3)
        self._set_next_active(True)

        self._section_title("ACT", "Choose an Action")
        self._rows = {}

        actions = [
            ("install",   "[+]", "Install Claisum",   "Inject Claisum into your Discord"),
            ("repair",    "[~]", "Repair Claisum",    "Re-inject if Claisum stopped working"),
            ("uninstall", "[x]", "Uninstall Claisum", "Completely remove Claisum from Discord"),
        ]
        for val, badge, label, sub in actions:
            row = tk.Frame(self.content, bg=BG3, cursor="hand2")
            row.pack(fill="x", pady=3)

            inner = tk.Frame(row, bg=BG3)
            inner.pack(fill="both", padx=12, pady=10)

            badge_lbl = tk.Label(inner, text=badge, bg=BG4, fg=DIM,
                                 font=("Consolas", 11, "bold"), width=3)
            badge_lbl.pack(side="left", padx=(0, 12))

            tf = tk.Frame(inner, bg=BG3)
            tf.pack(side="left", fill="x", expand=True)

            nl = tk.Label(tf, text=label, bg=BG3, fg=TEXT,
                          font=("Segoe UI", 11, "bold"), anchor="w")
            nl.pack(anchor="w")
            sl = tk.Label(tf, text=sub, bg=BG3, fg=DIM,
                          font=("Segoe UI", 9), anchor="w")
            sl.pack(anchor="w")

            self._rows[val] = (row, inner, badge_lbl, tf, nl, sl)
            for w in [row, inner, badge_lbl, tf, nl, sl]:
                w.bind("<Button-1>", lambda e, v=val: self._select(v))

        self._select("install")

    def _select(self, val):
        self.action.set(val)
        for v, (row, inner, badge_lbl, tf, nl, sl) in self._rows.items():
            on  = (v == val)
            bg  = ACCENT if on else BG3
            fg  = "#ffffff" if on else TEXT
            dfg = "#c5caff" if on else DIM
            bdg_bg = "#4752c4" if on else BG4
            bdg_fg = "#fff" if on else DIM
            for w in [row, inner, tf]:
                w.configure(bg=bg)
            badge_lbl.configure(bg=bdg_bg, fg=bdg_fg)
            nl.configure(bg=bg, fg=fg)
            sl.configure(bg=bg, fg=dfg)

    # ── Page: Installing ───────────────────────────────────────────────────
    def show_installing(self):
        self._page = "installing"
        self._clear()
        self.btn_back.configure(state="disabled", fg=DIM)
        self._set_next_active(False)

        act = self.action.get()
        titles = {
            "install":   "Installing Claisum...",
            "repair":    "Repairing Claisum...",
            "uninstall": "Uninstalling Claisum...",
        }
        self._section_title("...", titles.get(act, "Working..."))

        self.status_lbl = tk.Label(self.content, text="Preparing...",
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
            self.after(0, lambda pv=p: self.pb.place(relwidth=pv, relheight=1))

    def _run(self):
        try:
            if self.action.get() in ("install", "repair"):
                self._install()
            else:
                self._uninstall()
        except Exception as ex:
            tb = traceback.format_exc()
            self.after(0, lambda: self.show_done(False, str(ex) + "\n\n" + tb[:400]))

    def _install(self):
        self._upd("Closing Discord...", 0.10)
        kill_discord()
        self._upd("Finding Discord installation...", 0.30)
        idx = find_discord()
        if not idx:
            raise RuntimeError("Discord not found. Please install Discord first.")
        core = os.path.dirname(idx)
        dest = os.path.join(core, "claisum_inject.js")
        self._upd("Copying Claisum files...", 0.55)
        src = get_inject_src()
        if src:
            shutil.copy2(src, dest)
        else:
            urllib.request.urlretrieve(
                f"https://raw.githubusercontent.com/{REPO}/main/claisum/discord/claisum_inject.js",
                dest)
        self._upd("Patching Discord core...", 0.82)
        do_inject(idx, dest)
        self._upd("Done!", 1.0)
        self.after(300, lambda: self.show_done(True,
            "Claisum installed!\n\n"
            "Restart Discord. The [CL] button will appear in the bottom-left corner.\n\n"
            "Claisum checks for updates automatically on every Discord start."))

    def _uninstall(self):
        self._upd("Closing Discord...", 0.10)
        kill_discord()
        self._upd("Finding Discord...", 0.35)
        idx = find_discord()
        if not idx:
            raise RuntimeError("Discord not found.")
        dest = os.path.join(os.path.dirname(idx), "claisum_inject.js")
        self._upd("Removing injection...", 0.65)
        do_remove(idx)
        self._upd("Removing files...", 0.85)
        try:
            os.remove(dest)
        except FileNotFoundError:
            pass
        self._upd("Done!", 1.0)
        self.after(300, lambda: self.show_done(True,
            "Claisum removed from Discord.\n\n"
            "Your themes and plugin settings remain in Discord local storage."))

    # ── Page: Done ─────────────────────────────────────────────────────────
    def show_done(self, ok, msg):
        self._page = "done"
        self._clear()
        self.btn_back.configure(state="disabled", fg=DIM)
        self.btn_next.configure(text="Finish")
        self._set_next_active(True)
        badge = "OK" if ok else "!!"
        self._section_title(badge, "Done!" if ok else "Error")
        tk.Label(self.content, text=msg,
                 bg=BG, fg=TEXT if ok else ERR,
                 font=("Segoe UI", 9),
                 wraplength=490, justify="left").pack(anchor="w", pady=(4, 0))


if __name__ == "__main__":
    App().mainloop()
