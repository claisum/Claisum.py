"""Discord installation path detection for all platforms."""

import os
import platform
from pathlib import Path
from typing import Optional


def find_discord_path() -> Optional[Path]:
    """Find the Discord installation directory."""
    system = platform.system()

    if system == "Windows":
        return _find_discord_windows()
    elif system == "Linux":
        return _find_discord_linux()
    elif system == "Darwin":
        return _find_discord_macos()
    return None


def _find_discord_windows() -> Optional[Path]:
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        Path(local_app_data) / "Discord",
        Path(local_app_data) / "DiscordCanary",
        Path(local_app_data) / "DiscordPTB",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _find_discord_linux() -> Optional[Path]:
    home = Path.home()
    candidates = [
        home / ".config" / "discord",
        home / ".config" / "discordcanary",
        home / ".config" / "discordptb",
        Path("/usr/share/discord"),
        Path("/opt/discord"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _find_discord_macos() -> Optional[Path]:
    home = Path.home()
    candidates = [
        home / "Library" / "Application Support" / "discord",
        home / "Library" / "Application Support" / "discordcanary",
        Path("/Applications/Discord.app"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def get_discord_css_path() -> Optional[Path]:
    """Return the path where Discord loads custom CSS."""
    discord_path = find_discord_path()
    if not discord_path:
        return None

    system = platform.system()
    if system == "Windows":
        settings_dir = discord_path / "settings"
        return settings_dir / "custom.css"
    elif system == "Linux":
        return discord_path / "settings" / "custom.css"
    return None


def get_discord_user_data_path() -> Optional[Path]:
    """Return Discord's user data directory for plugin injection."""
    discord_path = find_discord_path()
    if not discord_path:
        return None
    system = platform.system()
    if system == "Windows":
        import glob
        matches = list(discord_path.glob("app-*/modules/discord_desktop_core-*/discord_desktop_core"))
        if matches:
            return matches[0]
    elif system == "Linux":
        matches = list(discord_path.glob("*/modules/discord_desktop_core-*/discord_desktop_core"))
        if matches:
            return matches[0]
    return None
