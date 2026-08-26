<div align="center">
  <h1>🎵 smytm 🎵</h1>
  <h3>
    CLI utility for searching and downloading music and audio from YouTube and YouTube Music.
  </h3>
  <p>
    smytm is a command-line utility for searching and downloading music and audio from YouTube and YouTube Music. It uses yt-dlp and other external command-line tools for searching, downloading, metadata processing, and terminal output.
  </p>
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
> Installing with `pip` DOESN'T install the system dependencies automatically; they are checked at runtime. Install them manually. This applies only on installation with python `pip`.


# 📥 Install

> [!WARNING]
> For Fedora, you'll have to enable the `RPM Fusion Free` repository; which will provide `ffmpeg` package.
>
> Enable RPM Fusion Free repo: `sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm`
>
> Install/swap ffmpeg: `sudo dnf swap ffmpeg-free ffmpeg --allowerasing`

Guide will be added soon...


# 📦 Build by yourself

> Replace any `x.x` with the actual version tag.

### Clone the repository

```sh
git clone https://github.com/SmileLulz/smytm.git && cd smytm
```

### Running directly

Do this when you're testing.

```sh
python3 -m smytm
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

### Build for Fedora

> [!WARNING]
> You'll have to enable the `RPM Fusion Free` repository; which will provide proper `ffmpeg` package.
>
> Enable RPM Fusion Free repo: `sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm`
>
> Install/swap ffmpeg: `sudo dnf swap ffmpeg-free ffmpeg --allowerasing`

Dependencies:

- Will list soon...

Create required directories:

```sh
mkdir -p rpm/{BUILD,BUILDROOT,RPMS,SOURCES,SRPMS}
```

**⚠︎ Now, you have two options for your build:**

**Option 1:** Use the release source archive:

This is for most users who want to just build the release version.

> If you want to build an old or any previous version/commit, do `git checkout` to that commit tag first (e.g. `git checkout v1.6`).

Download the release source archive:

```sh
spectool --define "_topdir $PWD/rpm" rpm/SPECS/smytm.spec
```

Build:

```sh
rpmbuild --define "_topdir $PWD/rpm" -ba rpm/SPECS/smytm.spec
```

Install:

```sh
sudo dnf install rpm/RPMS/noarch/smytm-x.x-1.fcxx.noarch.rpm
```

**Option 2:** Use the local or specific commit source archive:

This is for local testing or building a specific version.

> If you want to build an old or any previous version/commit, do `git checkout` to that commit first (e.g. `git checkout <commit_hash_or_tag>`).

Create the source archive from current commit (replace `x.x` with the actual version):

```sh
git archive --format=tar.gz --prefix=smytm-x.x/ HEAD > rpm/SOURCES/vx.x.tar.gz
```

Build:

```sh
rpmbuild --define "_topdir $PWD/rpm" -ba rpm/SPECS/smytm.spec
```

Install:

```sh
sudo dnf install rpm/RPMS/noarch/smytm-x.x-1.fcxx.noarch.rpm
```


# 🧾 License

This project is licensed under the GNU General Public License v3.0 only.

Also see [THIRD-PARTIES.md](https://github.com/SmileLulz/smytm/blob/main/THIRD-PARTIES.md).
