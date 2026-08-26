"""Configuration handling for smytm."""

import json
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "smytm"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "output_dir": str(Path.home() / "Music"),
    "format": "opus",
    "audio_quality": "0",
    "artist_in_filename": True,
    "replaygain_always": False,
    "thumbnail_size": "16",
    "nerd_font_icons": True,
}


def create_default_config():
    """Create the default config without overwriting an existing one."""
    if CONFIG_FILE.exists():
        print(f"Config already exists: {CONFIG_FILE}")
        return False

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as config_file:
        json.dump(DEFAULT_CONFIG, config_file, indent=4)
        config_file.write("\n")
    print(f"Created config: {CONFIG_FILE}")
    return True


def load_config():
    """Load the config file, creating defaults if missing or malformed."""
    if not CONFIG_FILE.exists():
        create_default_config()
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_FILE.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"Warning: could not read {CONFIG_FILE}: {exc}. "
            "Using default configuration.",
            file=sys.stderr,
        )
        return DEFAULT_CONFIG.copy()

    if not isinstance(config, dict):
        print(
            f"Warning: {CONFIG_FILE} must contain a JSON object. "
            "Using default configuration.",
            file=sys.stderr,
        )
        return DEFAULT_CONFIG.copy()

    merged = DEFAULT_CONFIG.copy()
    merged.update(config)
    return merged


def show_config():
    """Print the current config file content."""
    if CONFIG_FILE.exists():
        try:
            print(CONFIG_FILE.read_text(encoding="utf-8"))
        except OSError as exc:
            print(f"Could not read config: {exc}", file=sys.stderr)
    else:
        print("No config found.")
