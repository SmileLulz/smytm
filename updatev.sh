#!/usr/bin/env bash

set -euo pipefail

PYPROJECT="pyproject.toml"
PKGBUILD="PKGBUILD"
CHANGELOG="CHANGELOG.md"
SPEC="rpm/SPECS/smytm.spec"

PKGBUILD_MAINTAINER="SmileLulz <SmileLulz@users.noreply.github.com>"
SPEC_PACKAGER="SmileLulz"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage:
  $0 1|--major           Bump major version (1.2 -> 2.0)
  $0 2|--minor           Bump minor version (1.2 -> 1.3)
  $0 -s|--set X.Y[...]   Set explicit version (e.g. 1.6, 1.6.b1, 2.0.rc1)
EOF
    exit 1
}

get_current_version() {
    sed -nE 's/^version = "([^"]+)"/\1/p' "$PYPROJECT" | head -n1
}

get_pkgname() {
    sed -nE 's/^pkgname=([^[:space:]]+)/\1/p' "$PKGBUILD" | head -n1
}

validate_version() {
    local version="$1"

    [[ "$version" =~ ^[0-9]+\.[0-9]+$ ||
       "$version" =~ ^[0-9]+\.[0-9]+\.[^[:space:]]+$ ]]
}

validate_changelog() {
    local version="$1"

    python3 - "$CHANGELOG" "$version" <<'PY'
import re
import sys
from pathlib import Path

changelog_path = Path(sys.argv[1])
version = sys.argv[2]

text = changelog_path.read_text(encoding="utf-8")

pattern = (
    rf"^###\s+v{re.escape(version)}\s*\n"
    rf"(.*?)(?=^###\s+v|\Z)"
)

match = re.search(
    pattern,
    text,
    re.MULTILINE | re.DOTALL,
)

if not match:
    raise SystemExit(
        f"Error: CHANGELOG.md does not contain '### v{version}'."
    )

entries = [
    line.strip()
    for line in match.group(1).splitlines()
    if line.strip().startswith("- ")
]

if not entries:
    raise SystemExit(
        f"Error: '### v{version}' contains no changelog entries."
    )

print(f"Changelog validated: v{version}")
for entry in entries:
    print(f"  {entry}")
PY
}

bump_version() {
    local current="$1"
    local type="$2"

    if [[ ! "$current" =~ ^[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}Error: ${type} bump requires a clean X.Y version.${NC}" >&2
        echo -e "${RED}Current version: '${current}'${NC}" >&2
        echo -e "${YELLOW}Use --set to explicitly set a version with a suffix.${NC}" >&2
        exit 1
    fi

    local major
    local minor

    IFS='.' read -r major minor <<< "$current"

    case "$type" in
        major)
            echo "$((major + 1)).0"
            ;;
        minor)
            echo "${major}.$((minor + 1))"
            ;;
        *)
            echo -e "${RED}Error: Unknown bump type '$type'${NC}" >&2
            exit 1
            ;;
    esac
}

update_files() {
    local new_version="$1"
    local current_pkgname
    local fedora_date

    current_pkgname=$(get_pkgname)
    fedora_date=$(date '+%a %b %d %Y')

    if [[ "$current_pkgname" != "smytm" ]]; then
        echo -e "${RED}Error: PKGBUILD contains unexpected pkgname: '${current_pkgname}'${NC}" >&2
        echo -e "${RED}Expected: smytm${NC}" >&2
        exit 1
    fi

    # pyproject.toml
    sed -i \
        "s/^version = \".*\"/version = \"${new_version}\"/" \
        "$PYPROJECT"

    # Arch PKGBUILD
    sed -i \
        "s/^pkgver=.*/pkgver=${new_version}/" \
        "$PKGBUILD"

    if grep -q '^# Maintainer:' "$PKGBUILD"; then
        sed -i \
            "s/^# Maintainer:.*/# Maintainer: ${PKGBUILD_MAINTAINER}/" \
            "$PKGBUILD"
    fi

    # Fedora spec
    sed -i \
        "s/^Version:.*/Version:        ${new_version}/" \
        "$SPEC"

    # Fedora changelog
    python3 - "$SPEC" "$CHANGELOG" "$new_version" "$fedora_date" "$SPEC_PACKAGER" <<'PY'
import re
import sys
from pathlib import Path

spec_path = Path(sys.argv[1])
changelog_path = Path(sys.argv[2])
version = sys.argv[3]
date = sys.argv[4]
packager = sys.argv[5]

changelog_text = changelog_path.read_text(encoding="utf-8")

pattern = (
    rf"^###\s+v{re.escape(version)}\s*\n"
    rf"(.*?)(?=^###\s+v|\Z)"
)

match = re.search(
    pattern,
    changelog_text,
    re.MULTILINE | re.DOTALL,
)

if not match:
    raise SystemExit(
        f"Error: CHANGELOG.md does not contain '### v{version}'."
    )

entries = [
    line.strip()
    for line in match.group(1).splitlines()
    if line.strip().startswith("- ")
]

if not entries:
    raise SystemExit(
        f"Error: '### v{version}' contains no changelog entries."
    )

spec_text = spec_path.read_text(encoding="utf-8")

marker = "%changelog"

if marker not in spec_text:
    raise SystemExit(
        "Error: %changelog section not found in Fedora spec."
    )

before, _ = spec_text.split(marker, 1)

new_changelog = (
    f"* {date} {packager} - {version}-1\n"
    + "\n".join(entries)
    + "\n"
)

spec_path.write_text(
    before.rstrip()
    + "\n\n%changelog\n"
    + new_changelog,
    encoding="utf-8",
)

print(f"Using changelog: v{version}")
for entry in entries:
    print(entry)
PY

    echo -e "${GREEN}✓ Updated pyproject.toml${NC}"
    echo -e "${GREEN}✓ Updated PKGBUILD${NC}"
    echo -e "${GREEN}✓ Updated Fedora spec${NC}"
}

if [[ $# -lt 1 ]]; then
    usage
fi

for file in "$PYPROJECT" "$PKGBUILD" "$CHANGELOG" "$SPEC"; do
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}Error: Required file not found: $file${NC}" >&2
        exit 1
    fi
done

case "$1" in
    1|--major)
        current_version=$(get_current_version)

        if [[ -z "$current_version" ]]; then
            echo -e "${RED}Error: Could not determine current version from ${PYPROJECT}.${NC}" >&2
            exit 1
        fi

        new_version=$(bump_version "$current_version" "major")
        bump_type="major"

        echo -e \
            "${YELLOW}Bumping ${bump_type} version: ${current_version} -> ${new_version}${NC}"
        ;;

    2|--minor)
        current_version=$(get_current_version)

        if [[ -z "$current_version" ]]; then
            echo -e "${RED}Error: Could not determine current version from ${PYPROJECT}.${NC}" >&2
            exit 1
        fi

        new_version=$(bump_version "$current_version" "minor")
        bump_type="minor"

        echo -e \
            "${YELLOW}Bumping ${bump_type} version: ${current_version} -> ${new_version}${NC}"
        ;;

    -s|--set)
        if [[ $# -lt 2 || -z "${2:-}" ]]; then
            echo -e "${RED}Error: Version required with --set${NC}" >&2
            usage
        fi

        new_version="$2"

        if ! validate_version "$new_version"; then
            echo -e "${RED}Error: Invalid version format: ${new_version}${NC}" >&2
            echo -e \
                "${YELLOW}Examples: 1.6, 1.6.b1, 1.6.alpha, 2.0.rc1${NC}" >&2
            exit 1
        fi

        echo -e "${YELLOW}Setting version to: ${new_version}${NC}"
        ;;

    --help|-h)
        usage
        ;;

    *)
        echo -e "${RED}Error: Unknown option '$1'${NC}" >&2
        usage
        ;;
esac

if ! validate_version "$new_version"; then
    echo -e "${RED}Error: Invalid version format: ${new_version}${NC}" >&2
    exit 1
fi

validate_changelog "$new_version"

update_files "$new_version"

echo
echo -e "${GREEN}✓ Version successfully updated to ${new_version}-1${NC}"
