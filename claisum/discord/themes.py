"""Discord theme management — CLI interface."""
import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from claisum.config import get_themes_dir, load_config, save_config

console = Console()

# ── Built-in themes ────────────────────────────────────────────────────────
BUILTIN_THEMES: dict[str, dict] = {
    "midnight": {
        "name": "Midnight",
        "description": "Deep dark theme with blue accents",
        "author": "Claisum",
        "css": """:root{
  --background-primary:#0d0f12;--background-secondary:#101316;
  --background-secondary-alt:#0d0f12;--background-tertiary:#08090b;
  --channeltextarea-background:#1a1d24;
  --text-normal:#dcddde;--text-muted:#72767d;--text-link:#5865f2;
  --header-primary:#ffffff;--header-secondary:#b9bbbe;
  --interactive-normal:#b9bbbe;--interactive-hover:#dcddde;
  --interactive-active:#ffffff;--interactive-muted:#4f545c;}""",
    },
    "dracula": {
        "name": "Dracula",
        "description": "The classic Dracula color scheme",
        "author": "Claisum",
        "css": """:root{
  --background-primary:#282a36;--background-secondary:#21222c;
  --background-secondary-alt:#1e1f29;--background-tertiary:#191a21;
  --channeltextarea-background:#44475a;
  --text-normal:#f8f8f2;--text-muted:#6272a4;--text-link:#8be9fd;
  --header-primary:#f8f8f2;--header-secondary:#bd93f9;
  --interactive-normal:#f8f8f2;--interactive-hover:#bd93f9;
  --interactive-active:#ff79c6;--interactive-muted:#6272a4;}""",
    },
    "catppuccin": {
        "name": "Catppuccin Mocha",
        "description": "Soothing pastel theme (Mocha variant)",
        "author": "Claisum",
        "css": """:root{
  --background-primary:#1e1e2e;--background-secondary:#181825;
  --background-secondary-alt:#11111b;--background-tertiary:#181825;
  --channeltextarea-background:#313244;
  --text-normal:#cdd6f4;--text-muted:#6c7086;--text-link:#89b4fa;
  --header-primary:#cdd6f4;--header-secondary:#bac2de;
  --interactive-normal:#cdd6f4;--interactive-hover:#b4befe;
  --interactive-active:#cba6f7;--interactive-muted:#45475a;}""",
    },
    "nord": {
        "name": "Nord",
        "description": "Arctic north-bluish color palette",
        "author": "Claisum",
        "css": """:root{
  --background-primary:#2e3440;--background-secondary:#272c36;
  --background-secondary-alt:#21262e;--background-tertiary:#1e2229;
  --channeltextarea-background:#3b4252;
  --text-normal:#d8dee9;--text-muted:#4c566a;--text-link:#88c0d0;
  --header-primary:#eceff4;--header-secondary:#e5e9f0;
  --interactive-normal:#d8dee9;--interactive-hover:#eceff4;
  --interactive-active:#ffffff;--interactive-muted:#4c566a;}""",
    },
    "rose-pine": {
        "name": "Rosé Pine",
        "description": "Natural pine, rose and gold tones",
        "author": "Claisum",
        "css": """:root{
  --background-primary:#191724;--background-secondary:#1f1d2e;
  --background-secondary-alt:#191724;--background-tertiary:#191724;
  --channeltextarea-background:#26233a;
  --text-normal:#e0def4;--text-muted:#6e6a86;--text-link:#9ccfd8;
  --header-primary:#e0def4;--header-secondary:#e0def4;
  --interactive-normal:#e0def4;--interactive-hover:#f0f0ff;
  --interactive-active:#ebbcba;--interactive-muted:#6e6a86;}""",
    },
    "gruvbox": {
        "name": "Gruvbox Dark",
        "description": "Retro groove color scheme",
        "author": "Claisum",
        "css": """:root{
  --background-primary:#282828;--background-secondary:#1d2021;
  --background-secondary-alt:#1a1a1a;--background-tertiary:#141617;
  --channeltextarea-background:#3c3836;
  --text-normal:#ebdbb2;--text-muted:#928374;--text-link:#83a598;
  --header-primary:#fbf1c7;--header-secondary:#ebdbb2;
  --interactive-normal:#ebdbb2;--interactive-hover:#fbf1c7;
  --interactive-active:#ffffff;--interactive-muted:#504945;}""",
    },
    "solarized": {
        "name": "Solarized Dark",
        "description": "Classic Solarized dark palette",
        "author": "Claisum",
        "css": """:root{
  --background-primary:#002b36;--background-secondary:#073642;
  --background-secondary-alt:#001f27;--background-tertiary:#001f27;
  --channeltextarea-background:#073642;
  --text-normal:#839496;--text-muted:#586e75;--text-link:#268bd2;
  --header-primary:#93a1a1;--header-secondary:#839496;
  --interactive-normal:#839496;--interactive-hover:#93a1a1;
  --interactive-active:#fdf6e3;--interactive-muted:#586e75;}""",
    },
}


def list_themes() -> None:
    config = load_config()
    active = config.get("discord", {}).get("active_theme")

    table = Table(title="Available Themes", header_style="bold magenta")
    table.add_column("ID",     style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Source", style="dim")
    table.add_column("Active", style="bold")

    for key, t in BUILTIN_THEMES.items():
        table.add_row(key, t["name"], t["description"], "built-in",
                      "[green]✓[/green]" if key == active else "")

    themes_dir = get_themes_dir()
    for f in themes_dir.glob("*.json"):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
            table.add_row(f.stem, t.get("name", f.stem),
                          t.get("description", ""), "installed",
                          "[green]✓[/green]" if f.stem == active else "")
        except Exception:
            pass
    console.print(table)


def apply_theme(theme_name: str) -> bool:
    css = _get_css(theme_name)
    if css is None:
        console.print(f"[red]Theme '{theme_name}' not found.[/red]")
        console.print("[dim]Run 'claisum discord themes list' to see available themes.[/dim]")
        return False

    themes_dir = get_themes_dir()
    (themes_dir / f"{theme_name}.css").write_text(css, encoding="utf-8")
    (themes_dir / "ENABLED_THEME.txt").write_text(theme_name, encoding="utf-8")

    cfg = load_config()
    cfg.setdefault("discord", {})["active_theme"] = theme_name
    save_config(cfg)

    console.print(f"[green]Theme '{theme_name}' applied.[/green]")
    console.print("[dim]Restart Discord to see the changes.[/dim]")
    return True


def remove_theme() -> bool:
    cfg = load_config()
    active = cfg.get("discord", {}).get("active_theme")
    if not active:
        console.print("[dim]No theme is currently active.[/dim]")
        return True

    marker = get_themes_dir() / "ENABLED_THEME.txt"
    if marker.exists():
        marker.unlink()

    cfg.setdefault("discord", {}).pop("active_theme", None)
    save_config(cfg)
    console.print("[green]Theme removed. Restart Discord to apply.[/green]")
    return True


def _get_css(theme_name: str) -> Optional[str]:
    if theme_name in BUILTIN_THEMES:
        return BUILTIN_THEMES[theme_name]["css"]
    themes_dir = get_themes_dir()
    for ext, key in ((".json", "css"), (".css", None)):
        f = themes_dir / f"{theme_name}{ext}"
        if f.exists():
            try:
                if ext == ".json":
                    return json.loads(f.read_text(encoding="utf-8")).get("css")
                return f.read_text(encoding="utf-8")
            except Exception:
                pass
    return None
