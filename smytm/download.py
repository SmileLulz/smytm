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
    url,
    output_dir,
    audio_format,
    audio_quality,
    include_artist=True,
    skip_existing=False,
):
    """Download audio from a given URL.

    Returns:
        tuple[bool, Path | None, bool]: success, output path, skipped.
    """
    try:
        audio_format = utils.validate_audio_format(audio_format)
    except ValueError as exc:
        print(f"{icons.icon('error')}{exc}", file=sys.stderr)
        return False, None, False

    ytdlp = utils.find_tool("yt-dlp", "yt-dlp.exe")
    if ytdlp is None:
        return False, None, False

    info_cmd = [
        ytdlp,
        "--print", "%(title)s\t%(artist)s\t%(uploader)s",
        "--no-playlist",
        "--",
        url,
    ]
    result = _run(info_cmd, capture_output=True, text=True)
    if result is None or result.returncode != 0:
        return False, None, False

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

    expected_path = Path(output_dir) / f"{base_name}.{audio_format}"

    if skip_existing and expected_path.exists():
        print(f"{icons.icon('fallback')} File already exists, skipping: {expected_path}")
        return True, expected_path, True

    output_path = utils.get_incremented_filename(
        output_dir, base_name, audio_format
    )

    cmd = [
        ytdlp,
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
    return success, output_path if success else None, False


def download_by_id(
    video_id,
    output_dir,
    audio_format,
    audio_quality,
    include_artist=True,
    skip_existing=False,
    force_youtube=False,
):
    """Download a single video ID.

    By default, try YouTube Music first and fall back to YouTube.
    When force_youtube is True, use youtube.com directly with no fallback.
    """
    if not utils.validate_video_id(video_id):
        print(f"Invalid video ID: {video_id}")
        return False, None, False

    music_url = f"https://music.youtube.com/watch?v={video_id}"
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    if force_youtube:
        print(f"{icons.icon('music')} Using YouTube...")
        return download_single(
            youtube_url,
            output_dir,
            audio_format,
            audio_quality,
            video_id,
            include_artist,
            skip_existing,
        )

    print(f"{icons.icon('music')} Trying YouTube Music...")
    success, output_path, skipped = download_single(
        music_url,
        output_dir,
        audio_format,
        audio_quality,
        include_artist,
        skip_existing,
    )

    if success:
        return success, output_path, skipped

    print(
        f"\n{icons.icon('fallback')} Music domain failed, "
        "falling back to youtube.com..."
    )
    return download_single(
        youtube_url,
        output_dir,
        audio_format,
        audio_quality,
        include_artist,
        skip_existing,
    )


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
    skip_existing = args.skip or cfg.get("skip_always", False)
    include_artist = bool(cfg.get("artist_in_filename", True))

    output_dir.mkdir(parents=True, exist_ok=True)

    print()
    print(f"{icons.icon('download')} Downloading...")
    print(f"{icons.icon('video')} Video ID : {args.video_id}")
    print(f"{icons.icon('format')} Format   : {audio_format}")
    print(f"{icons.icon('output')} Output   : {output_dir}")
    print()

    success, output_path, skipped = download_by_id(
        args.video_id,
        output_dir,
        audio_format,
        audio_quality,
        include_artist,
        skip_existing,
        args.youtube,
    )

    if success:
        if skipped:
            print(f"\n{icons.icon('success')} Download skipped!")
        else:
            print(f"\n{icons.icon('success')} Download successful!")

        if not skipped and download_lyrics and output_path:
            print()
            from . import lyrics
            lyrics.write_lrc(output_path, args.video_id)

        if not skipped and apply_replaygain and output_path:
            print()
            utils.apply_replaygain(output_path, audio_format)
    else:
        print(f"\n{icons.icon('error')} Download failed!")
        sys.exit(1)
