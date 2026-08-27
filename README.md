<div align="center">
  <h1>🎵 smytm 🎵</h1>
  <h3>
    CLI utility for searching and downloading music and audio from YouTube and YouTube Music.
  </h3>
  <p>
    <b>smytm</b> is a command-line utility for searching and downloading music and audio from YouTube and YouTube Music. It uses yt-dlp and other external command-line tools for searching, downloading, metadata processing, and terminal output.
  </p>
</div>

<br></br>

> [!NOTE]
> This project was meant to be a personal project, but thought it would be nice to share it with others.
> 
> So, I am not accepting contributions. Thank you. Hope you like this small utility :)


# ✨ Features

- Search for songs in YouTube Music
- Download songs / playlists / any audios from YouTube Music or YouTube
- Download synchronized lyrics as `.lrc` sidecar files
- See [WIKI.md](https://github.com/SmileLulz/smytm/blob/main/WIKI.md) for more help.

**See [CHANGELOG.md](https://github.com/SmileLulz/smytm/blob/main/CHANGELOG.md) for latest update information.**


# 🔗 Dependencies

- [`Python`](https://github.com/python/cpython) (>= 3.10) (`python3`)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- [`ffmpeg`](https://ffmpeg.org/)
- [`ytmusicapi`](https://github.com/sigma67/ytmusicapi)
- [`mutagen`](https://github.com/quodlibet/mutagen)
- [`curl`](https://github.com/curl/curl)
- [`chafa`](https://github.com/hpjansson/chafa)
- [`AtomicParsley`](https://github.com/wez/atomicparsley) (optional - M4A thumbnail embedding)
- [`rsgain`](https://github.com/complexlogic/rsgain) (optional - ReplayGain 2.0 tagging)


# 📥 Install

> [!WARNING]
> Installing with `pip` won't install the dependencies; they are checked at runtime. Install them manually.

> [!WARNING]
> **Fedora** users must have RPM Fusion repository enabled and the full `ffmpeg` package installed from it. Fedora's `ffmpeg-free` package is not supported by `smytm`.

### For any distro

_This will install the latest release on any Arch or Fedora distributions._

Install:

```bash
curl -fsSL https://raw.githubusercontent.com/SmileLulz/smytm/main/install.sh | bash
```

But if you want to inspect the installation script first:

```bash
# Download the script
curl -fsSL https://raw.githubusercontent.com/SmileLulz/smytm/main/install.sh -o install.sh

# Inspect
less install.sh

# Then you can install with the downloaded script
bash install.sh
```


# 📦 Build by yourself

> Replace any `x.x` with the actual version tag.

### Clone the repository

```sh
git clone https://github.com/SmileLulz/smytm.git && cd smytm
```

### Running directly

> Install the dependencies manually first.

```sh
python3 -m smytm
```

### Build for Arch Linux

Build dependencies:

```sh
sudo pacman -S --needed \
    python-hatchling \
    python-build \
    python-installer \
    python-wheel
```

Build and install in one go:

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
> You must have RPM Fusion repository enabled and the full `ffmpeg` package installed from it. Fedora's `ffmpeg-free` package is not supported by `smytm`.

Build dependencies:

```sh
sudo dnf install \
    git \
    rpm-build \
    rpmdevtools \
    appstream \
    python3-devel \
    python3-hatchling \
    python3-pip \
    python3-rpm-generators
```

Create required directories:

```sh
mkdir -p rpm/{BUILD,BUILDROOT,RPMS,SOURCES,SRPMS}
```

> [!NOTE]
> Now, you have two options for your build:
> 
> Option 1: Use the release source archive.
>
> Option 2: Use a specific commit source archive.

Option 1:

_This is for most users who just want to build the release version._

> Make sure to `git checkout` to that commit tag first (e.g. `git checkout v1.6`).

Pull the release source archive:

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

Option 2:

_This is mostly for local testing or building from a specific commit._

> Make sure to `git checkout` to that commit first (e.g. `git checkout <commit_hash_or_tag>`).

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

Also see [DEPENDENCIES.md](https://github.com/SmileLulz/smytm/blob/main/DEPENDENCIES.md).
