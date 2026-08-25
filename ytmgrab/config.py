"""Configuration handling for ytmgrab."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "ytmgrab"
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
    """Create a default config file in the config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    print(f"Created config: {CONFIG_FILE}")

def load_config():
    """Load the config file, creating default if missing."""
    if not CONFIG_FILE.exists():
        create_default_config()
    with CONFIG_FILE.open() as f:
        return json.load(f)

def show_config():
    """Print the current config file content."""
    if CONFIG_FILE.exists():
        print(CONFIG_FILE.read_text())
    else:
        print("No config found.")
