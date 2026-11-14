#!/usr/bin/env bash
set -euo pipefail

VERSION="$(tr -d '[:space:]' < VERSION 2>/dev/null || echo "1.0.0")"
OS="$(uname -s)"

NATIVE_ARCH="$(go env GOARCH)"
case "$NATIVE_ARCH" in
    amd64) NFPM_ARCH="amd64" ;;
    arm64) NFPM_ARCH="arm64" ;;
    arm)   NFPM_ARCH="armv7" ;;
    *)     NFPM_ARCH="$NATIVE_ARCH" ;;
esac

usage() {
    cat >&2 <<EOF
Usage: $(basename "$0") <command> [extra args...]

Commands:
  go             Build for the current OS/arch (outputs ./smytm)
  cross          Cross-compile all supported OS/arch targets into ./dist
  termux         Cross-compile for Termux (android/arm64) into ./dist
  arch           Build the Arch Linux package using makepkg (Linux only)
  deb            Build a Debian/Ubuntu .deb package
  rpm            Build a Fedora/RHEL .rpm package
EOF
}

regen_checksums() {
    if [[ -d dist ]] && compgen -G "dist/*" > /dev/null; then
        if command -v sha256sum >/dev/null 2>&1; then
            (cd dist && sha256sum * > checksums.txt)
        else
            (cd dist && shasum -a 256 * > checksums.txt)
        fi
    fi
}

run_go() {
    CGO_ENABLED=0 go build \
        -trimpath \
        -ldflags "-s -w -X main.version=$VERSION" \
        -o smytm ./src "$@"
}

run_cross() {
    ./scripts/build-static-binaries.sh dist "$@"
}

run_termux() {
    local outdir="${1:-dist}"
    mkdir -p "$outdir"

    local out="$outdir/smytm-$VERSION-android-arm64"
    echo "Building android/arm64 -> $out ..."
    CGO_ENABLED=0 GOOS=android GOARCH=arm64 \
        go build \
        -trimpath \
        -buildvcs=false \
        -ldflags "-s -w -X main.version=$VERSION" \
        -o "$out" \
        ./src

    if [[ "$outdir" == "dist" ]]; then
        regen_checksums
    fi
}

run_arch() {
    if [[ "$OS" == "Darwin" ]]; then
        echo "Error: The 'arch' command is only supported on Linux (Arch)." >&2
        exit 1
    fi
    if ! command -v makepkg >/dev/null 2>&1; then
        echo "Error: makepkg not found. Are you on Arch Linux?" >&2
        exit 1
    fi

    mkdir -p dist
    export PKGDEST="$PWD/dist"

    makepkg --dir packaging/arch --syncdeps --cleanbuild --clean "$@"
    regen_checksums
}

run_nfpm() {
    local pkg_type="$1"
    shift

    run_go
    mkdir -p dist

    echo "Building .$pkg_type package for $NFPM_ARCH (v$VERSION)..."
    ARCH="$NFPM_ARCH" VERSION="$VERSION" \
        go run github.com/goreleaser/nfpm/v2/cmd/nfpm@v2.49.0 pkg \
        --packager "$pkg_type" \
        --config packaging/nfpm.yaml \
        --target "dist/"

    regen_checksums
}

if [[ $# -lt 1 ]]; then
    usage
    exit 1
fi

case "$1" in
    -h|--help) usage; exit 0 ;;
    go)        shift; run_go "$@" ;;
    cross)     shift; run_cross "$@" ;;
    termux)    shift; run_termux "$@" ;;
    arch)      shift; run_arch "$@" ;;
    deb)       shift; run_nfpm "deb" "$@" ;;
    rpm)       shift; run_nfpm "rpm" "$@" ;;
    *)         echo "Error: unknown command '$1'" >&2; usage; exit 1 ;;
esac
