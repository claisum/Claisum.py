"""Claisum Discord injector — patches discord_desktop_core/index.js (v2, safe)"""
import os, glob, shutil, sys

VERSION = "1.0.0.1"
REPO    = "claisum/Claisum.py"
MARKER  = "claisum_inject"

# Safe two-line injection — try/catch ensures Discord never crashes on load
INJECT = (
    "// [Claisum] Do NOT remove — uninstall via Claisum_Setup.exe\n"
    "try{require('./claisum_inject.js');}catch(e){console.error('[Claisum load]',e);}\n"
)


def _find_indices() -> list[str]:
    """Return all discord_desktop_core index.js paths on this system."""
    indices: list[str] = []

    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        names = ("Discord", "DiscordPTB", "DiscordCanary",
                 "discordptb", "discordcanary")
        bases = [os.path.join(local, n) for n in names]
    else:
        bases = [
            os.path.expanduser("~/.config/discord"),
            os.path.expanduser("~/.config/discordptb"),
            os.path.expanduser("~/.config/discordcanary"),
            "/opt/discord",
            "/usr/lib/discord",
            "/usr/share/discord",
        ]

    patterns = [
        "app-*/modules/discord_desktop_core-*/discord_desktop_core/index.js",
        "modules/discord_desktop_core-*/discord_desktop_core/index.js",
        "resources/app.asar.unpacked/node_modules/discord_desktop_core/index.js",
    ]
    for base in bases:
        for pat in patterns:
            indices.extend(glob.glob(os.path.join(base, pat)))

    return list(dict.fromkeys(indices))   # deduplicate, preserve order


def _strip_claisum(content: str) -> str:
    """Remove every line written by Claisum (idempotent)."""
    return "".join(
        line for line in content.splitlines(keepends=True)
        if MARKER not in line and "[Claisum]" not in line
    ).lstrip("\n")


# ── Public API ─────────────────────────────────────────────────────────────

def find_discord_indices() -> list[str]:
    """Return list of all found Discord core index.js paths."""
    return _find_indices()


def inject_into_discord(inject_js_src: str | None = None) -> list[str]:
    """
    Inject Claisum into all found Discord installations.

    Args:
        inject_js_src: Path to claisum_inject.js to copy next to index.js.
                       If None, assumes the file is already in place or
                       will be downloaded on first Discord start.

    Returns:
        List of patched index.js paths.

    Raises:
        FileNotFoundError: If no Discord installation is found.
    """
    indices = _find_indices()
    if not indices:
        raise FileNotFoundError(
            "No Discord installation found.\n"
            "Install Discord from https://discord.com/download")

    patched: list[str] = []
    for idx in indices:
        core = os.path.dirname(idx)
        dest = os.path.join(core, "claisum_inject.js")

        if inject_js_src and os.path.isfile(inject_js_src):
            shutil.copy2(inject_js_src, dest)

        with open(idx, "r", encoding="utf-8") as f:
            raw = f.read()

        cleaned = _strip_claisum(raw)          # idempotent — repair works
        with open(idx, "w", encoding="utf-8") as f:
            f.write(INJECT + cleaned)

        patched.append(idx)

    return patched


def remove_injection(index_path: str) -> bool:
    """
    Remove Claisum from a single index.js.

    Returns:
        True if injection was found and removed, False if not present.
    """
    with open(index_path, "r", encoding="utf-8") as f:
        raw = f.read()

    if MARKER not in raw and "[Claisum]" not in raw:
        return False

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(_strip_claisum(raw))

    return True


def uninstall_from_discord() -> list[str]:
    """
    Remove Claisum from all Discord installations.

    Returns:
        List of index.js paths that were cleaned.
    """
    indices = _find_indices()
    removed: list[str] = []

    for idx in indices:
        core   = os.path.dirname(idx)
        js_dst = os.path.join(core, "claisum_inject.js")

        if remove_injection(idx):
            removed.append(idx)

        try:
            os.remove(js_dst)
        except FileNotFoundError:
            pass

    return removed


def get_status() -> dict[str, bool | None]:
    """
    Check injection status across all Discord installations.

    Returns:
        {index_path: True if injected, False if not, None if unreadable}
    """
    result: dict[str, bool | None] = {}
    for idx in _find_indices():
        try:
            with open(idx, "r", encoding="utf-8") as f:
                result[idx] = MARKER in f.read()
        except Exception:
            result[idx] = None
    return result
