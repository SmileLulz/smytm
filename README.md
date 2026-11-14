<div align="center">
  <h1>🎵 smytm 🎵</h1>
  <h3>A small CLI for searching and downloading music from YouTube Music.</h2>
</div>

<br>

> [!IMPORTANT]
> This started as a Python project. That one worked, but it dragged in a whole pile of things to install and keep working. I rewrote it in Go so it's just one binary you drop on your `PATH` (or install for your Linux distro) and forget about. Same features, fewer moving parts.
>
> Like my other little tools, I build this for my own use, and I am not taking PRs for now. Fork it if you want to change something.

<br>

## Features

- Search YouTube Music from the terminal, with a thumbnail preview (squared, not stretched)
- Download one track by video ID, URL, or just the song name
- Download an entire playlist the same way
- Stream a track without writing it to disk
- Write tags and album art into the file natively
- Grab synchronized lyrics as `.lrc` sidecars
- Optionally tag ReplayGain 2.0
- Read cookies from your browser, so age-gated or rate-limited videos just work

Everything except transcoding and `play` is pure Go. `ffmpeg` is only needed when you ask for a format YouTube does not serve natively. `rsgain` is only needed if you ask for ReplayGain.

## Install

### Prebuilt binaries

Grab the right file from the [releases page](https://github.com/SmileLulz/smytm/releases), then:

```bash
# Linux example
chmod +x smytm-linux-amd64
sudo mv smytm-linux-amd64 /usr/local/bin/smytm

# macOS example (Apple Silicon)
chmod +x smytm-darwin-arm64
sudo mv smytm-darwin-arm64 /usr/local/bin/smytm

# Termux example (Android)
chmod +x smytm-android-arm64
mv smytm-android-arm64 $PREFIX/bin/smytm
```

```powershell
# Windows example (PowerShell)
# Move it to a folder that is in your PATH, e.g., C:\Users\YourName\bin
Move-Item .\smytm-windows-amd64.exe C:\Users\YourName\bin\smytm.exe
```

### Arch Linux

```bash
# Build & install
git clone https://github.com/SmileLulz/smytm
cd smytm
./build.sh arch
sudo pacman -U dist/smytm-*.pkg.tar.zst

# Or grab the '.pkg.tar.zst' from releases
# and install it with 'pacman -U'
```

### Debian / Ubuntu

```bash
# Build & install
git clone https://github.com/SmileLulz/smytm
cd smytm
./build.sh deb
sudo dpkg -i dist/smytm_*_amd64.deb

# Or grab the '.deb' from releases
# and install it with 'dpkg -i'
```

### Fedora / RHEL

```bash
# Build & install
git clone https://github.com/SmileLulz/smytm
cd smytm
./build.sh rpm
sudo dnf install dist/smytm-*.rpm

# Or grab the '.rpm' from releases
# and install it with 'dnf install'
```

### Termux (Android)

```bash
# Build & install
pkg install golang ffmpeg rsgain termux-exec
git clone https://github.com/SmileLulz/smytm
cd smytm
bash build.sh go

# Or grab the prebuilt binary from releases and install it
chmod +x smytm-android-arm64
mv smytm-android-arm64 $PREFIX/bin/smytm
```

Want `smytm play` to work too? You also need `ffplay`, which lives in Termux's x11 repo:

```bash
pkg install x11-repo && pkg install ffplay
```

### From source

```bash
git clone https://github.com/SmileLulz/smytm
cd smytm
./build.sh go
# The binary lands at root
```

## Commands

| Command | What it does |
| --- | --- |
| `smytm search <query>` | Search YouTube Music, show video IDs and thumbnails |
| `smytm download <id\|url\|query>` | Download one track |
| `smytm download playlist <id\|url>` | Download a playlist |
| `smytm play <id\|url\|query>` | Stream a track without saving |
| `smytm version` | Print version info |

Short aliases: `s` for search, `d` for download, `p` for play, `pl` for playlist. So `smytm p <id>` plays, `smytm d pl <id>` downloads a playlist. (Yes, `p` at the top level and `pl` inside `download` is a bit odd. It made sense at the time.)

## Usage

```bash
# search
smytm search "lofi hip hop" -c 5

# download one track
smytm download lYBUbBu4W08

# or by URL
smytm download https://youtu.be/lYBUbBu4W08

# or just type the song name
smytm download never gonna give you up rick astley

# download a playlist
smytm download playlist PLSSHGgSg1ajc

# with lyrics and ReplayGain
smytm download lYBUbBu4W08 --lyrics --replaygain

# mp3 instead of the default opus
smytm download lYBUbBu4W08 -f mp3

# pick an output directory
smytm download lYBUbBu4W08 -p ~/Music/Downloads

# stream without saving
smytm play lYBUbBu4W08 -v 80
```

### Formats

| Format | Native? | Notes                                         |
| ------ | ------- | --------------------------------------------- |
| `opus` | yes     | Default. What YouTube serves most of the time |
| `m4a`  | yes     | Also served natively for some videos          |
| `mp3`  | no      | Needs `ffmpeg`                                |
| `flac` | no      | Needs `ffmpeg`                                |
| `ogg`  | no      | Needs `ffmpeg` (encodes Vorbis)               |
| `wav`  | no      | Needs `ffmpeg`                                |

"Native" means YouTube already has it, so `smytm` just writes bytes to disk. Non-native formats go through `ffmpeg`. If both the source and target are native and match, it does not re-encode - it just remuxes.

## Configuration

Config lives at:

- `$XDG_CONFIG_HOME/smytm/config.yaml`, or
- `~/.config/smytm/config.yaml` on Linux/macOS, or
- `%APPDATA%\smytm\config.yaml` on Windows

It is created with defaults on first run. Delete it to reset. Note that `smytm --help` and `smytm version` do not create it - the file only appears the first time you actually download or search something.

```yaml
# Where downloads go. Supports '~' for your home directory.
output_dir: "/home/you/Music"

# "opus" and "m4a" need no extra tools. Other values need ffmpeg.
format: "opus"

# yt-dlp-style quality selector. "0" = best.
audio_quality: "0"

# Append " - <artist>" to the filename.
artist_in_filename: true

# Always tag ReplayGain (needs rsgain).
replaygain_always: false

# Always write .lrc sidecars when available.
lyrics_always: false

# Skip the download if the target file already exists.
skip_always: false

# Thumbnail size, in terminal cells, for `search`.
thumbnail_size: 16

# Browser cookies. See below.
cookies_browser: ""
cookies_profile: ""
```

### Cookies

Every now and then YouTube gets suspicious of anonymous traffic and starts returning 403s or bot-checks. Or you are trying to download something age-restricted. Either way, `smytm` can read cookies from your logged-in browser.

```yaml
cookies_browser: "firefox" # or chrome, edge, brave, chromium, opera, vivaldi, safari
cookies_profile: ""        # optional, path to a specific cookie store
```

Or pass it on a single command:

```bash
smytm download lYBUbBu4W08 --cookies-browser firefox
```

Browser forks that keep their profiles in a non-standard place (Waterfox, LibreWolf, etc.) need `cookies_profile` pointed at the `cookies.sqlite` file inside the profile directory:

```yaml
cookies_browser: "firefox"
cookies_profile: "~/.waterfox/xxxx.default-release/cookies.sqlite"
```

### Lyrics

`--lyrics` asks YouTube Music for synced lyrics first. If YTM does not have them, it tries LRCLIB - synced if available, plain text as a last resort. Either way, the result lands as a `.lrc` file next to the audio.

### ReplayGain

`--replaygain` runs `rsgain` on the downloaded file. It is opt-in because `rsgain` is not part of the base install. Available from:

- Arch: `yay -S rsgain` or `paru -S rsgain`
- Debian/Ubuntu: `sudo apt install rsgain`
- Fedora: `sudo dnf install rsgain`
- Termux: `pkg install rsgain`
- Windows: [rsgain releases](https://github.com/complexlogic/rsgain/releases)

If `rsgain` is not on `$PATH`, `smytm` just says so and skips the step. Nothing breaks.

## Dependencies

| Tool     | Needed for                                                                    |
| -------- | ----------------------------------------------------------------------------- |
| `ffmpeg` | Non-native formats (`mp3`, `flac`, `ogg`, `wav`) and `play`                   |
| `ffplay` | `play` only. Bundled with `ffmpeg` on Linux/macOS/Windows; separate on Termux |
| `rsgain` | Optional, ReplayGain 2.0 tagging                                              |
| `git`    | Only if you clone from source                                                 |

Search, download, tagging, album art, and lyrics are all pure Go. No external binaries required.

## Building

```bash
./build.sh go      # native binary at ./smytm
./build.sh cross   # cross-compile everything into ./dist
./build.sh termux  # just the Termux build
./build.sh arch    # Arch package (needs makepkg)
./build.sh deb     # Debian .deb
./build.sh rpm     # Fedora .rpm
```

`build.sh` works on Linux and macOS unchanged. On Windows, use `build.bat` - it handles `go` and `cross` natively, and the package commands just tell you they are Linux-only.

Cross targets: `linux/{amd64,arm64,riscv64}`, `darwin/{amd64,arm64}`, `windows/{amd64,arm64}`, `android/arm64` (Termux).

## Testing

```bash
./test.sh              # Linux / macOS
./test-on-termux.sh    # Termux
test.bat               # Windows (runs test.sh via Git-for-Windows bash)
```

The test suite covers:

- Version, help, config auto-creation, invalid commands
- Live search against YouTube Music
- Single-track download by ID, URL, and song name
- Playlist download
- `--lyrics`, `--skip`, `--replaygain`, `~` expansion
- Tag and artwork verification via `ffprobe`

Network tests hit YouTube Music and LRCLIB, so if you are offline those will fail - that is expected. Set `KEEP=1` to keep the temp directory around for poking at.

## Notes and quirks

- **Song names vs IDs**: When you pass a search query to `download` or `play`, `smytm` first checks if it looks like a video ID (11 chars, `[A-Za-z0-9_-]`). If it does, it pings YouTube to see if the video exists before treating it as an ID. So `smytm download GangnamStyle` (11 chars, but not a real ID) still does the sensible thing and searches for it.
- **Hyphenated IDs**: Rare but real - some YouTube IDs start with a `-`. `smytm d -tR8sX7C1eI` works; the CLI injects `--` behind the scenes so the arg parser does not choke.
- **" - Topic" suffix**: YouTube auto-generates `Artist - Topic` channels for music distributed through a label aggregator. `smytm` strips that suffix from the artist name before building the filename, writing tags, and looking up lyrics, so you get `Never Gonna Give You Up - Rick Astley.opus` instead of `... - Rick Astley - Topic.opus`. The stripping only applies when the suffix is exactly `" - Topic"`; a channel genuinely named after the word "Topic" is left alone.

## License

[GPL-3.0-only](https://github.com/SmileLulz/smytm/blob/main/LICENSE)
