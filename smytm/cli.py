"""Command-line interface for ytmgrab."""

import argparse
from . import config

def main():
    parser = argparse.ArgumentParser(
        prog="ytmgrab",
        description="Search or download audios from YouTube / YouTube Music."
    )
    subparsers = parser.add_subparsers(dest="command", required=False, help="Subcommand")

    # Download args
    download_parser = subparsers.add_parser("download", aliases=['d'], help="Download an audio by YouTube video ID")
    download_parser.add_argument("video_id", help="11-character YouTube video ID")
    download_parser.add_argument("-f", "--format", help="Override audio format (opus, flac, ...)")
    download_parser.add_argument("-rg", "--replaygain", action="store_true", help="Apply ReplayGain 2.0 tags")
    download_parser.add_argument("-p", "--path", type=str, help="Output directory (overrides config/default)")

    # Download playlist args
    playlist_parser = subparsers.add_parser("playlist", aliases=['p'], help="Download an entire playlist")
    playlist_parser.add_argument("playlist_id", help="Playlist ID or URL")
    playlist_parser.add_argument("-f", "--format", help="Override audio format (opus, flac, ...)")
    playlist_parser.add_argument("-rg", "--replaygain", action="store_true", help="Apply ReplayGain 2.0 tags")
    playlist_parser.add_argument("-p", "--path", type=str, help="Output directory (overrides config/default)")
    playlist_parser.add_argument("-inv", "--inverse", action="store_true", help="Download videos in reverse order")

    # Search args
    search_parser = subparsers.add_parser("search", aliases=['s'], help="Search for songs on YouTube Music")
    search_parser.add_argument("query", nargs="+", help="Search query")
    search_parser.add_argument("-c", "--count", type=int, default=3, help="Number of search results")
    search_parser.add_argument("-ts", "--tsize", type=str, help="Thumbnail size for chafa (e.g., 16x16, 24x24, 40x40)")

    # Global flags: config generation/show
    parser.add_argument("-gc", "--gen-config", action="store_true", help="Generate default config")
    parser.add_argument("-sc", "--show-config", action="store_true", help="Show current config")

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
