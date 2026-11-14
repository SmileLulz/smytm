#!/data/data/com.termux/files/usr/bin/bash
# (UNTESTED SCRIPT)
# End-to-end test suite.
# Everything lives in a temp dir and is removed on exit unless KEEP=1.
set -euo pipefail


# Pre-check: required commands + pkg hints

pkg_hint() {
    case "$1" in
        go)             echo "pkg install golang" ;;
        ffmpeg|ffprobe) echo "pkg install ffmpeg" ;;
        rsgain)         echo "pkg install rsgain" ;;
        sha256sum|mktemp|basename|tr|dirname)
                        echo "pkg install coreutils" ;;
        find)           echo "pkg install findutils" ;;
        sed)            echo "pkg install sed" ;;
        grep)           echo "pkg install grep" ;;
        awk)            echo "pkg install gawk" ;;
        *)              echo "(no package hint for '$1')" ;;
    esac
}

missing=()
for cmd in go ffmpeg ffprobe sha256sum mktemp sed grep awk find basename tr dirname; do
    command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
done

if [ ${#missing[@]} -gt 0 ]; then
    {
        echo "error: missing required command(s):"
        for cmd in "${missing[@]}"; do
            printf '  %-10s -> %s\n' "$cmd" "$(pkg_hint "$cmd")"
        done
        echo
        echo "This script is meant to run inside Termux, where packages come"
        echo "from 'pkg install'. If you are not on Termux, use ./test.sh instead."
    } >&2
    exit 1
fi

if [ ! -f go.mod ] || [ ! -d src ]; then
    echo "error: go.mod and src/ must exist in the current directory" >&2
    echo "(run this script from the project root)" >&2
    exit 1
fi


# Temp root: Termux has no /tmp; use $TMPDIR or $PREFIX/tmp

TMP_ROOT="${TMPDIR:-${PREFIX:-/data/data/com.termux/files/usr}/tmp}"
if [ ! -d "$TMP_ROOT" ]; then
    mkdir -p "$TMP_ROOT"
fi

ROOT="$(mktemp -d "$TMP_ROOT/smytm-test.XXXXXX")"
cleanup() {
    if [ -n "${KEEP:-}" ]; then
        printf 'keeping test dir: %s\n' "$ROOT" >&2
        return
    fi
    chmod -R u+w "$ROOT" 2>/dev/null || true
    rm -rf "$ROOT"
}
trap cleanup EXIT


# Build FIRST, using the real HOME and module cache

BIN="$ROOT/smytm"
echo "Building test binary (native android/arm64)..."
go build -trimpath -buildvcs=false -o "$BIN" ./src || { echo "build failed" >&2; exit 1; }

# Isolate HOME and XDG for runtime tests
export HOME="$ROOT/home"
export XDG_CONFIG_HOME="$ROOT/xdg"
mkdir -p "$HOME" "$XDG_CONFIG_HOME"

shopt -s nullglob

pass=0
fail=0
skipped=0

ok()      { pass=$((pass+1)); printf 'ok    %s\n' "$1"; }
not_ok()  { fail=$((fail+1)); printf 'FAIL  %s\n' "$1"; [ -n "${2:-}" ] && printf '      %s\n' "$2"; }
skip()    { skipped=$((skipped+1)); printf 'skip  %s\n' "$1"; }

assert_contains() {
    case "$2" in
        *"$3"*) ok "$1" ;;
        *) not_ok "$1" "missing '$3'" ;;
    esac
}

assert_file() {
    if [ -f "$2" ]; then ok "$1"; else not_ok "$1" "missing file: $2"; fi
}

assert_eq() {
    if [ "$2" = "$3" ]; then ok "$1"; else not_ok "$1" "expected '$3', got '$2'"; fi
}


# Offline tests

test_version() {
    local out
    out="$("$BIN" version 2>/dev/null)" || { not_ok "version runs"; return; }
    assert_contains "version prints name" "$out" "smytm"
    assert_contains "version prints go info" "$out" "go "
    assert_contains "version prints android" "$out" "android/arm64"
}

test_help() {
    local out
    out="$("$BIN" --help 2>&1)" || { not_ok "--help runs"; return; }
    assert_contains "help: download" "$out" "download"
    assert_contains "help: search"   "$out" "search"
    assert_contains "help: play"     "$out" "play"
    assert_contains "help: version"  "$out" "version"
}

test_download_help() {
    local out
    out="$("$BIN" download --help 2>&1)" || { not_ok "download --help runs"; return; }
    assert_contains "help: --format"     "$out" "--format"
    assert_contains "help: --path"       "$out" "--path"
    assert_contains "help: --lyrics"     "$out" "--lyrics"
    assert_contains "help: --replaygain" "$out" "--replaygain"
    assert_contains "help: --skip"       "$out" "--skip"
    assert_contains "help: playlist"     "$out" "playlist"
}

test_play_help() {
    local out
    out="$("$BIN" play --help 2>&1)" || { not_ok "play --help runs"; return; }
    assert_contains "help: --volume" "$out" "--volume"
}

test_invalid_command() {
    if "$BIN" foobar-nope >/dev/null 2>&1; then
        not_ok "invalid command fails"
    else
        ok "invalid command fails"
    fi
}

test_config() {
    local xdg="$ROOT/xdg-cfg"
    rm -rf "$xdg"
    mkdir -p "$xdg"
    XDG_CONFIG_HOME="$xdg" "$BIN" version >/dev/null 2>&1 || { not_ok "config: bootstrap"; return; }
    local cfg="$xdg/smytm/config.yaml"
    assert_file "config: auto-created" "$cfg"
    if [ -f "$cfg" ]; then
        assert_contains "config: default format=opus"       "$(cat "$cfg")" 'format: "opus"'
        assert_contains "config: default thumbnail_size=16" "$(cat "$cfg")" 'thumbnail_size: 16'
    fi
}


# Network: single track (rickroll)

test_search() {
    local out
    out="$("$BIN" search "rick astley" -c 1 --tsize 2 2>&1)" || { not_ok "search runs" "$out"; return; }
    assert_contains "search: shows title" "$out" "Title"
    assert_contains "search: shows ID"    "$out" "ID"
}

test_download_id() {
    local dir="$ROOT/dl-id"
    mkdir -p "$dir"
    local out
    out="$("$BIN" download lYBUbBu4W08 -p "$dir" 2>&1)" || { not_ok "download runs" "$out"; return; }
    assert_contains "download: prints Saved" "$out" "Saved"
    local count
    count=$(find "$dir" -maxdepth 1 -name '*.opus' | wc -l)
    if [ "$count" -ge 1 ]; then ok "download: produced .opus file"
    else not_ok "download: produced .opus file" "no .opus in $dir"; fi
}

test_download_m4a() {
    local dir="$ROOT/dl-m4a"
    mkdir -p "$dir"
    "$BIN" download lYBUbBu4W08 -p "$dir" -f m4a >/dev/null 2>&1 || { not_ok "download -f m4a"; return; }
    local count
    count=$(find "$dir" -maxdepth 1 -name '*.m4a' | wc -l)
    if [ "$count" -ge 1 ]; then ok "download: -f m4a produced .m4a"
    else not_ok "download: -f m4a produced .m4a"; fi
}

test_download_url() {
    local dir="$ROOT/dl-url"
    mkdir -p "$dir"
    "$BIN" download "https://youtu.be/lYBUbBu4W08" -p "$dir" >/dev/null 2>&1 || { not_ok "download by URL"; return; }
    local count
    count=$(find "$dir" -maxdepth 1 -name '*.opus' | wc -l)
    if [ "$count" -ge 1 ]; then ok "download: URL input works"
    else not_ok "download: URL input works"; fi
}

test_download_query() {
    local dir="$ROOT/dl-query"
    mkdir -p "$dir"
    local out
    out="$("$BIN" download "never gonna give you up rick astley" -p "$dir" 2>&1)" || { not_ok "query download"; return; }
    assert_contains "download: query shows Searching" "$out" "Searching"
    local count
    count=$(find "$dir" -maxdepth 1 -name '*.opus' | wc -l)
    if [ "$count" -ge 1 ]; then ok "download: query input works"
    else not_ok "download: query input works"; fi
}

test_download_lyrics() {
    local dir="$ROOT/dl-lyrics"
    mkdir -p "$dir"
    "$BIN" download lYBUbBu4W08 -p "$dir" --lyrics >/dev/null 2>&1 || { not_ok "download --lyrics"; return; }
    local count
    count=$(find "$dir" -maxdepth 1 -name '*.lrc' | wc -l)
    if [ "$count" -ge 1 ]; then ok "download: --lyrics produced .lrc"
    else not_ok "download: --lyrics produced .lrc"; fi
}

test_download_skip() {
    local dir="$ROOT/dl-skip"
    mkdir -p "$dir"
    "$BIN" download lYBUbBu4W08 -p "$dir" >/dev/null 2>&1 || { not_ok "skip: first download"; return; }
    local out
    out="$("$BIN" download lYBUbBu4W08 -p "$dir" --skip 2>&1)" || { not_ok "skip: second download"; return; }
    assert_contains "skip: prints Skipped" "$out" "Skipped"
    local count
    count=$(find "$dir" -maxdepth 1 -name '*.opus' | wc -l)
    assert_eq "skip: no duplicate file" "$count" "1"
}

test_download_tilde() {
    "$BIN" download lYBUbBu4W08 -p "~/tilde-test" >/dev/null 2>&1 || { not_ok "tilde: download runs"; return; }
    local count
    count=$(find "$HOME/tilde-test" -maxdepth 1 -name '*.opus' 2>/dev/null | wc -l)
    if [ "$count" -ge 1 ]; then ok "tilde: ~ expands to \$HOME"
    else not_ok "tilde: ~ expands to \$HOME" "no file in $HOME/tilde-test"; fi
}

test_download_replaygain() {
    if ! command -v rsgain >/dev/null 2>&1; then
        skip "download: --replaygain (rsgain not installed)"
        return
    fi
    local dir="$ROOT/dl-rg"
    mkdir -p "$dir"
    local out
    out="$("$BIN" download lYBUbBu4W08 -p "$dir" --replaygain 2>&1)" || { not_ok "replaygain runs"; return; }
    assert_contains "replaygain: tags applied" "$out" "ReplayGain tags applied"
}


# Network: playlist

test_playlist() {
    local dir="$ROOT/playlist"
    mkdir -p "$dir"
    local out
    out="$("$BIN" download playlist PLSSHGgSg1ajc -p "$dir" 2>&1)" || { not_ok "playlist runs" "$out"; return; }
    if echo "$out" | grep -qE "Found [0-9]+ tracks"; then
        ok "playlist: discovered tracks"
    else
        not_ok "playlist: discovered tracks" "$out"
    fi
    local count
    count=$(find "$dir" -maxdepth 1 -name '*.opus' | wc -l)
    if [ "$count" -ge 1 ]; then ok "playlist: downloaded $count tracks"
    else not_ok "playlist: downloaded tracks" "found $count"; fi
}


# Post-check: tags + artwork

test_tags_embedded() {
    local file
    file=$(find "$ROOT/dl-id" -maxdepth 1 -name '*.opus' 2>/dev/null | head -1)
    if [ -z "$file" ]; then
        skip "tags: no .opus file from download test"
        return
    fi
    local streams
    streams=$(ffprobe -show_streams "$file" 2>/dev/null || true)
    if echo "$streams" | grep -q "codec_type=audio"; then ok "tags: audio stream present"
    else not_ok "tags: audio stream present"; fi
    if echo "$streams" | grep -q "codec_type=video"; then ok "tags: artwork stream present"
    else not_ok "tags: artwork stream present"; fi
}


# Run

run_test() {
    printf '== %s\n' "$1"
    shift
    set +e
    "$@"
    set -e
}

run_test "version"                         test_version
run_test "--help"                          test_help
run_test "download --help"                 test_download_help
run_test "play --help"                     test_play_help
run_test "invalid command"                 test_invalid_command
run_test "config"                          test_config
run_test "search (network)"                test_search
run_test "download by ID (network)"        test_download_id
run_test "download -f m4a (network)"       test_download_m4a
run_test "download by URL (network)"       test_download_url
run_test "download by query (network)"     test_download_query
run_test "download --lyrics (network)"     test_download_lyrics
run_test "download --skip (network)"       test_download_skip
run_test "download ~ expansion (network)"  test_download_tilde
run_test "download --replaygain (network)" test_download_replaygain
run_test "playlist (network)"              test_playlist
run_test "tags embedded"                   test_tags_embedded

printf '\npassed: %d, failed: %d, skipped: %d\n' "$pass" "$fail" "$skipped"
[ "$fail" -eq 0 ]
