<div align="center">
  <h1>🎵 smytm 🎵</h1>
  <h3>
    CLI utility for searching and downloading musics / audios from YouTube (Music).
    <br/>For non-audiophiles.<br>
  </h3>
</div>

<br></br>

> [!WARNING]
> This project was meant to be a personal project, but thought it would be nice to share it with others.
> 
> By the way, I am not accepting contributions. Thank you. Hope you like this utility :)

> [!WARNING]
> It's still in beta, some things and features may not avilable currently.


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
> Installing with `pip` DOESN'T install the dependencies automatically, they are all checked at runtime. So install them manually.
>
> This applies only on installation via python `pip`.


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
python -m smytm
```

### Build for python pip

```sh
# Build the package
python -m build

# Install locally
python -m pip install .

# Or install locally for development purposes
python -m pip install -e .
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

#And then install
sudo pacman -U smytm-x.x-1-any.pkg.tar.zst
```


# 🧾 License

This project is licensed under the GNU General Public License v3.0 only.

Also see [THIRD-PARTIES.md](https://github.com/SmileLulz/smytm/blob/main/THIRD-PARTIES.md).
