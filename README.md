<div align="center">
  <h1>🎵 smytm 🎵</h1>
  <h3>CLI utility for searching and downloading music or audio from YouTube and YouTube Music.</h3>
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

Python dependencies are declared by the package and installed automatically when using `pip`:

- [`ytmusicapi`](https://github.com/sigma67/ytmusicapi)
- [`mutagen`](https://github.com/quodlibet/mutagen)

The following command-line tools must be installed separately and available through `PATH`:

- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- [`ffmpeg`](https://ffmpeg.org/)
- [`chafa`](https://github.com/hpjansson/chafa)

Optional:

- [`AtomicParsley`](https://github.com/wez/atomicparsley) — M4A thumbnail embedding
- [`rsgain`](https://github.com/complexlogic/rsgain) — ReplayGain 2.0 tagging

**See [DEPENDENCIES.md](https://github.com/SmileLulz/smytm/blob/main/DEPENDENCIES.md) for additional platform notes.**

# 📥 Install

> [!WARNING]
> **Fedora** users must have/install **RPM Fusion Free** repository enabled and the full **ffmpeg** package installed from it. Fedora's **ffmpeg-free** package is **not** supported by smytm.

> Replace any `x.x` with the actual version tag.

## Linux (Python PIP)

_Make sure you have installed **python 3.10** or higher._

Download the latest `.whl` file from the [Releases](https://github.com/SmileLulz/smytm/releases) page.

```sh
# Install
pip install /path/to/smytm-x.x-py3-none-any.whl

# Or install for current user only
pip install --user /path/to/smytm-x.x-py3-none-any.whl
```

Then install the required command-line tools using your distribution's package manager.

## Linux (Arch & Fedora)

Install:

```sh
curl -fsSL https://raw.githubusercontent.com/SmileLulz/smytm/main/install.sh | bash
```

Or if you want to inspect the installation script first:

```sh
# Download the script
curl -fsSL https://raw.githubusercontent.com/SmileLulz/smytm/main/install.sh -o install.sh

# Inspect
less install.sh

# Then you can install with the downloaded script
bash install.sh
```

## Windows

_Make sure you have installed **python 3.10** or higher._

Download the latest `.whl` file from the [Releases](https://github.com/SmileLulz/smytm/releases) page.

Update python pip and packages:

```powershell
py -m pip install --upgrade pip
```

1. Install:

```powershell
py -m pip install path\to\smytm-x.x-py3-none-any.whl
```

2. Install requirements:

```sh
winget install yt-dlp.yt-dlp BtbN.FFmpeg.GPL hpjansson.Chafa wez.atomicparsley -e --accept-source-agreements --accept-package-agreements   
```

This installs `yt-dlp`, `ffmpeg`, `chafa` and `AtomicParsley`.

`AtomicParsley` is optional, but required for `M4A`'s thumbnail embedding. If you don't want `AtomicParsley`, just remove it from the line (`  wez.atomicparsley`).

3. To install `rsgain`, you must do it manually:

- Go to their official repository's [Release](https://github.com/complexlogic/rsgain/releases) page and download the windows zip file.
- Extract it anywhere.
- Open your environment variables' settings (you can search for it in the windows search bar).
- In the **System variables** section, select the `Path` or `PATH`, then click Edit.
- Now click **New**, then **Browse**, then select the extracted rsgain's folder where the `rsgain.exe` is located.

# 📦 Build by yourself

## Build the Python wheel

**Linux:**

```sh
python3 -m pip install --upgrade build hatchling

python3 -m build
```

**Windows:**

```powershell
py -m pip install --upgrade pip build hatchling

py -m build
```

**The resulting wheel should be:**

```text
dist/smytm-x.x-py3-none-any.whl
```

**Install it with:**

Linux:

```sh
python3 -m pip install dist/smytm-x.x-py3-none-any.whl
```

Windows:

```powershell
py -m pip install dist\smytm-*-py3-none-any.whl
```

Python dependencies declared by the project are installed automatically by `pip`; you must install required external command-line tools separately.

## Build for Arch Linux

Build dependencies:

```bash
sudo pacman -S --needed base-devel python-hatchling python-build python-installer python-wheel
```

Build and install:

```bash
makepkg -si
```

Or build first, then istall:

```bash
# Build
makepkg -s

# Install
sudo pacman -U smytm-x.x-1-any.pkg.tar.zst
```

## Build for Fedora

> [!WARNING]
> Fedora builds require RPM Fusion's full `ffmpeg` package.
> Fedora's `ffmpeg-free` package is not supported by `smytm`.

Build dependencies:

```bash
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

Create the build directories:

```bash
mkdir -p rpm/{BUILD,BUILDROOT,RPMS,SOURCES,SRPMS}
```

Build from the release source archive:

```bash
# Pull the source archive
spectool --define "_topdir $PWD/rpm" rpm/SPECS/smytm.spec

# Build
rpmbuild --define "_topdir $PWD/rpm" -ba rpm/SPECS/smytm.spec
```

Or create a source archive from a specific checked-out commit:

```bash
# Create the source archive
git archive --format=tar.gz --prefix=smytm-x.x/ HEAD > rpm/SOURCES/vx.x.tar.gz

# Build
rpmbuild --define "_topdir $PWD/rpm" -ba rpm/SPECS/smytm.spec
```

Install:

```bash
sudo dnf install rpm/RPMS/noarch/smytm-x.x-1.fcxx.noarch.rpm
```

See [WIKI.md](https://github.com/SmileLulz/smytm/blob/main/WIKI.md) for usage and configuration details.

# 🧾 License

This project is licensed under the GNU General Public License v3.0 only.

Also see [DEPENDENCIES.md](https://github.com/SmileLulz/smytm/blob/main/DEPENDENCIES.md).
