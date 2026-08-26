# Maintainer: SmileLulz <SmileLulz@users.noreply.github.com>

pkgname=smytm
pkgver=1.1.b5
pkgrel=1
pkgdesc="CLI utility for searching and downloading musics / audios from YouTube (Music)."
arch=('any')
url="https://github.com/SmileLulz/smytm"
license=('GPL-3.0-only')

depends=(
    'python>=3.10'
    'python-ytmusicapi'
    'python-mutagen'
    'yt-dlp'
    'ffmpeg'
    'curl'
    'chafa'
)

makedepends=(
    'python-hatchling'
    'python-build'
    'python-installer'
    'python-wheel'
)

optdepends=(
    'atomicparsley: Thumbnail embedding for M4A'
    'rsgain: ReplayGain 2.0 tagging'
)

source=()
sha256sums=()

build() {
    cd "$startdir"
    python -m build --wheel --no-isolation
}

package() {
    cd "$startdir"

    python -m installer --destdir="$pkgdir" dist/*.whl

    install -Dm644 LICENSE \
        "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
