"""Shared constants for Claisum installers."""

import os
from pathlib import Path

# Installation paths
APPDATA = Path(os.getenv('APPDATA', ''))
CLAISUM_ROOT = APPDATA / 'Claisum'
CLAISUM_PLUGINS = CLAISUM_ROOT / 'plugins'
CLAISUM_THEMES = CLAISUM_ROOT / 'themes'
CLAISUM_CONFIG = CLAISUM_ROOT / 'config.json'

# Discord paths
DISCORD_APPDATA = APPDATA / 'discord'
DISCORD_RESOURCES = DISCORD_APPDATA / 'resources'

# Web Discord injection path
WEB_DISCORD_INTERCEPTOR = CLAISUM_ROOT / 'web_interceptor'

# URLs
PLUGIN_REGISTRY = 'https://raw.githubusercontent.com/claisum/plugin-registry/main/plugins.json'
THEME_REGISTRY = 'https://raw.githubusercontent.com/claisum/theme-registry/main/themes.json'

# Versions
CLAISUM_VERSION = '2.0.0'
INSTALLER_VERSION = '1.0.0'
