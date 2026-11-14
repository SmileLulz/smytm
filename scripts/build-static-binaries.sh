#!/usr/bin/env bash
set -euo pipefail

VERSION="$(tr -d '[:space:]' < VERSION)"
OUTDIR="${1:-dist}"
mkdir -p "$OUTDIR"

TARGETS=(
    "linux/amd64"
    "linux/arm64"
    "linux/riscv64"
    "darwin/amd64"
    "darwin/arm64"
    "windows/amd64"
    "windows/arm64"
    "android/arm64"
)

for target in "${TARGETS[@]}"; do
    os="${target%/*}"
    arch="${target#*/}"
    ext=""
    [[ "$os" == "windows" ]] && ext=".exe"

    bin="$OUTDIR/smytm-$VERSION-$os-$arch$ext"
    echo "Building $os/$arch -> $bin ..."
    CGO_ENABLED=0 GOOS="$os" GOARCH="$arch" \
        go build \
        -trimpath \
        -ldflags "-s -w -X main.version=$VERSION" \
        -o "$bin" \
        ./src
done

if compgen -G "$OUTDIR/*" > /dev/null; then
    if command -v sha256sum >/dev/null 2>&1; then
        (cd "$OUTDIR" && sha256sum * > checksums.txt)
    else
        (cd "$OUTDIR" && shasum -a 256 * > checksums.txt)
    fi
fi
echo "Builds and checksums written to $OUTDIR/"
