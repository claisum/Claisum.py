"""Claisum Installer v1.0.0.1 — BetterDiscord-style GUI"""
import sys, os, glob, shutil, threading, subprocess, urllib.request, webbrowser
import tkinter as tk

VERSION = "1.0.0.1"
REPO    = "claisum/Claisum.py"
BG      = "#1a1b1e"
BG2     = "#111214"
BG3     = "#2d2f32"
ACCENT  = "#5865F2"
TEXT    = "#dbdee1"
DIM     = "#80848e"
OK      = "#23a55a"
ERR     = "#f04747"
PRELOAD = "// [Claisum Injected]"

EULA = """End-User License Agreement for Claisum

PLEASE READ THIS AGREEMENT CAREFULLY.

By installing Claisum you agree to the following terms:

1. Claisum is free, open-source software provided "as is" without warranty.
2. You may not redistribute Claisum for commercial purposes.
3. Claisum modifies Discord's local files; use at your own risk.
4. The authors are not responsible for any Discord account actions.
5. You may uninstall Claisum at any time using this installer.
6. Auto-updates are downloaded from GitHub and applied on Discord restart.

This software is not affiliated with Discord Inc.
Source code: https://github.com/claisum/Claisum.py"""


# ── Discord helpers ────────────────────────────────────────────────────────
def find_discord():
    bases = [
        os.path.expandvars(r"%LOCALAPPDATA%\Discord"),
        os.path.expandvars(r"%LOCALAPPDATA%\discordptb"),
        os.path.expandvars(r"%LOCALAPPDATA%\discordcanary"),
    ]
    for base in bases:
        hits = glob.glob(os.path.join(base, "app-*", "modules",
            "discord_desktop_core-*", "discord_desktop_core", "index.js"))
        if hits:
            return sorted(hits)[-1]
    return None

def get_inject_src():
    for p in [
        os.path.join(os.path.dirname(sys.executable if getattr(sys,"frozen",False) else __file__), "claisum_inject.js"),
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "claisum", "discord", "claisum_inject.js")),
    ]:
        if os.path.exists(p): return p
    return None

def build_loader():
    return f"""{PRELOAD}
;(function(){{
  const _fs=require('fs'),_path=require('path'),_https=require('https');
  const VER='{VERSION}',REPO='{REPO}';
  const jsFile=_path.join(__dirname,'claisum_inject.js');
  function run(c){{const go=()=>{{try{{eval(c);}}catch(e){{console.error('[Claisum]',e);}}}};
    if(document.readyState==='loading')window.addEventListener('DOMContentLoaded',()=>setTimeout(go,1500));
    else setTimeout(go,1500);}}
  let base='';try{{base=_fs.readFileSync(jsFile,'utf8');}}catch(e){{}}
  if(base)run(base);
  try{{const req=_https.get({{hostname:'api.github.com',
    path:'/repos/'+REPO+'/releases/latest',
    headers:{{'User-Agent':'Claisum-'+VER,'Accept':'application/vnd.github+json'}}}},res=>{{
    let d='';res.on('data',c=>d+=c);res.on('end',()=>{{try{{
      const t=(JSON.parse(d).tag_name||'').replace(/^v/,'');
      if(t&&t!==VER){{_https.get({{hostname:'raw.githubusercontent.com',
        path:'/'+REPO+'/main/claisum/discord/claisum_inject.js',
        headers:{{'User-Agent':'Claisum-'+VER}}}},r=>{{
        let js='';r.on('data',c=>js+=c);
        r.on('end',()=>{{try{{_fs.writeFileSync(jsFile,js,'utf8');}}catch(e){{}}}});
      }}).on('error',()=>{{}});}}}}catch(e){{}}}}); }});
    req.setTimeout(8000,()=>req.destroy());req.on('error',()=>{{}});}}catch(e){{}}
}})();
"""

def kill_discord():
    try: subprocess.run(["taskkill","/F","/IM","Discord.exe"], capture_output=True)
    except: pass

def do_inject(idx, dest):
    with open(idx,"r",encoding="utf-8") as f: content=f.read()
    if PRELOAD in content: do_remove(idx); f=open(idx,"r",encoding="utf-8"); content=f.read(); f.close()
    with open(idx,"w",encoding="utf-8") as f: f.write(build_loader()+"\n"+content)

def do_remove(idx):
    with open(idx,"r",encoding="utf-8") as f: content=f.read()
    if PRELOAD not in content: return False
    lines=content.split("\n")
    start=next((i for i,l in enumerate(lines) if PRELOAD in l),None)
    if start is None: return False
    end=start+1
    while end<len(lines) and lines[end].strip(): end+=1
    with open(idx,"w",encoding="utf-8") as f: f.write("\n".join(lines[end:]).lstrip("\n"))
    return True


# ── GUI ────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Claisum Installer  v{VERSION}")
        self.geometry("555x400")
        self.resizable(False,False)
        self.configure(bg=BG)
        self._center()
        self._dark_titlebar()
        self.action = tk.StringVar(value="install")
        self._page  = None
        self._rows  = {}
        self._build_chrome()
        self.show_license()

    def _center(self):
        self.update_idletasks()
        sw,sh=self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f"555x400+{(sw-555)//2}+{(sh-400)//2}")

    def _dark_titlebar(self):
        try:
            import ctypes
            hwnd=ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd,20,ctypes.byref(ctypes.c_int(1)),ctypes.sizeof(ctypes.c_int))
        except: pass

    def _build_chrome(self):
        hdr=tk.Frame(self,bg=BG2,height=50); hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr,text="⚡",bg=BG2,fg=ACCENT,font=("Segoe UI",20)).pack(side="left",padx=(14,6),pady=10)
        tk.Label(hdr,text=f"Claisum Installer  v{VERSION}",bg=BG2,fg=TEXT,
                 font=("Segoe UI",11,"bold")).pack(side="left",pady=10)
        tk.Frame(self,bg="#0d0d0f",height=1).pack(fill="x")

        self.content=tk.Frame(self,bg=BG)
        self.content.pack(fill="both",expand=True,padx=26,pady=(18,0))

        tk.Frame(self,bg=BG3,height=1).pack(fill="x")
        foot=tk.Frame(self,bg=BG2,height=52); foot.pack(fill="x"); foot.pack_propagate(False)

        for icon,url in [("🌐","https://github.com/claisum/Claisum.py"),
                          ("🐙","https://github.com/claisum/Claisum.py"),
                          ("❤","https://github.com/claisum/Claisum.py/stargazers")]:
            lbl=tk.Label(foot,text=icon,bg=BG2,fg=DIM,font=("Segoe UI",13),cursor="hand2")
            lbl.pack(side="left",padx=(12,2),pady=14)
            lbl.bind("<Button-1>",lambda e,u=url: webbrowser.open(u))

        self.btn_next=tk.Button(foot,text="Next",bg="#3a3c40",fg=DIM,bd=0,relief="flat",
            font=("Segoe UI",10,"bold"),padx=20,pady=5,cursor="hand2",
            activebackground=ACCENT,activeforeground="#fff",command=self.go_next)
        self.btn_next.pack(side="right",padx=(4,14),pady=12)

        self.btn_back=tk.Button(foot,text="Back",bg=BG3,fg=DIM,bd=0,relief="flat",
            font=("Segoe UI",10,"bold"),padx=20,pady=5,cursor="hand2",
            activebackground="#45474a",activeforeground=TEXT,command=self.go_back)
        self.btn_back.pack(side="right",padx=4,pady=12)

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _hdr(self,icon,title):
        f=tk.Frame(self.content,bg=BG); f.pack(fill="x",pady=(0,12))
        tk.Label(f,text=icon,bg=BG,fg=TEXT,font=("Segoe UI",20)).pack(side="left",padx=(0,10))
        tk.Label(f,text=title,bg=BG,fg=TEXT,font=("Segoe UI",14,"bold")).pack(side="left",anchor="s",pady=(4,0))

    # ── Page: License ──────────────────────────────────────────────────────
    def show_license(self):
        self._page="license"; self._clear()
        # Back: disabled, Next: locked (gray) until checkbox
        self.btn_back.configure(state="disabled",bg=BG3,fg=DIM)
        self._next_locked(True)
        self._hdr("🏛","License Agreement")

        box=tk.Frame(self.content,bg=BG3); box.pack(fill="both",expand=True)
        sb=tk.Scrollbar(box,bg=BG3,troughcolor=BG3,width=8)
        txt=tk.Text(box,bg=BG3,fg=DIM,font=("Segoe UI",9),bd=0,relief="flat",
                    wrap="word",padx=12,pady=8,yscrollcommand=sb.set)
        sb.config(command=txt.yview); sb.pack(side="right",fill="y")
        txt.pack(fill="both",expand=True)
        txt.insert("1.0",EULA); txt.configure(state="disabled")

        chk_f=tk.Frame(self.content,bg=BG); chk_f.pack(fill="x",pady=(10,0))
        self._chk_var=tk.IntVar(value=0)

        def on_chk():
            if self._chk_var.get()==1: self._next_locked(False)
            else: self._next_locked(True)

        chk=tk.Checkbutton(chk_f,text="  I accept the license agreement.",
            variable=self._chk_var,onvalue=1,offvalue=0,
            bg=BG,fg=TEXT,selectcolor=BG3,
            activebackground=BG,activeforeground=TEXT,
            font=("Segoe UI",10,"bold"),cursor="hand2",
            command=on_chk)
        chk.pack(anchor="w")

    def _next_locked(self,locked):
        """Toggle Next button between locked (gray) and active (blue)."""
        if locked:
            self.btn_next.configure(bg="#3a3c40",fg=DIM,state="normal",
                                    command=lambda: None)
        else:
            self.btn_next.configure(bg=ACCENT,fg="#ffffff",state="normal",
                                    command=self.go_next)

    # ── Page: Choose Action ────────────────────────────────────────────────
    def show_action(self):
        self._page="action"; self._clear()
        self.btn_back.configure(state="normal",bg=BG3,fg=TEXT)
        self.btn_next.configure(bg=ACCENT,fg="#fff",state="normal",command=self.go_next)
        self._hdr("↔","Choose an Action")
        self._rows={}
        for val,icon,label,sub in [
            ("install",  "⬇","Install Claisum",  "Inject Claisum into your Discord"),
            ("repair",   "🔧","Repair Claisum",   "Re-inject if Claisum stopped working"),
            ("uninstall","🗑","Uninstall Claisum","Completely remove Claisum from Discord"),
        ]:
            row=tk.Frame(self.content,bg=BG3,cursor="hand2"); row.pack(fill="x",pady=4)
            inner=tk.Frame(row,bg=BG3); inner.pack(fill="both",padx=12,pady=10)
            ik=tk.Label(inner,text=icon,bg=BG3,fg=TEXT,font=("Segoe UI",16),width=2)
            ik.pack(side="left",padx=(0,10))
            tf=tk.Frame(inner,bg=BG3); tf.pack(side="left",fill="x",expand=True)
            nl=tk.Label(tf,text=label,bg=BG3,fg=TEXT,font=("Segoe UI",11,"bold"),anchor="w")
            nl.pack(anchor="w")
            sl=tk.Label(tf,text=sub,bg=BG3,fg=DIM,font=("Segoe UI",9),anchor="w")
            sl.pack(anchor="w")
            self._rows[val]=(row,inner,ik,tf,nl,sl)
            for w in [row,inner,ik,tf,nl,sl]:
                w.bind("<Button-1>",lambda e,v=val: self._select(v))
        self._select("install")

    def _select(self,val):
        self.action.set(val)
        for v,(row,inner,ik,tf,nl,sl) in self._rows.items():
            on=v==val
            bg=ACCENT if on else BG3; fg="#fff" if on else TEXT; dfg="#c5caff" if on else DIM
            for w in [row,inner,ik,tf]: w.configure(bg=bg)
            nl.configure(bg=bg,fg=fg); sl.configure(bg=bg,fg=dfg)

    # ── Page: Installing ───────────────────────────────────────────────────
    def show_installing(self):
        self._page="installing"; self._clear()
        self.btn_back.configure(state="disabled")
        self.btn_next.configure(bg="#3a3c40",fg=DIM,state="normal",command=lambda:None)
        act=self.action.get()
        self._hdr("⚡",{"install":"Installing…","repair":"Repairing…","uninstall":"Uninstalling…"}.get(act,"Working…"))
        self.status_lbl=tk.Label(self.content,text="Preparing…",bg=BG,fg=DIM,font=("Segoe UI",9))
        self.status_lbl.pack(anchor="w",pady=(0,10))
        pb_bg=tk.Frame(self.content,bg=BG3,height=6); pb_bg.pack(fill="x")
        self.pb=tk.Frame(pb_bg,bg=ACCENT,height=6); self.pb.place(relwidth=0.0,relheight=1)
        threading.Thread(target=self._run,daemon=True).start()

    def _status(self,msg,p=None):
        self.after(0,lambda:self.status_lbl.configure(text=msg))
        if p is not None: self.after(0,lambda:self.pb.place(relwidth=p,relheight=1))

    def _run(self):
        try:
            if self.action.get() in ("install","repair"): self._install()
            else: self._uninstall()
        except Exception as ex: self.after(0,lambda:self.show_done(False,str(ex)))

    def _install(self):
        self._status("Closing Discord…",.1); kill_discord()
        self._status("Finding Discord installation…",.3)
        idx=find_discord()
        if not idx: raise RuntimeError("Discord not found. Please install Discord first.")
        core=os.path.dirname(idx); dest=os.path.join(core,"claisum_inject.js")
        self._status("Copying files…",.55)
        src=get_inject_src()
        if src: shutil.copy2(src,dest)
        else:
            urllib.request.urlretrieve(
                f"https://raw.githubusercontent.com/{REPO}/main/claisum/discord/claisum_inject.js",dest)
        self._status("Patching Discord core…",.80)
        do_inject(idx,dest)
        self._status("Done!",1.0)
        self.after(300,lambda:self.show_done(True,
            "Claisum installed successfully!\n\n"
            "Restart Discord — the ⚡ button appears in the bottom-left corner.\n\n"
            "Claisum checks for updates automatically on every Discord start."))

    def _uninstall(self):
        self._status("Closing Discord…",.1); kill_discord()
        self._status("Finding Discord…",.35)
        idx=find_discord()
        if not idx: raise RuntimeError("Discord not found.")
        dest=os.path.join(os.path.dirname(idx),"claisum_inject.js")
        self._status("Removing injection…",.65); do_remove(idx)
        self._status("Removing files…",.85)
        try: os.remove(dest)
        except FileNotFoundError: pass
        self._status("Done!",1.0)
        self.after(300,lambda:self.show_done(True,
            "Claisum removed from Discord.\n\n"
            "Your themes and plugin settings are kept in Discord's local storage."))

    # ── Page: Done ─────────────────────────────────────────────────────────
    def show_done(self,ok,msg):
        self._page="done"; self._clear()
        self.btn_back.configure(state="disabled")
        self.btn_next.configure(bg=ACCENT,fg="#fff",state="normal",command=self.go_next)
        self._hdr("✅" if ok else "❌","Done!" if ok else "Error")
        tk.Label(self.content,text=msg,bg=BG,fg=TEXT if ok else ERR,
                 font=("Segoe UI",10),wraplength=490,justify="left").pack(anchor="w")

    # ── Navigation ──────────────────────────────────────────────────────────
    def go_back(self):
        if self._page=="action": self.show_license()
        elif self._page=="done": self.show_action()

    def go_next(self):
        if self._page=="license": self.show_action()
        elif self._page=="action": self.show_installing()
        elif self._page=="done": self.destroy()


if __name__=="__main__":
    App().mainloop()
