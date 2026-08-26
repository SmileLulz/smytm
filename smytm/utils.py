"""Utility functions for smytm."""

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import icons

CACHE_DIR = Path.home() / ".cache" / "smytm"
ALLOWED_AUDIO_FORMATS = {
    "aac",
    "alac",
    "flac",
    "m4a",
    "mp3",
    "opus",
    "vorbis",
    "wav",
}


def check_dependencies():
    """Check required tools and warn about optional/helper dependencies."""
    missing = []

    for tool in ("yt-dlp", "ffmpeg"):
        if shutil.which(tool) is None:
            missing.append(tool)
    
    for package in ["mutagen"]:
        if importlib.util.find_spec(package) is None:
            missing.append(f"python-{package}")

    warnings = []

    # if importlib.util.find_spec("mutagen") is None:
    #     warnings.append(
    #         "'python-mutagen' not found. Some yt-dlp metadata/thumbnail features may be unavailable."
    #     )

    if (
        shutil.which("AtomicParsley") is None
        and shutil.which("atomicparsley") is None
    ):
        warnings.append("'atomicparsley' not found. M4A thumbnail embedding may fail.")

    if shutil.which("rsgain") is None:
        warnings.append("'rsgain' not found. ReplayGain tagging will be skipped.")

    if warnings:
        print(f"{icons.icon('warning')}Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
        print()

    if missing:
        print(f"{icons.icon('error')}Missing required dependencies:")
        for dependency in missing:
            print(f"   - {dependency}")
        print()
        sys.exit(1)


def validate_video_id(video_id):
    """Check if a string is a valid YouTube video ID."""
    return re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id) is not None


def ensure_cache_dir():
    """Create the application cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name):
    """Sanitize a YouTube-derived filename for safe filesystem use."""
    sanitized = re.sub(r'[\\/*?:"<>|\x00-\x1f\x7f]', "_", name)
    sanitized = sanitized.strip(" .")
    return sanitized or "Unknown"


def validate_audio_format(audio_format):
    """Validate an audio format used both by yt-dlp and as a filename suffix."""
    normalized = str(audio_format).strip().lower()
    if normalized not in ALLOWED_AUDIO_FORMATS:
        supported = ", ".join(sorted(ALLOWED_AUDIO_FORMATS))
        raise ValueError(f"unsupported audio format '{audio_format}'; use one of: {supported}")
    return normalized


def get_incremented_filename(output_dir, title, ext):
    """Return a path that does not exist, appending (n) if needed."""
    output_dir = Path(output_dir)
    ext = validate_audio_format(ext)
    title = sanitize_filename(title)

    base_path = output_dir / f"{title}.{ext}"
    if not base_path.exists():
        return base_path

    counter = 1
    while True:
        new_path = output_dir / f"{title} ({counter}).{ext}"
        if not new_path.exists():
            return new_path
        counter += 1


def apply_replaygain(file_path, audio_format):
    """Apply ReplayGain tags using the external rsgain tool."""
    if shutil.which("rsgain") is None:
        return False

    cmd = ["rsgain", "custom", "-s", "i"]
    if audio_format == "opus":
        cmd.extend(["-o", "r"])
    cmd.append(str(file_path))

    print(f"{icons.icon('replaygain')}Applying ReplayGain tags...\n")
    try:
        result = subprocess.run(cmd, check=False)
    except OSError as exc:
        print(f"{icons.icon('error')}Unable to run rsgain: {exc}")
        return False

    if result.returncode == 0:
        print(f"{icons.icon('success')}ReplayGain tags applied successfully!")
        return True

    print(f"{icons.icon('error')}ReplayGain tagging failed!")
    return False
