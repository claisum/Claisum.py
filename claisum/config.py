"""Configuration management for Claisum."""

import json
import os
import platform
from pathlib import Path


def get_config_dir() -> Path:
    """Return the Claisum config directory for the current OS."""
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config_dir = base / "claisum"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    return get_config_dir() / "config.json"


def load_config() -> dict:
    config_file = get_config_file()
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: dict) -> None:
    config_file = get_config_file()
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_themes_dir() -> Path:
    themes_dir = get_config_dir() / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    return themes_dir


def get_plugins_dir() -> Path:
    plugins_dir = get_config_dir() / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    return plugins_dir
