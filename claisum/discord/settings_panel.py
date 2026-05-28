"""Discord settings panel — two injected tabs: Plugins and Themes."""

# This JavaScript is injected into Discord's Electron renderer.
# It adds two separate Settings tabs: "Plugins" and "Themes".
# Loaded by the injector and written into Discord's preload script.

import importlib.resources
import pathlib

DISCORD_SETTINGS_JS = None

def _load_js():
    global DISCORD_SETTINGS_JS
    if DISCORD_SETTINGS_JS is not None:
        return DISCORD_SETTINGS_JS
    js_path = pathlib.Path(__file__).parent / "claisum_inject.js"
    if js_path.exists():
        DISCORD_SETTINGS_JS = js_path.read_text(encoding="utf-8")
    return DISCORD_SETTINGS_JS

def get_settings_js() -> str:
    """Return the full JS string to inject into Discord."""
    return _load_js() or ""
