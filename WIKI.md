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

> Uses YouTube video ID

> [!WARNING]
> For IDs that has hiphen (`-`) as the first character, use double hiphen before the ID, like this: `smytm download -- -JZLqTnZZlY`, else it'll fail to download.

Download normally:

```sh
smytm download lYBUbBu4W08
```

Override the format:

```sh
smytm download lYBUbBu4W08 --format m4a
```

Apply ReplayGain (2.0) tags:

```sh
smytm download lYBUbBu4W08 --replaygain
```

Override the output/download path:

```sh
smytm download lYBUbBu4W08 --path ~/Downloads
```

### Download a playlist

> Uses YouTube playlist ID or full URL

> [!WARNING]
> For IDs that has hiphen (`-`) as the first character, use double hiphen before the ID, like this: `smytm download -- PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC`, else those tracks/audios will fail to download.

Download normally:

```sh
smytm playlist PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC
```

Override the download order:

```sh
smytm playlist PLj1lzMuovjRy-WbyMjqbeFA8QwjXstgLC --inverse
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


# ✨ Configuration

Config lives at `~/.config/smytm/config.json`:

| Key                  | Default   | Description                                                             |
| -------------------  | --------- | ----------------------------------------------------------------------- |
| `output_dir`         | `~/Music` | Where downloaded files are saved                                        |
| `format`             | `"opus"`  | Default audio format (can be overridden with `-f`/`--format`)           |
| `audio_quality`      | `"0"`     | yt-dlp audio quality (`0` = best, `9` = worst)                          |
| `artist_in_filename` | `true`    | Includes ` - Artist Name` in the end of the filename                    |
| `replaygain_always`  | `false`   | Always apply ReplayGain tags, without needing `-rg`/`--replaygain`      |
| `thumbnail_size`     | `"16"`    | Default thumbnail preview size (can be overridden with `-ts`/`--tsize`) |
| `nerd_font_icons`    | `true`    | Show Nerd Font icons in output; set `false` for plain text              |
