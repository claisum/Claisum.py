"""Discord theme management with BetterDiscord integration."""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from claisum.config import load_config, save_config
from claisum.discord import manager

console = Console()

# ── Built-in Themes ───────────────────────────────────────────────────────────

BUILTIN_THEMES = {
    "midnight": {
        "name": "Midnight",
        "description": "Deep dark theme with blue accents",
        "author": "Claisum",
        "css": """
/* Midnight Theme by Claisum */
:root {
  --background-primary: #0d0f12;
  --background-secondary: #101316;
  --background-secondary-alt: #0d0f12;
  --background-tertiary: #08090b;
  --background-accent: #1a1d24;
  --background-floating: #101316;
  --background-mobile-primary: #0d0f12;
  --background-mobile-secondary: #101316;
  --background-modifier-hover: rgba(79,84,92,0.16);
  --background-modifier-active: rgba(79,84,92,0.24);
  --background-modifier-selected: rgba(79,84,92,0.32);
  --background-modifier-accent: rgba(79,84,92,0.24);
  --channeltextarea-background: #1a1d24;
  --text-normal: #dcddde;
  --text-muted: #72767d;
  --text-link: #5865f2;
  --header-primary: #ffffff;
  --header-secondary: #b9bbbe;
  --interactive-normal: #b9bbbe;
  --interactive-hover: #dcddde;
  --interactive-active: #ffffff;
  --interactive-muted: #4f545c;
}
""",
    },
    "dracula": {
        "name": "Dracula",
        "description": "The classic Dracula color scheme",
        "author": "Claisum",
        "css": """
/* Dracula Theme by Claisum */
:root {
  --background-primary: #282a36;
  --background-secondary: #21222c;
  --background-secondary-alt: #1e1f29;
  --background-tertiary: #191a21;
  --background-accent: #44475a;
  --background-floating: #21222c;
  --channeltextarea-background: #44475a;
  --text-normal: #f8f8f2;
  --text-muted: #6272a4;
  --text-link: #8be9fd;
  --header-primary: #f8f8f2;
  --header-secondary: #bd93f9;
  --interactive-normal: #f8f8f2;
  --interactive-hover: #bd93f9;
  --interactive-active: #ff79c6;
  --interactive-muted: #6272a4;
}
""",
    },
    "catppuccin": {
        "name": "Catppuccin Mocha",
        "description": "Soothing pastel theme (Mocha variant)",
        "author": "Claisum",
        "css": """
/* Catppuccin Mocha Theme by Claisum */
:root {
  --background-primary: #1e1e2e;
  --background-secondary: #181825;
  --background-secondary-alt: #11111b;
  --background-tertiary: #181825;
  --background-accent: #313244;
  --background-floating: #1e1e2e;
  --channeltextarea-background: #313244;
  --text-normal: #cdd6f4;
  --text-muted: #6c7086;
  --text-link: #89b4fa;
  --header-primary: #cdd6f4;
  --header-secondary: #bac2de;
  --interactive-normal: #cdd6f4;
  --interactive-hover: #b4befe;
  --interactive-active: #cba6f7;
  --interactive-muted: #45475a;
}
""",
    },
}


def list_themes() -> None:
    """List all available themes."""
    table = Table(title="Available Themes", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Source", style="dim")

    for key, theme in BUILTIN_THEMES.items():
        table.add_row(key, theme["name"], theme["description"], "built-in")

    themes_dir = manager.get_themes_dir()
    for theme_file in themes_dir.glob("*.json"):
        try:
            with open(theme_file) as f:
                theme = json.load(f)
            table.add_row(
                theme_file.stem,
                theme.get("name", theme_file.stem),
                theme.get("description", "No description"),
                "installed",
            )
        except Exception:
            pass

    console.print(table)


def apply_theme(theme_name: str) -> bool:
    """Apply a theme to Discord (write to BetterDiscord)."""
    css = _get_theme_css(theme_name)
    if css is None:
        console.print(f"[red]Theme '{theme_name}' not found.[/red]")
        console.print("[dim]Run 'claisum discord themes list' to see available themes.[/dim]")
        return False

    # Write theme to BetterDiscord
    if not manager.write_theme_to_discord(css, theme_name):
        return False

    # Enable the theme
    if not manager.enable_theme(theme_name):
        return False

    # Save to config
    config = load_config()
    config.setdefault("discord", {})["active_theme"] = theme_name
    save_config(config)

    console.print(f"[green]Theme '{theme_name}' applied![/green]")
    console.print("[dim]Restart Discord to see the changes.[/dim]")
    return True


def remove_theme() -> bool:
    """Remove the currently active theme."""
    config = load_config()
    active = config.get("discord", {}).get("active_theme")

    if not active:
        console.print("[dim]No theme is currently active.[/dim]")
        return True

    if not manager.disable_theme(active):
        return False

    config.setdefault("discord", {}).pop("active_theme", None)
    save_config(config)

    console.print("[green]Theme removed![/green]")
    console.print("[dim]Restart Discord to see the changes.[/dim]")
    return True


def _get_theme_css(theme_name: str) -> Optional[str]:
    """Get theme CSS from builtin, JSON, or CSS file."""
    if theme_name in BUILTIN_THEMES:
        return BUILTIN_THEMES[theme_name]["css"]

    themes_dir = manager.get_themes_dir()
    
    # Try JSON format
    theme_file = themes_dir / f"{theme_name}.json"
    if theme_file.exists():
        try:
            with open(theme_file) as f:
                theme = json.load(f)
            return theme.get("css")
        except Exception:
            pass

    # Try CSS format
    css_file = themes_dir / f"{theme_name}.css"
    if css_file.exists():
        try:
            return css_file.read_text(encoding="utf-8")
        except Exception:
            pass

    return None
