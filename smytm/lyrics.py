"""Fetch and write synchronized lyrics as LRC sidecar files."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import icons
from . import utils

LRCLIB_API = "https://lrclib.net/api/get"
LRCLIB_USER_AGENT = (
    "smytm/1.1 "
    "(https://github.com/SmileLulz/smytm)"
)
REQUEST_TIMEOUT = 20
LRCLIB_DELAY = 0.3


def _get_lrclib(
    title: str,
    artist: str,
    album: str,
    duration: int,
) -> dict[str, Any] | None:
    """Fetch the closest LRCLIB record for a track signature."""
    params = {
        "track_name": title,
        "artist_name": artist,
        "duration": str(duration),
    }
    if album:
        params["album_name"] = album
    url = f"{LRCLIB_API}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": LRCLIB_USER_AGENT,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None

    try:
        result = json.loads(payload)
    except json.JSONDecodeError:
        return None

    return result if isinstance(result, dict) else None


def _format_lrc_timestamp(milliseconds: int) -> str:
    """Convert milliseconds to an LRC [MM:SS.xx] timestamp."""
    total_centiseconds = max(0, int(milliseconds)) // 10
    minutes, remainder = divmod(total_centiseconds, 6000)
    seconds, centiseconds = divmod(remainder, 100)
    return f"[{minutes:02d}:{seconds:02d}.{centiseconds:02d}]"


def _ytmusic_to_lrc(lyrics: Any, title: str, artist: str, album: str) -> str | None:
    """Convert ytmusicapi timestamped lyrics to standard LRC."""
    if not isinstance(lyrics, dict) or not lyrics.get("hasTimestamps"):
        return None

    lines = lyrics.get("lyrics")
    if not isinstance(lines, list):
        return None

    output = [
        f"[ti:{title}]",
        f"[ar:{artist}]",
    ]
    if album:
        output.append(f"[al:{album}]")

    lyric_lines = []
    for line in lines:
        if isinstance(line, dict):
            text = str(line.get("text") or "").replace("\r", "").strip()
            start_time = line.get("start_time")
        else:
            text = str(getattr(line, "text", "") or "").replace("\r", "").strip()
            start_time = getattr(line, "start_time", None)

        try:
            timestamp = int(start_time)
        except (TypeError, ValueError):
            continue

        if not text:
            continue

        lyric_lines.append(
            f"{_format_lrc_timestamp(timestamp)}{text}"
        )

    if not lyric_lines:
        return None

    output.extend(lyric_lines)
    return "\n".join(output) + "\n"


def _fetch_from_ytmusic(
    video_id: str,
) -> tuple[str | None, dict[str, Any]]:
    """Fetch timestamped lyrics and metadata from YouTube Music."""
    from ytmusicapi import YTMusic

    yt = YTMusic()
    watch = yt.get_watch_playlist(videoId=video_id)

    if not isinstance(watch, dict):
        return None, {}

    tracks = watch.get("tracks") or []
    track = next(
        (
            item
            for item in tracks
            if isinstance(item, dict) and item.get("videoId") == video_id
        ),
        tracks[0] if tracks and isinstance(tracks[0], dict) else {},
    )

    artists = track.get("artists") or []
    artist = ", ".join(
        str(item.get("name"))
        for item in artists
        if isinstance(item, dict) and item.get("name")
    )
    album_info = track.get("album")
    album = (
        str(album_info.get("name"))
        if isinstance(album_info, dict) and album_info.get("name")
        else ""
    )
    title = str(track.get("title") or "")

    lyrics_browse_id = watch.get("lyrics")
    if not isinstance(lyrics_browse_id, str) or not lyrics_browse_id:
        return None, {
            "title": title,
            "artist": artist,
            "album": album,
            "duration": track.get("duration_seconds"),
        }

    result = yt.get_lyrics(lyrics_browse_id, timestamps=True)
    return _ytmusic_to_lrc(result, title, artist, album), {
        "title": title,
        "artist": artist,
        "album": album,
        "duration": track.get("duration_seconds"),
    }


def _get_ytdlp_metadata(video_id: str) -> dict[str, Any]:
    """Get fallback track metadata from yt-dlp when YouTube Music is unavailable."""
    ytdlp = utils.find_tool("yt-dlp", "yt-dlp.exe")
    if ytdlp is None:
        return {}

    try:
        result = subprocess.run(
            [
                ytdlp,
                "--skip-download",
                "--no-playlist",
                "--print",
                "%(title)s\t%(artist)s\t%(uploader)s\t%(duration)s",
                "--",
                f"https://music.youtube.com/watch?v={video_id}",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}

    if result.returncode != 0:
        return {}

    parts = result.stdout.strip().split("\t")
    title = parts[0] if parts and parts[0] else ""
    artist = parts[1] if len(parts) > 1 and parts[1] else ""
    uploader = parts[2] if len(parts) > 2 and parts[2] else ""
    raw_duration = parts[3] if len(parts) > 3 else ""

    try:
        duration = int(float(raw_duration))
    except (TypeError, ValueError):
        duration = 0

    return {
        "title": title,
        "artist": artist or uploader,
        "album": "",
        "duration": duration,
    }


def fetch_lrc(video_id: str) -> str | None:
    """Fetch synchronized lyrics, preferring YouTube Music then LRCLIB."""
    try:
        lrc, metadata = _fetch_from_ytmusic(video_id)
        if lrc:
            return lrc
    except Exception:
        metadata = _get_ytdlp_metadata(video_id)

    title = str(metadata.get("title") or "")
    artist = str(metadata.get("artist") or "")
    album = str(metadata.get("album") or "")

    try:
        duration = int(metadata.get("duration"))
    except (TypeError, ValueError):
        duration = 0

    if not title or not artist or duration <= 0:
        return None

    time.sleep(LRCLIB_DELAY)
    record = _get_lrclib(title, artist, album, duration)
    if not record:
        return None

    synced = record.get("syncedLyrics")
    if not isinstance(synced, str) or not synced.strip():
        return None

    return synced.rstrip() + "\n"


def write_lrc(audio_path: Path, video_id: str) -> bool:
    """Fetch and atomically write an LRC sidecar next to the downloaded audio."""
    print(f"{icons.icon('music')} Fetching synchronized lyrics...")

    lrc = fetch_lrc(video_id)
    if not lrc:
        print("   No synchronized lyrics found.")
        return False

    lrc_path = audio_path.with_suffix(".lrc")
    temporary_path = lrc_path.with_suffix(".lrc.tmp")

    try:
        temporary_path.write_text(lrc, encoding="utf-8")
        temporary_path.replace(lrc_path)
    except OSError as exc:
        print(f"{icons.icon('error')} Unable to write lyrics: {exc}")
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        return False

    print(f"{icons.icon('success')} Lyrics saved: {lrc_path}")
    return True
