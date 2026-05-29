"""Claisum Discord manager — native path helpers, no BetterDiscord required."""
import json
import os
import platform
from pathlib import Path
from typing import Optional

from rich.console import Console

from claisum.config import get_plugins_dir, get_themes_dir

console = Console()


# ── Discord path detection ─────────────────────────────────────────────────

def _discord_config_dirs() -> list[Path]:
    system = platform.system()
    if system == "Windows":
        local = os.environ.get("LOCALAPPDATA", "")
        return [
            Path(local) / name
            for name in ("Discord", "DiscordPTB", "DiscordCanary",
                         "discordptb", "discordcanary")
        ]
    elif system == "Linux":
        home = Path.home()
        return [
            home / ".config" / "discord",
            home / ".config" / "discordptb",
            home / ".config" / "discordcanary",
            home / ".var/app/com.discordapp.Discord/config/discord",
            home / "snap/discord/current/.config/discord",
            Path("/usr/lib/discord"),
            Path("/opt/discord"),
            Path("/usr/share/discord"),
        ]
    elif system == "Darwin":
        home = Path.home()
        return [
            home / "Library/Application Support/discord",
            home / "Library/Application Support/discordcanary",
        ]
    return []


def find_discord_core_index() -> Optional[Path]:
    """Return the newest discord_desktop_core/index.js, or None."""
    import glob as _glob
    candidates: list[str] = []
    for base in _discord_config_dirs():
        for pat in (
            "app-*/modules/discord_desktop_core-*/discord_desktop_core/index.js",
            "*/modules/discord_desktop_core-*/discord_desktop_core/index.js",
        ):
            candidates.extend(_glob.glob(str(base / pat)))
    return Path(sorted(candidates)[-1]) if candidates else None


# ── Theme helpers (CLI-level, separate from localStorage-based inject.js) ──

def get_themes_dir() -> Path:  # re-exported for callers that import from manager
    from claisum.config import get_themes_dir as _gtd
    return _gtd()


def write_theme_to_discord(theme_css: str, theme_name: str) -> bool:
    """Write a CSS theme file to Claisum's themes directory."""
    try:
        theme_file = get_themes_dir() / f"{theme_name}.css"
        theme_file.write_text(theme_css, encoding="utf-8")
        console.print(f"[green]Theme saved → {theme_file}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to save theme: {e}[/red]")
        return False


def enable_theme(theme_name: str) -> bool:
    marker = get_themes_dir() / "ENABLED_THEME.txt"
    try:
        marker.write_text(theme_name, encoding="utf-8")
        return True
    except Exception as e:
        console.print(f"[red]Could not enable theme: {e}[/red]")
        return False


def disable_theme(theme_name: str) -> bool:
    marker = get_themes_dir() / "ENABLED_THEME.txt"
    try:
        if marker.exists():
            marker.unlink()
        return True
    except Exception as e:
        console.print(f"[red]Could not disable theme: {e}[/red]")
        return False


def get_enabled_theme() -> Optional[str]:
    marker = get_themes_dir() / "ENABLED_THEME.txt"
    try:
        return marker.read_text().strip() if marker.exists() else None
    except Exception:
        return None


# ── Plugin helpers ──────────────────────────────────────────────────────────

def write_plugin_to_discord(plugin_code: str, plugin_id: str) -> bool:
    try:
        plugin_file = get_plugins_dir() / f"{plugin_id}.js"
        plugin_file.write_text(plugin_code, encoding="utf-8")
        console.print(f"[green]Plugin saved → {plugin_file}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to save plugin: {e}[/red]")
        return False


def _enabled_plugins_file() -> Path:
    return get_plugins_dir() / "ENABLED_PLUGINS.json"


def _load_enabled_plugins() -> dict[str, bool]:
    f = _enabled_plugins_file()
    try:
        return json.loads(f.read_text()) if f.exists() else {}
    except Exception:
        return {}


def _save_enabled_plugins(data: dict[str, bool]) -> None:
    _enabled_plugins_file().write_text(
        json.dumps(data, indent=2), encoding="utf-8")


def enable_plugin(plugin_id: str) -> bool:
    try:
        enabled = _load_enabled_plugins()
        enabled[plugin_id] = True
        _save_enabled_plugins(enabled)
        return True
    except Exception as e:
        console.print(f"[red]Could not enable plugin: {e}[/red]")
        return False


def disable_plugin(plugin_id: str) -> bool:
    try:
        enabled = _load_enabled_plugins()
        enabled[plugin_id] = False
        _save_enabled_plugins(enabled)
        return True
    except Exception as e:
        console.print(f"[red]Could not disable plugin: {e}[/red]")
        return False


def get_enabled_plugins() -> list[str]:
    return [k for k, v in _load_enabled_plugins().items() if v]
