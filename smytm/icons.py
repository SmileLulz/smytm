"""Optional Nerd Font icon handling for smytm.

Icons are referenced throughout the codebase by short, semantic string
keys (e.g. "warning", "error", "success") instead of raw glyphs. Whether
a glyph is actually printed is controlled by the "nerd_font_icons" config
toggle, so the tool looks clean on terminals without a Nerd Font too.
"""

ICONS = {
    "download":   "  ",
    "video":      "  ",
    "format":     "  ",
    "output":     "󰉍  ",
    "music":      "󰝚  ",
    "fallback":   "  ",
    "success":    "  ",
    "error":      "  ",
    "title":      "󰝚  ",
    "artist":     "󰀄  ",
    "warning":    "  ",
    "replaygain": "󰕾  ",
}

_enabled = None
_icon_map = None


def _nerd_fonts_enabled():
    """Load and cache the "nerd_font_icons" config toggle for this run."""
    global _enabled
    if _enabled is None:
        from . import config
        _enabled = bool(config.load_config().get("nerd_font_icons", True))
    return _enabled


def _load_icon_map():
    """Load the user-defined icon overrides from config and merge with defaults."""
    global _icon_map
    if _icon_map is not None:
        return

    from . import config
    cfg = config.load_config()
    user_icons = cfg.get("icons")

    if isinstance(user_icons, dict):
        merged = ICONS.copy()
        merged.update(user_icons)
        _icon_map = merged
    else:
        _icon_map = ICONS.copy()


def icon(key):
    """Return "GLYPH  " for a known key if Nerd Fonts are enabled, else ''."""
    if not _nerd_fonts_enabled():
        return ""
    _load_icon_map()
    glyph = _icon_map.get(key)
    return f"{glyph}" if glyph else ""
