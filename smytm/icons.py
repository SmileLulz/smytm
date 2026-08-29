"""Optional Nerd Font icon handling for smytm.

Icons are referenced throughout the codebase by short, semantic string
keys (e.g. "warning", "error", "success") instead of raw glyphs. Whether
a glyph is actually printed is controlled by the "nerd_font_icons" config
toggle, so the tool looks clean on terminals without a Nerd Font too.
"""

from . import config

ICONS = {
    "download": "\uf019",       # nf-fa-download
    "video": "\uf44c",          # nf-oct-device_camera_video
    "format": "\U000f0f04",     # nf-md-file_music
    "output": "\U000f024d",     # nf-md-folder_outline
    "music": "\U000f0339",      # nf-md-youtube
    "fallback": "\U000f033a",   # nf-md-youtube_studio (fallback attempt)
    "success": "\uf00c",        # nf-fa-check
    "error": "\uf468",          # nf-oct-x_circle
    "title": "\U000f075a",      # nf-md-music_note
    "artist": "\U000f0004",     # nf-md-account_music
    "warning": "\uf071",        # nf-fa-warning
    "replaygain": "\U000f057e", # nf-md-volume_high
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
