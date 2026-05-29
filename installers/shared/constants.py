"""Shared constants for Claisum installers."""
import os
from pathlib import Path

CLAISUM_VERSION  = "1.0.0.1"
INSTALLER_VERSION= "1.0.0.1"
REPO             = "claisum/Claisum.py"

# Windows paths
LOCALAPPDATA     = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
APPDATA          = Path(os.getenv("APPDATA",      Path.home() / "AppData" / "Roaming"))
CLAISUM_ROOT     = APPDATA / "Claisum"
CLAISUM_PLUGINS  = CLAISUM_ROOT / "plugins"
CLAISUM_THEMES   = CLAISUM_ROOT / "themes"
CLAISUM_CONFIG   = CLAISUM_ROOT / "config.json"

# Remote URLs
RELEASES_URL     = f"https://github.com/{REPO}/releases/latest"
RAW_BASE         = f"https://raw.githubusercontent.com/{REPO}/main"
INJECT_JS_URL    = f"{RAW_BASE}/claisum/discord/claisum_inject.js"
