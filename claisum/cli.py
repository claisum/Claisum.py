"""Claisum CLI — minimal entry point for installation and updates."""

import subprocess
import sys

import click
from rich.console import Console

from claisum import __version__, __url__
from claisum.discord.paths import find_discord_path
from claisum.discord.injector import inject_into_discord, remove_from_discord

console = Console()

GITHUB_API = "https://api.github.com/repos/claisum/Claisum.py/releases/latest"
GITHUB_ZIP = "https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip"


def print_banner():
    console.print(f"\n[bold cyan]Claisum[/bold cyan] [dim]v{__version__}[/dim]")
    console.print(f"[dim]{__url__}[/dim]\n")


@click.group()
@click.version_option(__version__, prog_name="claisum")
def main():
    """Claisum — Discord theme & plugin manager.

    After installation, manage your themes and plugins directly
    inside Discord Settings — look for the Themes and Plugins tabs!
    """
    pass


@main.command("inject")
def inject():
    """Inject Claisum into Discord (adds Themes & Plugins settings tabs)."""
    print_banner()
    path = find_discord_path()
    if not path:
        console.print("[red]Discord not found.[/red] Please install Discord first.")
        return

    console.print(f"[dim]Found Discord at: {path}[/dim]")
    if inject_into_discord(path):
        console.print("[green]✓ Claisum injected into Discord![/green]")
        console.print("[dim]Restart Discord to see the Themes & Plugins tabs in Settings.[/dim]")
    else:
        console.print("[red]Injection failed.[/red] Try running as Administrator.")


@main.command("remove")
def remove():
    """Remove Claisum from Discord (restores Discord to default).

    This only removes Claisum from Discord files.
    To also uninstall the claisum command itself, run: claisum uninstall
    """
    print_banner()
    path = find_discord_path()
    if not path:
        console.print("[red]Discord not found.[/red]")
        return
    if click.confirm("This will remove Claisum from Discord. Continue?"):
        if remove_from_discord(path):
            console.print("[green]✓ Claisum removed. Discord restored to default.[/green]")
            console.print("[dim]Restart Discord to apply.[/dim]")
            console.print(
                "\n[dim]Note: the [bold]claisum[/bold] command is still installed.\n"
                "To fully remove it run: [bold]claisum uninstall[/bold][/dim]"
            )
        else:
            console.print("[red]Removal failed.[/red]")


@main.command("uninstall")
def uninstall():
    """Fully remove Claisum from Discord AND uninstall this package.

    After this command the 'claisum' command will no longer be available.
    """
    print_banner()

    # Step 1 — remove injection from Discord
    path = find_discord_path()
    if path:
        console.print("[dim]Removing Claisum from Discord...[/dim]")
        if remove_from_discord(path):
            console.print("[green]✓ Claisum removed from Discord.[/green]")
        else:
            console.print("[yellow]⚠ Could not fully remove from Discord files.[/yellow]")
    else:
        console.print("[dim]Discord not found (or already clean).[/dim]")

    # Step 2 — uninstall the pip package
    # We must spawn a *new* process so the currently-running claisum script
    # is not locked when pip tries to delete it.
    if not click.confirm(
        "\nThis will uninstall the [bold]claisum[/bold] command. Continue?"
    ):
        console.print("[dim]Cancelled. Discord injection was still removed.[/dim]")
        return

    console.print("[dim]Uninstalling package...[/dim]")

    # Try python -m pip first, then pip/pip3 directly
    import shutil as _shutil
    candidates = [
        [sys.executable, "-m", "pip", "uninstall", "claisum", "-y"],
    ]
    for pip_name in ("pip", "pip3"):
        p = _shutil.which(pip_name)
        if p:
            candidates.append([p, "uninstall", "claisum", "-y"])

    uninstalled = False
    for cmd in candidates:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                uninstalled = True
                break
        except Exception:
            pass

    if uninstalled:
        console.print(
            "[green]✓ claisum package uninstalled.[/green]\n"
            "[dim]The 'claisum' command is no longer available.[/dim]"
        )
    else:
        console.print(
            "[yellow]⚠ Could not auto-uninstall via pip.[/yellow]\n"
            "[dim]Run manually: [bold]pip uninstall claisum -y[/bold][/dim]"
        )


@main.command("status")
def status():
    """Show whether Claisum is injected into Discord."""
    print_banner()
    path = find_discord_path()
    if path:
        console.print(f"[green]Discord found:[/green] {path}")
        from claisum.discord.injector import is_injected
        if is_injected(path):
            console.print("[green]✓ Claisum is active[/green] — Themes & Plugins tabs visible in Discord Settings.")
        else:
            console.print("[yellow]Claisum is not injected.[/yellow] Run [cyan]claisum inject[/cyan] to activate.")
    else:
        console.print("[red]Discord not found.[/red] Make sure Discord is installed.")


@main.command("update")
def update():
    """Download and install the latest version of Claisum from GitHub."""
    print_banner()
    import urllib.request
    import json

    console.print("[dim]Checking for updates...[/dim]")
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "claisum-updater"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            latest = data.get("tag_name", "unknown")
        if latest != "unknown" and latest.lstrip("v") == __version__.lstrip("v"):
            console.print(f"[green]Already up to date[/green] — v{__version__}")
            return
        console.print(f"[cyan]New version:[/cyan] {latest} (current: v{__version__})")
    except Exception:
        console.print("[dim]Could not check version — updating anyway...[/dim]")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", GITHUB_ZIP],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print("[green]Claisum updated successfully![/green]")
        else:
            console.print("[red]Update failed.[/red]")
            console.print(f"[dim]{result.stderr.strip()}[/dim]")
    except Exception as e:
        console.print(f"[red]Update failed:[/red] {e}")


if __name__ == "__main__":
    main()
