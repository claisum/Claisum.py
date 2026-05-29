"""Claisum configuration — persistent JSON store and path helpers."""
import json
import os
from pathlib import Path

# ── Directories ────────────────────────────────────────────────────────────
def _data_home() -> Path:
    """Return platform-appropriate user data directory."""
    if os.name == "nt":
        base = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
    elif os.environ.get("XDG_DATA_HOME"):
        base = os.environ["XDG_DATA_HOME"]
    else:
        base = Path.home() / ".local" / "share"
    return Path(base) / "Claisum"

CLAISUM_DIR   = _data_home()
THEMES_DIR    = CLAISUM_DIR / "themes"
PLUGINS_DIR   = CLAISUM_DIR / "plugins"
CONFIG_FILE   = CLAISUM_DIR / "config.json"

for _d in (CLAISUM_DIR, THEMES_DIR, PLUGINS_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def get_themes_dir() -> Path:
    return THEMES_DIR

def get_plugins_dir() -> Path:
    return PLUGINS_DIR

def get_claisum_dir() -> Path:
    return CLAISUM_DIR


# ── Config I/O ─────────────────────────────────────────────────────────────
def load_config() -> dict:
    """Load config from disk; return {} if missing or corrupt."""
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_config(data: dict) -> None:
    """Persist config to disk atomically."""
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(CONFIG_FILE)


def get_config_value(key: str, default=None):
    return load_config().get(key, default)


def set_config_value(key: str, value) -> None:
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
