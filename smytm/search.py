"""Search for songs on YouTube Music."""

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
import urllib.error
import urllib.request

from . import config
from . import icons
from . import utils

SUBPROCESS_TIMEOUT = 30
NETWORK_TIMEOUT = 20


def check_search_dependencies():
    """Check packages and external tools required for search."""
    missing = []

    if utils.find_tool("chafa", "chafa.exe") is None:
        missing.append("chafa")

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
    """Download one HTTPS thumbnail using Python's standard HTTPS stack."""
    if not isinstance(url, str) or not url.lower().startswith("https://"):
        return False

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "smytm/1.2"},
    )

    try:
        with urllib.request.urlopen(request, timeout=NETWORK_TIMEOUT) as response:
            with open(path, "wb") as output:
                output.write(response.read())
    except (urllib.error.URLError, TimeoutError, OSError):
        return False

    return True


def run(args):
    """Execute the search subcommand."""
    if not check_search_dependencies():
        sys.exit(1)

    chafa = utils.find_tool("chafa", "chafa.exe")

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
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".img",
                    delete=False,
                ) as tmp:
                    tmp_path = tmp.name

                if _download_thumbnail(thumb, tmp_path):
                    try:
                        preview = subprocess.run(
                            [
                                chafa,
                                f"--size={thumbnail_size}x{thumbnail_size}",
                                tmp_path,
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
            finally:
                if tmp_path:
                    try:
                        Path(tmp_path).unlink(missing_ok=True)
                    except OSError:
                        pass
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
