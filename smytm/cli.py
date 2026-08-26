"""Command-line interface for smytm."""

import argparse

from . import config


def positive_int(value):
    """Parse a strictly positive integer for argparse."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def thumbnail_size(value):
    """Parse a positive thumbnail size in pixels."""
    return positive_int(value)


def main():
    parser = argparse.ArgumentParser(
        prog="smytm",
        description="Search or download audio from YouTube / YouTube Music.",
    )
    subparsers = parser.add_subparsers(
        dest="command", required=False, help="Subcommand"
    )

    download_parser = subparsers.add_parser(
        "download",
        aliases=["d"],
        help="Download an audio by YouTube video ID",
    )
    download_parser.add_argument("video_id", help="11-character YouTube video ID")
    download_parser.add_argument(
        "-f", "--format", help="Override audio format (opus, flac, ...)"
    )
    download_parser.add_argument(
        "-rg", "--replaygain", action="store_true", help="Apply ReplayGain 2.0 tags"
    )
    download_parser.add_argument(
        "-p", "--path", type=str, help="Output directory (overrides config/default)"
    )

    playlist_parser = subparsers.add_parser(
        "playlist",
        aliases=["p"],
        help="Download an entire playlist",
    )
    playlist_parser.add_argument("playlist_id", help="Playlist ID or URL")
    playlist_parser.add_argument(
        "-f", "--format", help="Override audio format (opus, flac, ...)"
    )
    playlist_parser.add_argument(
        "-rg", "--replaygain", action="store_true", help="Apply ReplayGain 2.0 tags"
    )
    playlist_parser.add_argument(
        "-p", "--path", type=str, help="Output directory (overrides config/default)"
    )
    playlist_parser.add_argument(
        "-inv", "--inverse", action="store_true",
        help="Download videos in reverse order",
    )

    search_parser = subparsers.add_parser(
        "search",
        aliases=["s"],
        help="Search for songs on YouTube Music",
    )
    search_parser.add_argument("query", nargs="+", help="Search query")
    search_parser.add_argument(
        "-c", "--count", type=positive_int, default=3,
        help="Number of search results",
    )
    search_parser.add_argument(
        "-ts", "--tsize", type=thumbnail_size,
        help="Thumbnail size for chafa (e.g., 16, 24, 40)",
    )

    parser.add_argument(
        "-gc", "--gen-config", action="store_true", help="Generate default config"
    )
    parser.add_argument(
        "-sc", "--show-config", action="store_true", help="Show current config"
    )

    args = parser.parse_args()

    if args.gen_config:
        config.create_default_config()
        return
    if args.show_config:
        config.show_config()
        return

    if args.command is None:
        parser.error("the following arguments are required: command")

    if args.command in ("download", "d"):
        from . import download
        download.run(args)
    elif args.command in ("search", "s"):
        from . import search
        search.run(args)
    elif args.command in ("playlist", "p"):
        from . import playlist
        playlist.run(args)


if __name__ == "__main__":
    main()
