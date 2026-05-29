#!/usr/bin/env python3
"""Claisum Linux Installer — v1.0.0.1  (matches Windows installer feature parity)"""
import sys, os, glob, shutil, threading, subprocess, urllib.request, time, traceback

VERSION = "1.0.0.1"
REPO    = "claisum/Claisum.py"
MARKER  = "claisum_inject"
INJECT  = (
    "// [Claisum] Do NOT remove — uninstall via Claisum_Linux_Setup --remove\n"
    "try{require('./claisum_inject.js');}catch(e){console.error('[Claisum load]',e);}\n"
)

# ── Colour helpers ─────────────────────────────────────────────────────────
RST = "\033[0m"
def col(c, text): return f"{c}{text}{RST}"
RED  = lambda t: col("\033[0;31m", t)
GRN  = lambda t: col("\033[0;32m", t)
YLW  = lambda t: col("\033[1;33m", t)
CYN  = lambda t: col("\033[0;36m", t)
BLD  = lambda t: col("\033[1m",    t)
DIM  = lambda t: col("\033[2m",    t)

# ── Discord path detection ─────────────────────────────────────────────────
def find_discord_indices() -> list[str]:
    bases = [
        os.path.expanduser("~/.config/discord"),
        os.path.expanduser("~/.config/discordptb"),
        os.path.expanduser("~/.config/discordcanary"),
        os.path.expanduser("~/.var/app/com.discordapp.Discord/config/discord"),
        os.path.expanduser("~/snap/discord/current/.config/discord"),
        "/usr/lib/discord",
        "/opt/discord",
        "/usr/share/discord",
    ]
    patterns = [
        "*/modules/discord_desktop_core-*/discord_desktop_core/index.js",
        "app-*/modules/discord_desktop_core-*/discord_desktop_core/index.js",
        "modules/discord_desktop_core-*/discord_desktop_core/index.js",
    ]
    found: list[str] = []
    for base in bases:
        for pat in patterns:
            found.extend(glob.glob(os.path.join(base, pat)))
    return list(dict.fromkeys(sorted(found, reverse=True)))


def discord_running() -> bool:
    try:
        result = subprocess.run(
            ["pgrep", "-x", "Discord"], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False


def kill_discord() -> None:
    for name in ("Discord", "discord", "discord-ptb", "discord-canary"):
        subprocess.run(["pkill", "-f", name], capture_output=True)


def relaunch_discord() -> bool:
    for exe in ("discord", "Discord", "discord-ptb",
                "discord-canary", "discord-stable"):
        if shutil.which(exe):
            subprocess.Popen([exe], start_new_session=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return True
    return False


def get_inject_src() -> str | None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "claisum_inject.js"),
        os.path.normpath(os.path.join(
            script_dir, "..", "claisum", "discord", "claisum_inject.js")),
    ]
    return next((p for p in candidates if os.path.isfile(p)), None)


def _strip_claisum(content: str) -> str:
    return "".join(
        line for line in content.splitlines(keepends=True)
        if MARKER not in line and "[Claisum]" not in line
    ).lstrip("\n")


def do_inject(idx: str, js_src: str | None = None) -> None:
    core = os.path.dirname(idx)
    dest = os.path.join(core, "claisum_inject.js")
    if js_src:
        shutil.copy2(js_src, dest)
    elif not os.path.isfile(dest):
        urllib.request.urlretrieve(
            f"https://raw.githubusercontent.com/{REPO}"
            "/main/claisum/discord/claisum_inject.js", dest)
    with open(idx, "r", encoding="utf-8") as f:
        raw = f.read()
    with open(idx, "w", encoding="utf-8") as f:
        f.write(INJECT + _strip_claisum(raw))


def do_remove(idx: str) -> bool:
    dest = os.path.join(os.path.dirname(idx), "claisum_inject.js")
    with open(idx, "r", encoding="utf-8") as f:
        raw = f.read()
    if MARKER not in raw and "[Claisum]" not in raw:
        return False
    with open(idx, "w", encoding="utf-8") as f:
        f.write(_strip_claisum(raw))
    try:
        os.remove(dest)
    except FileNotFoundError:
        pass
    return True


# ══ Interactive installer ═══════════════════════════════════════════════════

def banner() -> None:
    print(f"""
{BLD('══════════════════════════════════════')}
  {CYN('⚡ Claisum Installer')}  {DIM(f'v{VERSION}')}
  {DIM('https://github.com/' + REPO)}
{BLD('══════════════════════════════════════')}
""")


def step(n: int, total: int, msg: str) -> None:
    print(f"  {DIM(f'[{n}/{total}]')} {msg}")


def ok(msg: str)   -> None: print(f"  {GRN('✓')} {msg}")
def err(msg: str)  -> None: print(f"  {RED('✗')} {msg}", file=sys.stderr)
def warn(msg: str) -> None: print(f"  {YLW('!')} {msg}")
def info(msg: str) -> None: print(f"  {DIM('·')} {msg}")


def _check_status() -> tuple[list[str], bool]:
    """Return (indices, already_injected)."""
    indices = find_discord_indices()
    if not indices:
        return [], False
    with open(indices[0], "r", encoding="utf-8") as f:
        injected = MARKER in f.read()
    return indices, injected


def run_install() -> int:
    """Returns exit code 0=success, 1=failure."""
    banner()
    print(f"{BLD('Installing Claisum')}\n")

    step(1, 5, "Checking for Discord…")
    indices, already = _check_status()
    if not indices:
        err("Discord not found.")
        warn("Install Discord from https://discord.com/download")
        return 1
    ok(f"Found: {indices[0]}")
    if already:
        warn("Claisum already injected — re-injecting (repair).")

    step(2, 5, "Stopping Discord…")
    if discord_running():
        kill_discord()
        time.sleep(1.2)
        ok("Discord closed.")
    else:
        info("Discord was not running.")

    step(3, 5, "Copying claisum_inject.js…")
    js_src = get_inject_src()
    if js_src:
        ok(f"Using local: {js_src}")
    else:
        info("Downloading from GitHub…")

    step(4, 5, "Patching Discord core module…")
    errors: list[str] = []
    patched: list[str] = []
    for idx in indices:
        try:
            do_inject(idx, js_src)
            patched.append(idx)
            ok(f"Patched: {idx}")
        except Exception as e:
            err(f"Failed: {idx}")
            errors.append(str(e))

    step(5, 5, "Verifying…")
    for idx in patched:
        with open(idx, "r", encoding="utf-8") as f:
            if MARKER not in f.read():
                err(f"Verify failed: {idx}")
                return 1
    ok("Patch verified.")

    if errors:
        for e in errors:
            warn(f"  {e}")

    print(f"""
{BLD('══════════════════════════════════════')}
  {GRN('✓ Claisum installed successfully!')}
{BLD('══════════════════════════════════════')}

  Restart Discord to see the {CYN('⚡')} button.
  Keyboard shortcut: {BLD('F8')}
""")

    print("  Restart Discord now? [Y/n] ", end="", flush=True)
    ans = input().strip().lower()
    if ans in ("", "y"):
        if relaunch_discord():
            ok("Discord restarted.")
        else:
            warn("Could not find Discord executable — restart manually.")
    return 0


def run_remove() -> int:
    banner()
    print(f"{BLD('Removing Claisum')}\n")

    step(1, 4, "Checking for Discord…")
    indices, injected = _check_status()
    if not indices:
        err("Discord not found.")
        return 1
    if not injected:
        info("Claisum is not injected — nothing to remove.")
        return 0
    ok(f"Found: {indices[0]}")

    step(2, 4, "Stopping Discord…")
    if discord_running():
        kill_discord()
        time.sleep(1.2)
        ok("Discord closed.")
    else:
        info("Discord was not running.")

    step(3, 4, "Removing injection…")
    for idx in indices:
        removed = do_remove(idx)
        if removed:
            ok(f"Cleaned: {idx}")
        else:
            info(f"Not injected: {idx}")

    step(4, 4, "Verifying…")
    for idx in indices:
        with open(idx, "r", encoding="utf-8") as f:
            if MARKER in f.read():
                err(f"Verify failed — traces remain in {idx}")
                return 1
    ok("Removal verified.")

    print(f"""
{BLD('══════════════════════════════════════')}
  {GRN('✓ Claisum removed successfully!')}
{BLD('══════════════════════════════════════')}

  Discord restored to stock. Restart Discord.
""")

    print("  Restart Discord now? [Y/n] ", end="", flush=True)
    ans = input().strip().lower()
    if ans in ("", "y"):
        if relaunch_discord():
            ok("Discord restarted.")
        else:
            warn("Restart Discord manually.")
    return 0


def run_status() -> int:
    banner()
    indices, _ = _check_status()
    if not indices:
        warn("Discord not found on this system.")
        return 1
    print(f"  {BLD('Claisum status:')}\n")
    for idx in indices:
        try:
            with open(idx, "r", encoding="utf-8") as f:
                injected = MARKER in f.read()
            js_dst = os.path.join(os.path.dirname(idx), "claisum_inject.js")
            js_ok  = os.path.isfile(js_dst)
            status = GRN("injected") if injected else RED("not injected")
            js_txt = GRN("present") if js_ok else RED("missing")
            print(f"  {DIM(idx)}")
            print(f"    Injection : {status}")
            print(f"    inject.js : {js_txt}\n")
        except Exception as e:
            print(f"  {RED(str(e))}\n")
    return 0


if __name__ == "__main__":
    if "--remove" in sys.argv or "-r" in sys.argv:
        sys.exit(run_remove())
    elif "--status" in sys.argv or "-s" in sys.argv:
        sys.exit(run_status())
    else:
        sys.exit(run_install())
