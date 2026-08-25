# Maintainer: SmileLulz <SmileLulz404@noreply.codeberg.org>

pkgname=ytmgrab
pkgver=1.2.1
pkgrel=1
pkgdesc="Download and search audio from YouTube Music"
arch=('any')
url="https://codeberg.org/SmileLulz404/ytmgrab"
license=('MIT')

depends=(
    'python>=3.11'
    'yt-dlp'
    'ffmpeg'
    'curl'
    'chafa'
    'python-ytmusicapi'
    'python-mutagen'
)

makedepends=(
    'python-build'
    'python-installer'
    'python-wheel'
    'python-setuptools'
)

optdepends=(
    'atomicparsley: Thumbnail embedding for M4A'
    'rsgain: ReplayGain 2.0 tagging'
)

source=()
sha256sums=()

build() {
    cd "$startdir"

    python -m build \
        --wheel \
        --no-isolation
}

package() {
    cd "$startdir"

    python -m installer \
        --destdir="$pkgdir" \
        dist/*.whl

    install -Dm644 \
        LICENSE \
        "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
