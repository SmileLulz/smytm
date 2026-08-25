# ❤️ ytmgrab

Search or download audios from YouTube / YouTube Music


> This project was meant to be a personal project, but I'm sharing anyways. Therefore, I am not accepting any contributions. Thank you.


## Features

- Search for songs in YouTube Music
- Download songs or any audios or playlists from YouTube Music or YouTube (as fallback)
- Customize your experience with config file or directly through the cli


## Requirements

- [Python](https://github.com/python/cpython) >= 3.11
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/) (required)
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) and [mutagen](https://github.com/quodlibet/mutagen) (Python packages, required)
- [curl](https://github.com/curl/curl) and [chafa](https://github.com/hpjansson/chafa) (required for searching for thumbnail previews)
- [AtomicParsley](https://github.com/wez/atomicparsley) (optional, but M4A thumbnail embedding may fail without it)
- [rsgain](https://github.com/complexlogic/rsgain) (optional, for ReplayGain 2.0 tagging)

In `pip` build, these are all checked at runtime rather than installed automatically.
For Arch Linux, `PKGBUILD` declares them all as package dependencies.


## Install

Via the `PKGBUILD` (Arch Linux):

```sh
makepkg -csfCi
```

Or with pip, bringing your own system tools:

```sh
pip install .
```


## Usage

```sh
# Download a track by YouTube video ID
ytmgrab download 8BiLurrzFRw

# Override the output format, and tag with ReplayGain
ytmgrab download 8BiLurrzFRw --format m4a --replaygain

# Override the output path
ytmgrab download 8BiLurrzFRw --path ~/Downloads

# Download a playlist by ID or full URL
ytmgrab playlist PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC

# Override the download order
ytmgrab playlist PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC --inverse

# Search in YouTube Music
ytmgrab search night changes
# Or
ytmgrab search 'night changes'

# Override the search result count and preview thumbnail size
ytmgrab search night changes --count 5 --tsize 32 # 32x32 pixel

# Generate / view the config file
ytmgrab --gen-config
ytmgrab --show-config

# Show help message
ytmgrab --help
```

**Note**: For IDs that has hiphen (`-`) as the first character, use double hiphen before the ID, like this: `ytmgrab download -- -JZLqTnZZlY`, else it'll fail as an option.


## Configuration

Config lives at `~/.config/ytmgrab/config.json`:

| Key                  | Default   | Description                                                             |
| -------------------  | --------- | ----------------------------------------------------------------------- |
| `output_dir`         | `~/Music` | Where downloaded files are saved                                        |
| `format`             | `"opus"`  | Default audio format (can be overridden with `-f`/`--format`)           |
| `audio_quality`      | `"0"`     | yt-dlp audio quality (`0` = best, `9` = worst)                          |
| `artist_in_filename` | `true`    | Includes ` - Artist Name` in the end of the filename                    |
| `replaygain_always`  | `false`   | Always apply ReplayGain tags, without needing `-rg`/`--replaygain`      |
| `thumbnail_size`     | `"16"`    | Default thumbnail preview size (can be overridden with `-ts`/`--tsize`) |
| `nerd_font_icons`    | `true`    | Show Nerd Font icons in output; set `false` for plain text              |


## License

This project is licensed under the MIT License.

### Third-party dependencies

This project relies on several open-source tools and libraries.
Please refer to their respective repositories or websites for license information (see [Requirements section](#requirements)).
