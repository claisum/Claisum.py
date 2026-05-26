"""Discord plugin management."""

import json
import shutil
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from rich.table import Table

from claisum.config import get_plugins_dir, load_config, save_config
from claisum.discord.paths import get_discord_user_data_path

console = Console()

REGISTRY_URL = "https://raw.githubusercontent.com/claisum/Claisum.py/main/plugins/registry.json"

BUILTIN_PLUGINS = {
    "better-notifications": {
        "name": "Better Notifications",
        "description": "Enhanced notification sounds and badges",
        "version": "1.0.0",
        "author": "Claisum",
    },
    "compact-mode": {
        "name": "Compact Mode",
        "description": "Reduces spacing for a denser message layout",
        "version": "1.0.0",
        "author": "Claisum",
    },
    "message-logger": {
        "name": "Message Logger",
        "description": "Keep a local log of deleted/edited messages",
        "version": "1.0.0",
        "author": "Claisum",
    },
}


def list_plugins() -> None:
    """List installed plugins."""
    config = load_config()
    installed = config.get("discord", {}).get("plugins", [])

    table = Table(title="Discord Plugins", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description")
    table.add_column("Version", style="dim")
    table.add_column("Status", style="bold")

    if not installed:
        console.print("[dim]No plugins installed. Run 'claisum discord plugins install <name>'[/dim]")
        return

    for plugin_id in installed:
        meta = BUILTIN_PLUGINS.get(plugin_id, {})
        table.add_row(
            plugin_id,
            meta.get("description", "No description"),
            meta.get("version", "?"),
            "[green]active[/green]",
        )

    console.print(table)


def list_available_plugins() -> None:
    """List all available plugins from the registry."""
    table = Table(title="Available Plugins", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Author", style="dim")

    for plugin_id, meta in BUILTIN_PLUGINS.items():
        table.add_row(
            plugin_id,
            meta.get("name", plugin_id),
            meta.get("description", ""),
            meta.get("author", ""),
        )

    console.print(table)


def install_plugin(plugin_id: str) -> bool:
    """Install a plugin by ID."""
    if plugin_id not in BUILTIN_PLUGINS:
        console.print(f"[red]Plugin '[bold]{plugin_id}[/bold]' not found.[/red]")
        console.print("[dim]Run 'claisum discord plugins available' to see all plugins.[/dim]")
        return False

    config = load_config()
    config.setdefault("discord", {}).setdefault("plugins", [])
    if plugin_id in config["discord"]["plugins"]:
        console.print(f"[yellow]Plugin '[bold]{plugin_id}[/bold]' is already installed.[/yellow]")
        return True

    config["discord"]["plugins"].append(plugin_id)
    save_config(config)

    meta = BUILTIN_PLUGINS[plugin_id]
    console.print(f"[green]Plugin '[bold]{meta['name']}[/bold]' installed.[/green]")
    console.print("[dim]Restart Discord to activate the plugin.[/dim]")
    return True


def remove_plugin(plugin_id: str) -> bool:
    """Remove an installed plugin."""
    config = load_config()
    plugins = config.get("discord", {}).get("plugins", [])

    if plugin_id not in plugins:
        console.print(f"[yellow]Plugin '[bold]{plugin_id}[/bold]' is not installed.[/yellow]")
        return False

    plugins.remove(plugin_id)
    config.setdefault("discord", {})["plugins"] = plugins
    save_config(config)

    console.print(f"[green]Plugin '[bold]{plugin_id}[/bold]' removed.[/green]")
    console.print("[dim]Restart Discord to apply the change.[/dim]")
    return True
