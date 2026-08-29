# Third-party dependencies

`smytm` is a pure-Python CLI application. Python packages are installed
through the Python package manager, while command-line tools are expected to
be installed separately and available through `PATH`.

| Tool / Library | Purpose | Type | Required |
|---|---|---|---|
| [Python](https://github.com/python/cpython) (>= 3.10) | Base runtime | Python | Yes |
| [ytmusicapi](https://github.com/sigma67/ytmusicapi) | YouTube Music search/lyrics | Python package | Yes |
| [mutagen](https://github.com/quodlibet/mutagen) | Metadata support used by yt-dlp | Python package | Yes |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Audio/video downloading | External CLI | Yes |
| [ffmpeg](https://ffmpeg.org/) | Audio conversion/post-processing | External CLI | Yes |
| [chafa](https://github.com/hpjansson/chafa) | Terminal thumbnail previews | External CLI | Yes |
| [AtomicParsley](https://github.com/wez/atomicparsley) | M4A thumbnail embedding | External CLI | Optional |
| [rsgain](https://github.com/complexlogic/rsgain) | ReplayGain 2.0 tagging | External CLI | Optional |
| [LRCLIB](https://lrclib.net/) | Synchronized lyrics fallback | Online service | Optional |

`smytm` no longer requires `curl` for runtime operation; HTTPS requests are
performed with Python's standard library.

## Platform notes

### Linux

Install the Python package dependencies with:

```sh
python3 -m pip install smytm
```

Install the external tools using your distribution's package manager.

### Windows

Install the Python package with:

```powershell
py -m pip install smytm
```

Install the required external command-line tools separately and make sure
their installation directories are present in `PATH`.

`smytm` does not bundle third-party executables.
