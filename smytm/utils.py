"""Utility functions for ytmgrab."""

import re
import shutil
import importlib.util
import subprocess
import sys
from pathlib import Path
from . import icons

CACHE_DIR = Path.home() / ".cache" / "ytmgrab"

def check_dependencies():
    """Check required Python packages and external tools."""
    missing = []

    for tool in ["yt-dlp", "ffmpeg"]:
        if shutil.which(tool) is None:
            missing.append(tool)

    for package in ["mutagen"]:
        if importlib.util.find_spec(package) is None:
            missing.append(f"python-{package}")

    warnings = []
    if shutil.which("AtomicParsley") is None and shutil.which("atomicparsley") is None:
        warnings.append("'atomicparsley' not found. M4A thumbnail embedding may fail.")
    if shutil.which("rsgain") is None:
        warnings.append("'rsgain' not found. ReplayGain tagging will be skipped.")

    if warnings:
        print(f"{icons.icon('warning')}Warnings:")
        for w in warnings:
            print(f"   - {w}")
        print()

    if missing:
        print(f"{icons.icon('error')}Missing required dependencies:")
        for d in missing:
            print(f"   - {d}")
        print()
        sys.exit(1)

def validate_video_id(video_id):
    """Check if a string is a valid YouTube video ID (11 chars)."""
    return re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id) is not None

def ensure_cache_dir():
    """Create the cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name):
    """Remove characters that are invalid in filenames."""
    return re.sub(r'[\\/*?:"<>|]', '_', name)

def get_incremented_filename(output_dir, title, ext):
    """Return a path that does not exist, appending (n) if needed."""
    base_path = Path(output_dir) / f"{title}.{ext}"
    if not base_path.exists():
        return base_path
    counter = 1
    while True:
        new_path = Path(output_dir) / f"{title} ({counter}).{ext}"
        if not new_path.exists():
            return new_path
        counter += 1

def apply_replaygain(file_path, audio_format):
    """Apply ReplayGain tags using the external 'rsgain' tool (if available)."""
    if shutil.which("rsgain") is None:
        return False
    cmd = ["rsgain", "custom", "-s", "i"]
    if audio_format == "opus":
        cmd.extend(["-o", "r"])
    cmd.append(str(file_path))
    print(f"{icons.icon('replaygain')}Applying ReplayGain tags...\n")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"{icons.icon('success')}ReplayGain tags applied successfully!")
        return True
    else:
        print(f"{icons.icon('error')}ReplayGain tagging failed!")
        return False
