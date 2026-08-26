<div align="center">
  <h1>🎵 smytm 🎵</h1>
  <h3>
    CLI utility for searching and downloading music and audio from YouTube and YouTube Music.
    <br/>For non-audiophiles.<br>
  </h3>
</div>

<br></br>

> [!NOTE]
> This project was meant to be a personal project, but thought it would be nice to share it with others.
> 
> By the way, I am not accepting contributions. Thank you. Hope you like this small utility :)


# ✨ Features

- Search for songs in YouTube Music
- Download songs / playlists / any audios from YouTube Music or YouTube
- See [WIKI.md](https://github.com/SmileLulz/smytm/blob/main/WIKI.md) for more help.


# 🔗 Dependencies

- `python` (>= 3.10) (`python3`)
- `yt-dlp`
- `ffmpeg`
- `ytmusicapi`
- `mutagen`
- `curl`
- `chafa`
- `rsgain` (optional - ReplayGain 2.0 tagging)
- `atomicparsley` (optional - M4A thumbnail embedding)

> [!WARNING]
> Installing with `pip` DOESN'T install the system dependencies automatically; they are checked at runtime. Install them manually.
>
> This applies only on installation with python `pip`.


# 📥 Install

Guide will be added soon...


# 📦 Build by yourself

> Replace any `x.x` with the actual version tag.

### Clone the repository

```sh
git clone https://github.com/SmileLulz/smytm.git && cd smytm
```

### Running directly

```sh
python3 -m smytm
```

### Build for python pip

```sh
# Build the package
python3 -m build

# Install locally
python3 -m pip install .

# Or install locally for development purposes
python3 -m pip install -e .
```

### Build for Arch Linux

Dependencies:

- `python-hatchling`
- `python-build`
- `python-installer`
- `python-wheel`

```sh
sudo pacman -S --needed python-hatchling python-build python-installer python-wheel
```

Build and install in one go (recommended):

```sh
makepkg -si
```

Or:

```sh
# Build first
makepkg -s

# And then install
sudo pacman -U smytm-x.x-1-any.pkg.tar.zst
```


# 🧾 License

This project is licensed under the GNU General Public License v3.0 only.

Also see [THIRD-PARTIES.md](https://github.com/SmileLulz/smytm/blob/main/THIRD-PARTIES.md).
