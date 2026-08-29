# ✨ Usage

### Search for songs

> Searches on YouTube Music

Search normally:

```sh
smytm search never gonna give you up # or 'smytm search "never gonna give you up"'
```

Override the search result count:

```sh
smytm search never gonna give you up --count 5
```

Override the preview thumbnail size:

```sh
smytm search never gonna give you up --tsize 32 # 32x32 pixel
```

### Download a track / audio

> [!NOTE]
> Uses YouTube video ID.
>
> Always put the ID at the end. Example structure: `smytm [OPTIONS] <ID>`
>
> `smytm` handles IDs beginning with `-` automatically; users do not need to type `--`.

Download normally:

```sh
smytm download lYBUbBu4W08
```

Skip the download if it already exists:

```sh
smytm download --skip lYBUbBu4W08
```

Force-use YouTube instead of YouTube Music:

```sh
smytm download --youtube lYBUbBu4W08
```

Override the format:

```sh
smytm download --format m4a lYBUbBu4W08
```

Apply ReplayGain (2.0) tags:

```sh
smytm download --replaygain lYBUbBu4W08
```

Download lyrics as an `.lrc` sidecar file:

```sh
smytm download --lyrics lYBUbBu4W08
```

Override the output/download path:

```sh
smytm download --path ~/Downloads lYBUbBu4W08
```

### Download a playlist

> [!NOTE]
> Uses YouTube playlist ID or full URL.
>
> Always put the ID at the end. Example structure: `smytm [OPTIONS] <ID_or_URL>`

Download normally:

```sh
smytm playlist PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC
```

Skip tracks that already exists:

```sh
smytm playlist --skip PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC
```

Override the download order:

```sh
smytm playlist --inverse PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC
```

Download lyrics as an `.lrc` sidecar file for each track:

```sh
smytm playlist --lyrics PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC
```

### Other uses

Generate the config file:

```sh
smytm --gen-config
```

View the config file:

```sh
smytm --show-config
```

Show help message:

```sh
smytm --help
```

Show download help message:

```sh
smytm download --help
```

Show playlist help message:

```sh
smytm playlist --help
```

Show search help message:

```sh
smytm search --help
```


# ✨ Configuration

**Config location:**

- Linux: `$XDG_CONFIG_HOME/smytm/config.json`, or `~/.config/smytm/config.json` when `XDG_CONFIG_HOME` is not set
- Windows: `%APPDATA%\\smytm\\config.json`

| Key                  | Default   | Description                                                                 |
| -------------------  | --------- | --------------------------------------------------------------------------- |
| `output_dir`         | `~/Music` | Where downloaded files are saved                                            |
| `format`             | `"opus"`  | Default audio format (can be overridden with `-f`/`--format`)               |
| `audio_quality`      | `"0"`     | yt-dlp audio quality (`0` = best, `9` = worst)                              |
| `artist_in_filename` | `true`    | Includes ` - Artist Name` in the end of the filename                        |
| `replaygain_always`  | `true`    | Always apply ReplayGain tags, without needing `-rg`/`--replaygain`          |
| `lyrics_always`      | `false`   | Always download synchronized `.lrc` files, without needing `-ly`/`--lyrics` |
| `skip_always`        | `false`   | Always skip downloads when the output filename already exists               |
| `thumbnail_size`     | `"16"`    | Default thumbnail preview size (can be overridden with `-ts`/`--tsize`)     |
| `nerd_font_icons`    | `true`    | Show Nerd Font icons in output; set `false` for plain text                  |

**Linux config example:**

```json
{
    "output_dir": "/home/<Username>/Music",
    "format": "opus",
    "audio_quality": "0",
    "artist_in_filename": true,
    "replaygain_always": false,
    "lyrics_always": true,
    "skip_always": false,
    "thumbnail_size": "16",
    "nerd_font_icons": true
}
```

**WIndows config example:**

```json
{
    "output_dir": "C:\\Users\\<Username>\\Music",
    "format": "opus",
    "audio_quality": "0",
    "artist_in_filename": true,
    "replaygain_always": true,
    "lyrics_always": false,
    "skip_always": false,
    "thumbnail_size": "16",
    "nerd_font_icons": true
}
```
