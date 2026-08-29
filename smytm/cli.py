"""Command-line interface for smytm."""

import argparse
import sys

from importlib.metadata import version

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


def _normalize_leading_hyphen_id(argv):
    """Insert '--' before a leading-hyphen video/playlist ID.

    The CLI should not require users to know argparse's '--' convention.
    Only the first positional argument of download/playlist is normalized;
    legitimate options and option values remain untouched.
    """
    if not argv:
        return argv

    try:
        command_index = next(
            i
            for i, token in enumerate(argv)
            if token in {"download", "d", "playlist", "p"}
        )
    except StopIteration:
        return argv

    value_options = {
        "-f",
        "--format",
        "-p",
        "--path",
    }

    flag_options = {
        "-rg",
        "--replaygain",
        "-ly",
        "--lyrics",
        "-inv",
        "--inverse",
        "-h",
        "--help",
    }

    i = command_index + 1

    while i < len(argv):
        token = argv[i]

        if token == "--":
            return argv

        if token.startswith("-"):
            if token in value_options:
                i += 2
                continue

            if any(
                token.startswith(option + "=")
                for option in ("--format", "--path")
            ):
                i += 1
                continue

            if token in flag_options:
                i += 1
                continue

            return argv[:i] + ["--"] + argv[i:]

        return argv

    return argv


def _add_detailed_help(parser, download_parser, playlist_parser, search_parser):
    """Add detailed subcommand usage to the top-level help."""
    parser.epilog = f"""
Examples:
  smytm download [OPTIONS] <ID>
  smytm playlist [OPTIONS] <ID>
  smytm search [OPTIONS] <QUERY>

Download options:
{download_parser.format_help().rstrip()}

Playlist options:
{playlist_parser.format_help().rstrip()}

Search options:
{search_parser.format_help().rstrip()}
"""


def main():
    current_version = version("smytm")

    parser = argparse.ArgumentParser(
        prog="smytm",
        description=(
            "Search or download music and audio from "
            "YouTube / YouTube Music."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"smytm {current_version}",
    )
    parser.add_argument(
        "-gc",
        "--gen-config",
        action="store_true",
        help="Generate default config",
    )
    parser.add_argument(
        "-sc",
        "--show-config",
        action="store_true",
        help="Show current config",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="subcommands",
        metavar="{download,d,playlist,p,search,s}",
        description=(
            "Use one of the subcommands below. "
            "Run '<subcommand> --help' for focused help."
        ),
    )

    download_parser = subparsers.add_parser(
        "download",
        aliases=["d"],
        help="Download an audio by YouTube video ID",
        description="Download an audio by YouTube video ID.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    download_parser.add_argument(
        "video_id",
        help="11-character YouTube video ID",
    )
    download_parser.add_argument(
        "-f",
        "--format",
        help="Override audio format (opus, flac, ...)",
    )
    download_parser.add_argument(
        "-rg",
        "--replaygain",
        action="store_true",
        help="Apply ReplayGain 2.0 tags",
    )
    download_parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Output directory (overrides config/default)",
    )
    download_parser.add_argument(
        "-ly",
        "--lyrics",
        action="store_true",
        help="Download synchronized lyrics as an '.lrc' sidecar file",
    )

    playlist_parser = subparsers.add_parser(
        "playlist",
        aliases=["p"],
        help="Download an entire playlist",
        description="Download an entire playlist.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    playlist_parser.add_argument(
        "playlist_id",
        help="Playlist ID or URL",
    )
    playlist_parser.add_argument(
        "-f",
        "--format",
        help="Override audio format (opus, flac, ...)",
    )
    playlist_parser.add_argument(
        "-rg",
        "--replaygain",
        action="store_true",
        help="Apply ReplayGain 2.0 tags",
    )
    playlist_parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Output directory (overrides config/default)",
    )
    playlist_parser.add_argument(
        "-inv",
        "--inverse",
        action="store_true",
        help="Download videos in reverse order",
    )
    playlist_parser.add_argument(
        "-ly",
        "--lyrics",
        action="store_true",
        help="Download synchronized lyrics as an '.lrc' sidecar file",
    )

    search_parser = subparsers.add_parser(
        "search",
        aliases=["s"],
        help="Search for songs on YouTube Music",
        description="Search for songs on YouTube Music.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    search_parser.add_argument(
        "query",
        nargs="+",
        help="Search query",
    )
    search_parser.add_argument(
        "-c",
        "--count",
        type=positive_int,
        default=3,
        help="Number of search results",
    )
    search_parser.add_argument(
        "-ts",
        "--tsize",
        type=thumbnail_size,
        help="Thumbnail size for chafa (e.g., 16, 24, 40)",
    )

    _add_detailed_help(
        parser,
        download_parser,
        playlist_parser,
        search_parser,
    )

    argv = _normalize_leading_hyphen_id(sys.argv[1:])
    args = parser.parse_args(argv)

    if args.gen_config:
        config.create_default_config()
        return

    if args.show_config:
        config.show_config()
        return

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
