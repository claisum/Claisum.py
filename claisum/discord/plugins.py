"""Discord plugin management — CLI interface."""
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from claisum.config import get_plugins_dir, load_config, save_config

console = Console()

# ── Built-in plugins (metadata only; JS is in plugin_engine.py) ───────────
BUILTIN_PLUGINS: dict[str, dict] = {
    "compact-mode": {
        "name": "Compact Mode",
        "description": "Tighter message layout — more content visible at once",
        "version": "1.0.0",
        "author": "Claisum",
    },
    "square-corners": {
        "name": "Square Corners",
        "description": "Removes all border-radius for a sharp, modern look",
        "version": "1.0.0",
        "author": "Claisum",
    },
    "big-emoji": {
        "name": "Big Emoji",
        "description": "Enlarges solo emoji to 48 px",
        "version": "1.0.0",
        "author": "Claisum",
    },
    "hide-game-activity": {
        "name": "Hide Game Activity",
        "description": "Hides the 'playing a game' status bar",
        "version": "1.0.0",
        "author": "Claisum",
    },
    "hide-avatars": {
        "name": "Hide Avatars",
        "description": "Removes all user avatars to reduce visual noise",
        "version": "1.0.0",
        "author": "Claisum",
    },
}


def list_plugins() -> None:
    cfg = load_config()
    installed: list[str] = cfg.get("discord", {}).get("plugins", [])

    table = Table(title="Installed Plugins", header_style="bold magenta")
    table.add_column("ID",          style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Version",     style="dim")
    table.add_column("Status",      style="bold")

    if not installed:
        console.print("[dim]No plugins installed.[/dim]")
        console.print("[dim]Run 'claisum discord plugins available' to see what's available.[/dim]")
        return

    for pid in installed:
        meta = BUILTIN_PLUGINS.get(pid, {})
        table.add_row(pid,
                      meta.get("name", pid),
                      meta.get("description", ""),
                      meta.get("version", "?"),
                      "[green]active[/green]")
    console.print(table)


def list_available_plugins() -> None:
    table = Table(title="Available Plugins", header_style="bold magenta")
    table.add_column("ID",          style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Author",      style="dim")

    for pid, meta in BUILTIN_PLUGINS.items():
        table.add_row(pid, meta["name"], meta["description"], meta["author"])
    console.print(table)


def install_plugin(plugin_id: str) -> bool:
    if plugin_id not in BUILTIN_PLUGINS:
        console.print(f"[red]Plugin '{plugin_id}' not found.[/red]")
        console.print("[dim]Run 'claisum discord plugins available' to see all plugins.[/dim]")
        return False

    cfg = load_config()
    cfg.setdefault("discord", {}).setdefault("plugins", [])
    if plugin_id in cfg["discord"]["plugins"]:
        console.print(f"[yellow]'{plugin_id}' is already installed.[/yellow]")
        return True

    cfg["discord"]["plugins"].append(plugin_id)
    save_config(cfg)
    console.print(f"[green]Plugin '{BUILTIN_PLUGINS[plugin_id]['name']}' installed.[/green]")
    console.print("[dim]Restart Discord to activate.[/dim]")
    return True


def remove_plugin(plugin_id: str) -> bool:
    cfg = load_config()
    plugins: list[str] = cfg.get("discord", {}).get("plugins", [])
    if plugin_id not in plugins:
        console.print(f"[yellow]'{plugin_id}' is not installed.[/yellow]")
        return False

    plugins.remove(plugin_id)
    cfg.setdefault("discord", {})["plugins"] = plugins
    save_config(cfg)
    console.print(f"[green]'{plugin_id}' removed. Restart Discord to apply.[/green]")
    return True
