"""Discord plugin management with BetterDiscord integration."""

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from claisum.config import load_config, save_config
from claisum.discord import manager, plugin_engine

console = Console()


def list_plugins() -> None:
    """List installed plugins."""
    enabled = manager.get_enabled_plugins()

    table = Table(title="Installed Plugins", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Status", style="bold")

    if not enabled:
        console.print("[dim]No plugins installed. Run 'claisum discord plugins install <id>'[/dim]")
        return

    for plugin_id in enabled:
        meta = plugin_engine.BUILTIN_PLUGINS.get(plugin_id, {})
        table.add_row(
            plugin_id,
            meta.get("name", plugin_id),
            "[green]active[/green]",
        )

    console.print(table)


def list_available_plugins() -> None:
    """List all available plugins."""
    table = Table(title="Available Plugins", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Author", style="dim")

    for plugin_id, meta in plugin_engine.BUILTIN_PLUGINS.items():
        table.add_row(
            plugin_id,
            meta.get("name", plugin_id),
            meta.get("description", ""),
            meta.get("author", ""),
        )

    console.print(table)


def install_plugin(plugin_id: str) -> bool:
    """Install and activate a plugin."""
    if plugin_id not in plugin_engine.BUILTIN_PLUGINS:
        console.print(f"[red]Plugin '{plugin_id}' not found.[/red]")
        console.print("[dim]Run 'claisum discord plugins available' to see all plugins.[/dim]")
        return False

    meta = plugin_engine.BUILTIN_PLUGINS[plugin_id]
    plugin_code = meta.get("code", "")

    # Write plugin to BetterDiscord
    if not manager.write_plugin_to_discord(plugin_code, plugin_id):
        return False

    # Enable the plugin
    if not manager.enable_plugin(plugin_id):
        return False

    # Save to config
    config = load_config()
    config.setdefault("discord", {}).setdefault("plugins", [])
    if plugin_id not in config["discord"]["plugins"]:
        config["discord"]["plugins"].append(plugin_id)
    save_config(config)

    console.print(f"[green]Plugin '{meta['name']}' installed and enabled![/green]")
    console.print("[dim]Restart Discord to activate the plugin.[/dim]")
    return True


def remove_plugin(plugin_id: str) -> bool:
    """Remove and disable a plugin."""
    enabled = manager.get_enabled_plugins()

    if plugin_id not in enabled:
        console.print(f"[yellow]Plugin '{plugin_id}' is not installed.[/yellow]")
        return False

    # Disable the plugin
    if not manager.disable_plugin(plugin_id):
        return False

    # Remove from config
    config = load_config()
    plugins = config.get("discord", {}).get("plugins", [])
    if plugin_id in plugins:
        plugins.remove(plugin_id)
        config.setdefault("discord", {})["plugins"] = plugins
        save_config(config)

    console.print(f"[green]Plugin '{plugin_id}' removed![/green]")
    console.print("[dim]Restart Discord to apply the change.[/dim]")
    return True


def get_status() -> dict:
    """Get current plugin/theme status."""
    return {
        "active_theme": manager.get_enabled_theme(),
        "enabled_plugins": manager.get_enabled_plugins(),
    }
