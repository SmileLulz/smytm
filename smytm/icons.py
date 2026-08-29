"""Optional Nerd Font icon handling for smytm.

Icons are referenced throughout the codebase by short, semantic string
keys (e.g. "warning", "error", "success") instead of raw glyphs. Whether
a glyph is actually printed is controlled by the "nerd_font_icons" config
toggle, so the tool looks clean on terminals without a Nerd Font too.
"""

from . import config

ICONS = {
    "download": "",
    "video": "",
    "format": "",
    "output": "󰉍",
    "music": "󰝚",
    "fallback": "",
    "success": "",
    "error": "",
    "title": "󰝚",
    "artist": "󰀄",
    "warning": "",
    "replaygain": "󰕾",
}

_enabled = None


def _nerd_fonts_enabled():
    """Load and cache the "nerd_font_icons" config toggle for this run."""
    global _enabled
    if _enabled is None:
        _enabled = bool(config.load_config().get("nerd_font_icons", True))
    return _enabled


def icon(key):
    """Return "GLYPH  " for a known key if Nerd Fonts are enabled, else ''."""
    if not _nerd_fonts_enabled():
        return ""
    glyph = ICONS.get(key)
    return f"{glyph}  " if glyph else ""
