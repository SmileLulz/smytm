"""Stream audio from YouTube without downloading it to disk."""

import subprocess
import sys

from . import icons
from . import utils

SUBPROCESS_TIMEOUT = 300


def _stream_url(url):
    """Stream one URL through yt-dlp into ffplay.

    Returns True when playback completes successfully, otherwise False.
    """
    ytdlp = utils.find_tool("yt-dlp", "yt-dlp.exe")
    ffplay = utils.find_tool("ffplay", "ffplay.exe")

    if ytdlp is None:
        print(f"{icons.icon('error')}yt-dlp is not installed.", file=sys.stderr)
        return False

    if ffplay is None:
        print(f"{icons.icon('error')}ffplay is not installed.", file=sys.stderr)
        print("Install FFmpeg with ffplay included and make it available on PATH.", file=sys.stderr)
        return False

    ytdlp_cmd = [
        ytdlp,
        "--no-playlist",
        "--no-warnings",
        "-f",
        "bestaudio/best",
        "-o",
        "-",
        "--",
        url,
    ]

    ffplay_cmd = [
        ffplay,
        "-hide_banner",
        "-loglevel",
        "warning",
        "-nodisp",
        "-autoexit",
        "-i",
        "-",
    ]

    ytdlp_process = None
    ffplay_process = None

    try:
        ytdlp_process = subprocess.Popen(
            ytdlp_cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )

        ffplay_process = subprocess.Popen(
            ffplay_cmd,
            stdin=ytdlp_process.stdout,
        )

        if ytdlp_process.stdout is not None:
            ytdlp_process.stdout.close()

        ffplay_returncode = ffplay_process.wait(timeout=SUBPROCESS_TIMEOUT)
        ytdlp_process.wait(timeout=SUBPROCESS_TIMEOUT)

        return ffplay_returncode == 0

    except subprocess.TimeoutExpired:
        print(f"{icons.icon('error')}Playback timed out.", file=sys.stderr)
        return False
    except OSError as exc:
        print(f"{icons.icon('error')}Unable to start playback: {exc}", file=sys.stderr)
        return False
    finally:
        for process in (ffplay_process, ytdlp_process):
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


def play_by_id(video_id):
    """Play a video ID, preferring YouTube Music and falling back to YouTube."""
    if not utils.validate_video_id(video_id):
        print(f"{icons.icon('error')}Invalid video ID: {video_id}", file=sys.stderr)
        return False

    music_url = f"https://music.youtube.com/watch?v={video_id}"
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"{icons.icon('music')} Trying YouTube Music...")
    if _stream_url(music_url):
        return True

    print(
        f"\n{icons.icon('fallback')} YouTube Music failed, "
        "falling back to YouTube..."
    )
    return _stream_url(youtube_url)


def run(args):
    """Execute the play subcommand."""
    print()
    print(f"{icons.icon('play')} Playing...")
    print(f"{icons.icon('video')} Video ID : {args.video_id}")
    print()

    if not play_by_id(args.video_id):
        print(f"\n{icons.icon('error')} Playback failed!", file=sys.stderr)
        sys.exit(1)
