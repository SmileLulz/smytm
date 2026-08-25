"""Search for songs on YouTube Music."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
from . import config
from . import icons

def check_search_dependencies():
    """Check if external tools and packages for search are available."""
    missing = []
    for cmd in ("curl", "chafa"):
        if shutil.which(cmd) is None:
            missing.append(cmd)
    if importlib.util.find_spec("ytmusicapi") is None:
        missing.append("python-ytmusicapi")
    if missing:
        print(f"Missing dependencies for search: {', '.join(missing)}", file=sys.stderr)
        return False
    return True

def run(args):
    """Execute the search subcommand."""
    if not check_search_dependencies():
        sys.exit(1)

    from ytmusicapi import YTMusic

    query = " ".join(args.query)
    count = args.count

    yt = YTMusic()
    try:
        songs = yt.search(query, filter="songs")[:count]
    except Exception as e:
        print(f"Search failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not songs:
        print("No songs found.")
        sys.exit(1)

    cfg = config.load_config()
    thumbnail_size = cfg.get("thumbnail_size", "16")
    if args.tsize:
        thumbnail_size = args.tsize

    for i, song in enumerate(songs):
        title = song.get("title", "Unknown")
        artists = ", ".join(a["name"] for a in song.get("artists", []))
        video_id = song.get("videoId", "")
        thumb = song.get("thumbnails", [{}])[-1].get("url", "")

        print()

        if thumb:
            with tempfile.NamedTemporaryFile() as tmp:
                if subprocess.run(
                    ["curl", "-Ls", thumb, "-o", tmp.name],
                    capture_output=True
                ).returncode == 0:
                    subprocess.run(
                        ["chafa", f"--size={thumbnail_size}x{thumbnail_size}", tmp.name]
                    )
                else:
                    print("[Thumbnail unavailable]")
        else:
            print("[Thumbnail unavailable]")

        print(f"{icons.icon('title')}Title  : {title}")
        print(f"{icons.icon('artist')}Artist : {artists}")
        print(f"{icons.icon('music')}ID     : {video_id}")
        print(f"{icons.icon('music')}Link   : https://music.youtube.com/watch?v={video_id}")

        if i != len(songs) - 1:
            print()
