"""Built-in plugin CSS/JS implementations for claisum_inject.js and CLI."""

# CSS keyed by the same IDs used in plugins.py BUILTIN_PLUGINS and inject.js
PLUGIN_CSS: dict[str, str] = {
    "compact-mode": (
        "[class*='message-']{padding:2px 16px !important;}"
        "[class*='contents-']{padding-top:0 !important;}"
        "[class*='cozyMessage']{min-height:0 !important;}"
    ),
    "square-corners": "*{border-radius:0 !important;}",
    "big-emoji": (
        "[class*='emoji'][class*='jumboable'],"
        "[class*='emojiContainer']{width:48px !important;height:48px !important;}"
    ),
    "hide-game-activity": (
        "[class*='activityStatus'],[class*='gameInfo'],"
        "[class*='nowPlayingColumn']{display:none !important;}"
    ),
    "hide-avatars": (
        "[class*='avatar-'],[class*='avatarWrapper']"
        "{display:none !important;}"
    ),
}


def get_plugin_css(plugin_id: str) -> str | None:
    """Return the CSS string for a built-in plugin, or None if not found."""
    return PLUGIN_CSS.get(plugin_id)
