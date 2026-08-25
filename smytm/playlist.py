"""Download entire playlists from YouTube."""

import subprocess
import sys
from pathlib import Path
from . import config
from . import download
from . import icons
from . import utils


def get_playlist_entries(playlist_id):
    """Fetch all video IDs and titles from a playlist.

    Returns:
        List of dicts: [{"id": "abc123", "title": "Song Name"}, ...]
    """
    if playlist_id.startswith("http"):
        url = playlist_id
    else:
        url = f"https://www.youtube.com/playlist?list={playlist_id}"

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s",
        "--no-warnings",
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to fetch playlist: {result.stderr}", file=sys.stderr)
        return []

    entries = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            video_id, title = parts
            entries.append({"id": video_id, "title": title})
        else:
            entries.append({"id": parts[0], "title": "Unknown"})

    return entries


def run(args):
    """Execute the playlist subcommand."""
    utils.check_dependencies()
    cfg = config.load_config()

    audio_format = args.format or cfg.get("format", "opus")
    audio_quality = cfg.get("audio_quality", "0")

    if args.path:
        output_dir = Path(args.path).expanduser()
    else:
        output_dir = Path(cfg.get("output_dir", str(Path.home() / "Music")))

    apply_replaygain = args.replaygain or cfg.get("replaygain_always", False)
    include_artist = cfg.get("artist_in_filename", True)

    output_dir.mkdir(parents=True, exist_ok=True)

    utils.ensure_cache_dir()
    log_path = utils.CACHE_DIR / "playlist-logs.log"

    with open(log_path, 'w') as log_file:
        log_file.write("# Failed downloads (ID\\tTitle):\n")

        print(f"{icons.icon('download')} Fetching playlist...")
        entries = get_playlist_entries(args.playlist_id)

        if not entries:
            print("No videos found in playlist or failed to fetch.", file=sys.stderr)
            return

        if args.inverse:
            entries.reverse()
            print(f"{icons.icon('fallback')} Download order: Reversed (last → first)")
        else:
            print(f"{icons.icon('download')} Download order: Normal (first → last)")

        print(f"Found {len(entries)} videos in playlist.")
        print(f"{icons.icon('format')} Format: {audio_format}")
        print(f"{icons.icon('output')} Output: {output_dir}")
        print()

        success_count = 0
        fail_count = 0

        for idx, entry in enumerate(entries, 1):
            video_id = entry["id"]
            title = entry["title"]

            print(f"\n[{idx}/{len(entries)}] {icons.icon('download')} Downloading: {title}")
            print(f"   ID: {video_id}")

            success, output_path = download.download_by_id(
                video_id,
                output_dir,
                audio_format,
                audio_quality,
                include_artist
            )

            if success:
                success_count += 1
                if apply_replaygain and output_path:
                    print()
                    utils.apply_replaygain(output_path, audio_format)
            else:
                fail_count += 1
                log_file.write(f"{video_id}\t{title}\n")

    print()
    if fail_count > 0:
        print(f"{icons.icon('error')} Failed: {fail_count}")
        print(f"   Failed entries logged to: {log_path}")
    print()
    print(f"{icons.icon('success')} Playlist download complete!")
    print(f"   Success: {success_count}")
