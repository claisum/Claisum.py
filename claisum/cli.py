"""Claisum CLI — main entry point."""

import subprocess
import sys

import click
from rich.console import Console
from rich import print as rprint

from claisum import __version__, __url__
from claisum.discord import themes as discord_themes
from claisum.discord import plugins as discord_plugins
from claisum.discord.paths import find_discord_path

console = Console()

GITHUB_ZIP = "https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip"
GITHUB_API = "https://api.github.com/repos/claisum/Claisum.py/releases/latest"


def print_banner():
    console.print(f"\n[bold cyan]Claisum[/bold cyan] [dim]v{__version__}[/dim]")
    console.print(f"[dim]{__url__}[/dim]\n")


@click.group()
@click.version_option(__version__, prog_name="claisum")
def main():
    """Claisum — customize your apps the way you want them."""
    pass


@main.command("update")
def update():
    """Download and install the latest version of Claisum from GitHub."""
    print_banner()

    import urllib.request
    import json

    # Check latest release version via GitHub API
    console.print("[dim]Checking for updates...[/dim]")
    try:
        req = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": "claisum-updater"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest = data.get("tag_name", "unknown")

        if latest != "unknown" and latest.lstrip("v") == __version__.lstrip("v"):
            console.print(f"[green]Already up to date[/green] — v{__version__}")
            return
        else:
            console.print(f"[cyan]New version available:[/cyan] {latest} (current: v{__version__})")
    except Exception:
        console.print("[dim]Could not check version — updating anyway...[/dim]")

    # Reinstall from GitHub ZIP
    console.print("[dim]Downloading latest version from GitHub...[/dim]")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", GITHUB_ZIP],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            console.print("[green]Claisum updated successfully![/green]")
            console.print("[dim]Restart your terminal for the changes to take effect.[/dim]")
        else:
            console.print("[red]Update failed.[/red]")
            console.print(f"[dim]{result.stderr.strip()}[/dim]")
    except Exception as e:
        console.print(f"[red]Update failed:[/red] {e}")


# ── Discord ────────────────────────────────────────────────────────────────────

@main.group()
def discord():
    """Commands for customizing Discord."""
    pass


# ── Discord Themes ─────────────────────────────────────────────────────────────

@discord.group()
def themes():
    """Manage Discord themes."""
    pass


@themes.command("list")
def themes_list():
    """List all available themes."""
    print_banner()
    discord_themes.list_themes()


@themes.command("apply")
@click.argument("theme_name")
def themes_apply(theme_name: str):
    """Apply a theme to Discord.

    THEME_NAME is the ID of the theme to apply (e.g. midnight, dracula, catppuccin).
    Run 'claisum discord themes list' to see all available themes.
    """
    print_banner()
    discord_themes.apply_theme(theme_name)


@themes.command("remove")
def themes_remove():
    """Remove the currently active theme."""
    print_banner()
    discord_themes.remove_theme()


# ── Discord Plugins ────────────────────────────────────────────────────────────

@discord.group()
def plugins():
    """Manage Discord plugins."""
    pass


@plugins.command("list")
def plugins_list():
    """List installed plugins."""
    print_banner()
    discord_plugins.list_plugins()


@plugins.command("available")
def plugins_available():
    """List all available plugins."""
    print_banner()
    discord_plugins.list_available_plugins()


@plugins.command("install")
@click.argument("plugin_id")
def plugins_install(plugin_id: str):
    """Install a plugin.

    PLUGIN_ID is the ID of the plugin (e.g. better-notifications, compact-mode).
    Run 'claisum discord plugins available' to see all plugins.
    """
    print_banner()
    discord_plugins.install_plugin(plugin_id)


@plugins.command("remove")
@click.argument("plugin_id")
def plugins_remove(plugin_id: str):
    """Remove an installed plugin.

    PLUGIN_ID is the ID of the plugin to remove.
    """
    print_banner()
    discord_plugins.remove_plugin(plugin_id)


# ── Discord Status ─────────────────────────────────────────────────────────────

@discord.command("status")
def discord_status():
    """Show current Discord configuration."""
    print_banner()
    path = find_discord_path()
    if path:
        console.print(f"[green]Discord found:[/green] {path}")
    else:
        console.print("[red]Discord not found.[/red] Make sure Discord is installed.")

    from claisum.config import load_config
    config = load_config()
    discord_cfg = config.get("discord", {})

    active_theme = discord_cfg.get("active_theme")
    if active_theme:
        console.print(f"[cyan]Active theme:[/cyan] {active_theme}")
    else:
        console.print("[dim]No theme active.[/dim]")

    installed_plugins = discord_cfg.get("plugins", [])
    if installed_plugins:
        console.print(f"[cyan]Installed plugins:[/cyan] {', '.join(installed_plugins)}")
    else:
        console.print("[dim]No plugins installed.[/dim]")


@discord.command("reset")
def discord_reset():
    """Reset Discord to defaults (remove all Claisum customizations)."""
    print_banner()
    if click.confirm("This will remove all themes and plugins. Continue?"):
        discord_themes.remove_theme()
        from claisum.config import load_config, save_config
        config = load_config()
        config["discord"] = {}
        save_config(config)
        console.print("[green]Discord reset to defaults.[/green]")


if __name__ == "__main__":
    main()
