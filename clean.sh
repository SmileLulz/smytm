#!/usr/bin/env bash
# Removes build artifacts produced by build.bat and build.sh
set -euo pipefail

cd "$(dirname -- "${BASH_SOURCE[0]}")"

shopt -s nullglob

echo "Removing build artifacts..."

rm -fv ./smytm ./smytm.exe
rm -rfv ./dist
rm -fv ./*.pkg.tar.zst ./*.pkg.tar.zst.sig ./*.deb ./*.rpm 2>/dev/null || true

for d in packaging/*/; do
    rm -rfv "${d}src"
    rm -rfv "${d}pkg"
    rm -fv "${d}"*.pkg.tar.zst     2>/dev/null || true
    rm -fv "${d}"*.pkg.tar.zst.sig 2>/dev/null || true
    rm -fv "${d}"*.src.tar.*       2>/dev/null || true
done

echo "Done."
