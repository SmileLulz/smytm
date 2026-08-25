# Third party dependencies

This project relies on several open-source tools and libraries.

All of them (except `ytmusicapi`) run as subprocess rather than importing or linking.

Please refer to their respective repositories or websites for license information.


| Tool / Library                                        | Note                        | Depend   |
| ----------------------------------------------------- | --------------------------- | -------- |
| [python](https://github.com/python/cpython) (>= 3.10) | Base language               | Required |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp)            | Core                        | Required |
| [ffmpeg](https://ffmpeg.org/)                         | Core                        | Required |
| [ytmusicapi](https://github.com/sigma67/ytmusicapi)   | Core                        | Required |
| [mutagen](https://github.com/quodlibet/mutagen)       | For some metadata embedding | Required |
| [curl](https://github.com/curl/curl)                  | For searching thumbnail     | Required |
| [chafa](https://github.com/hpjansson/chafa)           | For thumbnail previews      | Required |
| [rsgain](https://github.com/complexlogic/rsgain)      | For ReplayGain 2.0 tagging  | Optional |
| [atomicparsley](https://github.com/wez/atomicparsley) | For M4A thumbnail embedding | Optional |
