"""Discord injector — patches Discord to load Claisum's settings tabs."""

import os
import shutil
import platform
from pathlib import Path
from typing import Optional

PRELOAD_MARKER = "// [Claisum Injected]"

JS_LOADER = """
// [Claisum Injected]
try {
  const path = require('path');
  const fs   = require('fs');
  const js   = fs.readFileSync(
    path.join(__dirname, '..', '..', 'claisum_inject.js'), 'utf8');
  // Wait for Discord to fully load then inject
  window.addEventListener('load', () => {
    setTimeout(() => { try { eval(js); } catch(e) { console.error('[Claisum]', e); } }, 2000);
  });
} catch(e) { console.error('[Claisum preload]', e); }
"""


def find_discord_preload(discord_path: str) -> Optional[Path]:
    """Find Discord's preload.js or index.js to patch."""
    base = Path(discord_path).parent
    candidates = [
        base / "resources" / "app" / "preload.js",
        base / "resources" / "app.asar.unpacked" / "app" / "preload.js",
    ]
    # Also search app-* directories on Windows
    local = os.environ.get("LOCALAPPDATA", "")
    for variant in ["Discord", "DiscordPTB", "DiscordCanary"]:
        variant_path = Path(local) / variant
        if variant_path.exists():
            for app_dir in sorted(variant_path.glob("app-*"), reverse=True):
                p = app_dir / "modules" / "discord_desktop_core-1" / "discord_desktop_core" / "index.js"
                if p.exists():
                    candidates.insert(0, p)
                    break

    for path in candidates:
        if path.exists():
            return path
    return None


def _get_inject_js_path(discord_path: str) -> Optional[Path]:
    """Return path to the claisum_inject.js file to copy into Discord's resources."""
    import importlib.resources
    import claisum.discord as pkg
    pkg_dir = Path(pkg.__file__).parent
    js = pkg_dir / "claisum_inject.js"
    return js if js.exists() else None


def inject_into_discord(discord_path: str) -> bool:
    """Patch Discord to load Claisum on startup."""
    target = find_discord_preload(discord_path)
    if target is None:
        return False

    try:
        content = target.read_text(encoding="utf-8")
        if PRELOAD_MARKER in content:
            return True  # already injected

        # Copy claisum_inject.js next to the target file
        js_src = _get_inject_js_path(discord_path)
        if js_src:
            dst = target.parent / "claisum_inject.js"
            shutil.copy2(str(js_src), str(dst))

        patched = content + "\n" + JS_LOADER
        target.write_text(patched, encoding="utf-8")
        return True
    except PermissionError:
        return False
    except Exception:
        return False


def remove_from_discord(discord_path: str) -> bool:
    """Remove Claisum patch from Discord."""
    target = find_discord_preload(discord_path)
    if target is None:
        return False

    try:
        content = target.read_text(encoding="utf-8")
        if PRELOAD_MARKER not in content:
            return True  # not injected

        idx = content.find("\n" + PRELOAD_MARKER)
        if idx == -1:
            idx = content.find(PRELOAD_MARKER)
        patched = content[:idx] if idx != -1 else content.replace(JS_LOADER, "")
        target.write_text(patched.rstrip() + "\n", encoding="utf-8")

        # Remove copied JS file
        inject_file = target.parent / "claisum_inject.js"
        if inject_file.exists():
            inject_file.unlink()

        return True
    except Exception:
        return False


def is_injected(discord_path: str) -> bool:
    """Check whether Claisum is currently injected into Discord."""
    target = find_discord_preload(discord_path)
    if target is None:
        return False
    try:
        return PRELOAD_MARKER in target.read_text(encoding="utf-8")
    except Exception:
        return False
