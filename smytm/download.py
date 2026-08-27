"""Download audio from YouTube."""

import subprocess
import sys
from pathlib import Path

from . import config
from . import icons
from . import utils

SUBPROCESS_TIMEOUT = 300


def _run(command, **kwargs):
    """Run an external command and convert launch errors into a clean failure."""
    try:
        return subprocess.run(
            command,
            check=False,
            timeout=SUBPROCESS_TIMEOUT,
            **kwargs,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"{icons.icon('error')}External command failed: {exc}", file=sys.stderr)
        return None


def download_single(
    url, output_dir, audio_format, audio_quality, video_id, include_artist=True
):
    """Download audio from a given URL, return (success, output_path)."""
    try:
        audio_format = utils.validate_audio_format(audio_format)
    except ValueError as exc:
        print(f"{icons.icon('error')}{exc}", file=sys.stderr)
        return False, None

    info_cmd = [
        "yt-dlp",
        "--print", "%(title)s\t%(artist)s\t%(uploader)s",
        "--no-playlist",
        "--",
        url,
    ]
    result = _run(info_cmd, capture_output=True, text=True)
    if result is None or result.returncode != 0:
        return False, None

    parts = result.stdout.strip().split("\t")
    title = parts[0] if parts and parts[0] else "Unknown"
    artist = parts[1] if len(parts) > 1 else ""
    uploader = parts[2] if len(parts) > 2 else ""

    if include_artist and (artist or uploader):
        artist_name = artist or uploader
        base_name = (
            f"{utils.sanitize_filename(title)} - "
            f"{utils.sanitize_filename(artist_name)}"
        )
    else:
        base_name = utils.sanitize_filename(title)

    output_path = utils.get_incremented_filename(
        output_dir, base_name, audio_format
    )

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--extract-audio",
        "--audio-format", audio_format,
        "--audio-quality", str(audio_quality),
        "--embed-metadata",
        "--embed-thumbnail",
        "--convert-thumbnails", "jpg",
        "--postprocessor-args",
        r"ThumbnailsConvertor+ffmpeg_o:-vf crop='min(iw\,ih)':'min(iw\,ih)'",
        "--output", str(output_path),
        "--rm-cache-dir",
        "--no-keep-video",
        "--",
        url,
    ]

    result = _run(cmd)
    success = result is not None and result.returncode == 0
    return success, output_path if success else None


def download_by_id(video_id, output_dir, audio_format, audio_quality, include_artist=True):
    """Download a single video ID, preferring music.youtube.com."""
    if not utils.validate_video_id(video_id):
        print(f"Invalid video ID: {video_id}")
        return False, None

    music_url = f"https://music.youtube.com/watch?v={video_id}"
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"{icons.icon('music')} Trying music.youtube.com...")
    success, output_path = download_single(
        music_url, output_dir, audio_format, audio_quality, video_id, include_artist
    )

    if not success:
        print(
            f"\n{icons.icon('fallback')} Music domain failed, "
            "falling back to youtube.com..."
        )
        success, output_path = download_single(
            youtube_url, output_dir, audio_format, audio_quality, video_id, include_artist
        )

    return success, output_path


def run(args):
    """Execute the download subcommand."""
    utils.check_dependencies()

    cfg = config.load_config()

    audio_format = args.format or cfg.get("format", "opus")
    try:
        audio_format = utils.validate_audio_format(audio_format)
    except ValueError as exc:
        print(f"{icons.icon('error')}{exc}", file=sys.stderr)
        sys.exit(2)

    audio_quality = cfg.get("audio_quality", "0")

    if args.path:
        output_dir = Path(args.path).expanduser()
    else:
        output_dir = Path(cfg.get("output_dir", str(Path.home() / "Music")))

    apply_replaygain = args.replaygain or cfg.get("replaygain_always", False)
    download_lyrics = args.lyrics or cfg.get("lyrics_always", False)
    include_artist = bool(cfg.get("artist_in_filename", True))

    output_dir.mkdir(parents=True, exist_ok=True)

    print()
    print(f"{icons.icon('download')} Downloading...")
    print(f"{icons.icon('video')} Video ID : {args.video_id}")
    print(f"{icons.icon('format')} Format   : {audio_format}")
    print(f"{icons.icon('output')} Output   : {output_dir}")
    print()

    success, output_path = download_by_id(
        args.video_id, output_dir, audio_format, audio_quality, include_artist
    )

    if success:
        print(f"\n{icons.icon('success')} Download successful!")
        if download_lyrics and output_path:
            print()
            from . import lyrics
            lyrics.write_lrc(output_path, args.video_id)

        if apply_replaygain and output_path:
            print()
            utils.apply_replaygain(output_path, audio_format)
    else:
        print(f"\n{icons.icon('error')} Download failed!")
        sys.exit(1)
