#!/usr/bin/env python3
"""Claisum Linux Setup — injects Themes & Plugins tabs into Discord."""

import os, sys, shutil, subprocess, time
from pathlib import Path

MARKER = "// [Claisum Injected]"

def col(c): return {"grn":"\033[92m","red":"\033[91m","ylw":"\033[93m","cyn":"\033[96m","rst":"\033[0m"}.get(c,"")
def p(msg, c=""): print(col(c)+msg+col("rst"))

def find_discord_core():
    bases = [
        Path.home()/".config/discord",
        Path("/usr/lib/discord"), Path("/opt/discord"), Path("/usr/share/discord"),
        Path.home()/".var/app/com.discordapp.Discord/config/discord",
        Path.home()/"snap/discord/current/.config/discord",
    ]
    for base in bases:
        if not base.exists(): continue
        for core in sorted(base.rglob("discord_desktop_core/index.js"), reverse=True):
            return str(core)
    return None

def inject(js_src):
    core = find_discord_core()
    if not core: return False, "Discord core not found"
    content = open(core, encoding="utf-8").read()
    if MARKER in content: return True, "Already injected"
    dst = os.path.join(os.path.dirname(core), "claisum_inject.js")
    shutil.copy2(js_src, dst)
    loader = """
""" + MARKER + """
try {
  const fs=require('fs'),path=require('path');
  const js=fs.readFileSync(path.join(__dirname,'claisum_inject.js'),'utf8');
  window.addEventListener('load',()=>{setTimeout(()=>{try{eval(js)}catch(e){console.error('[Claisum]',e)}},2000)});
}catch(e){console.error('[Claisum preload]',e)}
"""
    with open(core,"a",encoding="utf-8") as f: f.write(loader)
    return True, core

def remove():
    core = find_discord_core()
    if not core: return False, "Discord core not found"
    content = open(core, encoding="utf-8").read()
    if MARKER not in content: return True, "Not injected"
    idx = content.find("\n" + MARKER)
    patched = content[:idx] if idx != -1 else content
    with open(core,"w",encoding="utf-8") as f: f.write(patched.rstrip()+"\n")
    dst = os.path.join(os.path.dirname(core), "claisum_inject.js")
    if os.path.isfile(dst): os.remove(dst)
    return True, "Removed"

def main():
    p("\nClaisum Linux Setup","cyn")
    p("Discord Theme & Plugin Manager\n")
    if "--remove" in sys.argv:
        ok, msg = remove()
        p(("✓ " if ok else "✗ ")+msg, "grn" if ok else "red")
        if ok: p("Restart Discord to apply.","ylw")
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    js_src = os.path.join(script_dir,"claisum_inject.js")
    if not os.path.isfile(js_src):
        p("✗ claisum_inject.js not found next to this script.","red")
        sys.exit(1)
    p("Checking for Discord...")
    core = find_discord_core()
    if core: p(f"✓ Found: {core}","grn")
    else:
        p("✗ Discord not found. Install from https://discord.com/download","red")
        sys.exit(1)
    p("Injecting Claisum...")
    ok, msg = inject(js_src)
    if ok:
        p(f"✓ {msg}","grn")
        p("✓ Themes & Plugins tabs added to Discord Settings!","grn")
    else:
        p(f"✗ {msg}","red")
        p("  Try: sudo python3 Claisum_Linux_Setup.py","ylw")
        sys.exit(1)
    p("Restarting Discord...")
    subprocess.run(["pkill","-f","discord"],capture_output=True)
    time.sleep(1)
    for exe in ["discord","Discord","discord-stable","discord-ptb","discord-canary"]:
        if shutil.which(exe):
            subprocess.Popen([exe],start_new_session=True)
            p("✓ Discord restarted","grn"); break
    else: p("→ Please restart Discord manually.","ylw")
    p("\nDone! Open Discord → Settings → look for Themes and Plugins tabs","grn")

if __name__=="__main__":
    main()
