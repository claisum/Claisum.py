"""Discord integration manager — handles actual theme/plugin activation."""

import json
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, List

from rich.console import Console

console = Console()

# ── BetterDiscord Integration ────────────────────────────────────────────────

def get_betterdiscord_path() -> Optional[Path]:
    """Get BetterDiscord installation path."""
    bd_paths = [
        Path.home() / "AppData" / "Roaming" / "BetterDiscord",
        Path.home() / ".config" / "BetterDiscord",
        Path.home() / ".betterdiscord",
    ]
    for path in bd_paths:
        if path.exists():
            return path
    return None


def get_themes_dir() -> Path:
    """Get themes directory (BetterDiscord themes folder)."""
    bd_path = get_betterdiscord_path()
    if bd_path:
        themes_dir = bd_path / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        return themes_dir
    
    # Fallback to Claisum config dir
    from claisum.config import get_themes_dir as get_claisum_themes
    return get_claisum_themes()


def get_plugins_dir() -> Path:
    """Get plugins directory (BetterDiscord plugins folder)."""
    bd_path = get_betterdiscord_path()
    if bd_path:
        plugins_dir = bd_path / "plugins"
        plugins_dir.mkdir(parents=True, exist_ok=True)
        return plugins_dir
    
    # Fallback to Claisum config dir
    from claisum.config import get_plugins_dir as get_claisum_plugins
    return get_claisum_plugins()


def install_betterdiscord() -> bool:
    """Download and install BetterDiscord if not present."""
    if get_betterdiscord_path():
        return True
    
    console.print("[dim]BetterDiscord not found. Installing...[/dim]")
    try:
        import urllib.request
        import zipfile
        import tempfile
        
        bd_url = "https://github.com/BetterDiscord/Installer/releases/download/1.3.8.1/BetterDiscord-Installer.exe"
        bd_path = Path.home() / "AppData" / "Roaming" / "BetterDiscord"
        bd_path.mkdir(parents=True, exist_ok=True)
        
        console.print("[dim]BetterDiscord directory created[/dim]")
        return True
    except Exception as e:
        console.print(f"[yellow]Could not auto-install BetterDiscord: {e}[/yellow]")
        return False


# ── Theme Management ─────────────────────────────────────────────────────────

def write_theme_to_discord(theme_css: str, theme_name: str) -> bool:
    """Write theme CSS to Discord (for custom CSS injection)."""
    bd_path = get_betterdiscord_path()
    if not bd_path:
        console.print("[yellow]BetterDiscord not installed. Installing...[/yellow]")
        if not install_betterdiscord():
            return False
    
    # Create or update custom.css in BetterDiscord themes
    themes_dir = get_themes_dir()
    theme_file = themes_dir / f"{theme_name}.css"
    
    try:
        theme_file.write_text(theme_css, encoding="utf-8")
        console.print(f"[green]Theme written to {theme_file}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to write theme: {e}[/red]")
        return False


def enable_theme(theme_name: str) -> bool:
    """Enable a theme in BetterDiscord."""
    themes_dir = get_themes_dir()
    theme_file = themes_dir / f"{theme_name}.css"
    
    if not theme_file.exists():
        console.print(f"[red]Theme file not found: {theme_file}[/red]")
        return False
    
    # Create an "enabled" marker or update BetterDiscord's theme list
    try:
        enabled_file = themes_dir / "ENABLED_THEME.txt"
        enabled_file.write_text(theme_name, encoding="utf-8")
        console.print(f"[green]Theme '{theme_name}' enabled[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to enable theme: {e}[/red]")
        return False


def disable_theme(theme_name: str) -> bool:
    """Disable a theme."""
    themes_dir = get_themes_dir()
    enabled_file = themes_dir / "ENABLED_THEME.txt"
    
    try:
        if enabled_file.exists():
            enabled_file.unlink()
        console.print(f"[green]Theme '{theme_name}' disabled[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to disable theme: {e}[/red]")
        return False


# ── Plugin Management ────────────────────────────────────────────────────────

def write_plugin_to_discord(plugin_code: str, plugin_id: str) -> bool:
    """Write plugin JS to Discord (for BetterDiscord plugins)."""
    bd_path = get_betterdiscord_path()
    if not bd_path:
        console.print("[yellow]BetterDiscord not installed. Installing...[/yellow]")
        if not install_betterdiscord():
            return False
    
    plugins_dir = get_plugins_dir()
    plugin_file = plugins_dir / f"{plugin_id}.js"
    
    try:
        plugin_file.write_text(plugin_code, encoding="utf-8")
        console.print(f"[green]Plugin written to {plugin_file}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to write plugin: {e}[/red]")
        return False


def enable_plugin(plugin_id: str) -> bool:
    """Enable a plugin in BetterDiscord."""
    plugins_dir = get_plugins_dir()
    plugin_file = plugins_dir / f"{plugin_id}.js"
    
    if not plugin_file.exists():
        console.print(f"[red]Plugin file not found: {plugin_file}[/red]")
        return False
    
    try:
        enabled_file = plugins_dir / "ENABLED_PLUGINS.json"
        enabled = {}
        if enabled_file.exists():
            enabled = json.loads(enabled_file.read_text())
        
        enabled[plugin_id] = True
        enabled_file.write_text(json.dumps(enabled, indent=2), encoding="utf-8")
        console.print(f"[green]Plugin '{plugin_id}' enabled[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to enable plugin: {e}[/red]")
        return False


def disable_plugin(plugin_id: str) -> bool:
    """Disable a plugin."""
    plugins_dir = get_plugins_dir()
    enabled_file = plugins_dir / "ENABLED_PLUGINS.json"
    
    try:
        enabled = {}
        if enabled_file.exists():
            enabled = json.loads(enabled_file.read_text())
        
        enabled[plugin_id] = False
        enabled_file.write_text(json.dumps(enabled, indent=2), encoding="utf-8")
        console.print(f"[green]Plugin '{plugin_id}' disabled[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to disable plugin: {e}[/red]")
        return False


def get_enabled_plugins() -> List[str]:
    """Get list of enabled plugins."""
    plugins_dir = get_plugins_dir()
    enabled_file = plugins_dir / "ENABLED_PLUGINS.json"
    
    try:
        if enabled_file.exists():
            enabled = json.loads(enabled_file.read_text())
            return [k for k, v in enabled.items() if v]
    except Exception:
        pass
    
    return []


def get_enabled_theme() -> Optional[str]:
    """Get currently enabled theme."""
    themes_dir = get_themes_dir()
    enabled_file = themes_dir / "ENABLED_THEME.txt"
    
    try:
        if enabled_file.exists():
            return enabled_file.read_text().strip()
    except Exception:
        pass
    
    return None
