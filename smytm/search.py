"""Search for songs on YouTube Music."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile

from . import config
from . import icons

SUBPROCESS_TIMEOUT = 30


def check_search_dependencies():
    """Check if external tools and packages for search are available."""
    missing = []

    for command in ("curl", "chafa"):
        if shutil.which(command) is None:
            missing.append(command)
    if importlib.util.find_spec("ytmusicapi") is None:
        missing.append("python-ytmusicapi")

    if missing:
        print(
            f"Missing dependencies for search: {', '.join(missing)}",
            file=sys.stderr,
        )
        return False
    return True


def _download_thumbnail(url, path):
    """Download one HTTPS thumbnail with a bounded network operation."""
    if not isinstance(url, str) or not url.lower().startswith("https://"):
        return False

    try:
        result = subprocess.run(
            [
                "curl",
                "--fail",
                "--silent",
                "--show-error",
                "--location",
                "--connect-timeout", "5",
                "--max-time", "20",
                "--output", str(path),
                url,
            ],
            check=False,
            capture_output=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def run(args):
    """Execute the search subcommand."""
    if not check_search_dependencies():
        sys.exit(1)

    from ytmusicapi import YTMusic

    query = " ".join(args.query)
    count = args.count

    try:
        yt = YTMusic()
        songs = yt.search(query, filter="songs")[:count]
    except Exception as exc:
        print(f"Search failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not songs:
        print("No songs found.")
        sys.exit(1)

    cfg = config.load_config()
    thumbnail_size = args.tsize or cfg.get("thumbnail_size", "16")

    try:
        thumbnail_size = int(thumbnail_size)
        if thumbnail_size < 1:
            raise ValueError
    except (TypeError, ValueError):
        print(
            f"Invalid thumbnail size '{thumbnail_size}'. Use a positive integer.",
            file=sys.stderr,
        )
        sys.exit(2)

    for index, song in enumerate(songs):
        title = song.get("title") or "Unknown"
        artists = ", ".join(
            artist.get("name", "Unknown")
            for artist in song.get("artists", [])
            if isinstance(artist, dict)
        ) or "Unknown"
        video_id = song.get("videoId") or ""
        thumbnails = song.get("thumbnails") or []
        thumb = thumbnails[-1].get("url", "") if thumbnails else ""

        print()

        if thumb:
            with tempfile.NamedTemporaryFile() as tmp:
                if _download_thumbnail(thumb, tmp.name):
                    try:
                        preview = subprocess.run(
                            [
                                "chafa",
                                f"--size={thumbnail_size}x{thumbnail_size}",
                                tmp.name,
                            ],
                            check=False,
                            timeout=SUBPROCESS_TIMEOUT,
                        )
                        if preview.returncode != 0:
                            print("[Thumbnail preview unavailable]")
                    except (OSError, subprocess.TimeoutExpired):
                        print("[Thumbnail preview unavailable]")
                else:
                    print("[Thumbnail unavailable]")
        else:
            print("[Thumbnail unavailable]")

        print(f"{icons.icon('title')}Title  : {title}")
        print(f"{icons.icon('artist')}Artist : {artists}")
        print(f"{icons.icon('music')}ID     : {video_id}")
        if video_id:
            print(
                f"{icons.icon('music')}Link   : "
                f"https://music.youtube.com/watch?v={video_id}"
            )

        if index != len(songs) - 1:
            print()
