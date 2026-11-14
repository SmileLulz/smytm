package config

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/SmileLulz/smytm/src/appdirs"
	"gopkg.in/yaml.v3"
)

// Config is the on-disk configuration for smytm.
// Fields mirror the Python version's config so users can port over.
type Config struct {
	OutputDir        string `yaml:"output_dir"`
	Format           string `yaml:"format"`
	AudioQuality     string `yaml:"audio_quality"`
	ArtistInFilename bool   `yaml:"artist_in_filename"`
	ReplayGainAlways bool   `yaml:"replaygain_always"`
	LyricsAlways     bool   `yaml:"lyrics_always"`
	SkipAlways       bool   `yaml:"skip_always"`
	ThumbnailSize    int    `yaml:"thumbnail_size"`
	CookiesBrowser   string `yaml:"cookies_browser"`
	CookiesProfile   string `yaml:"cookies_profile"`
}

func defaults() *Config {
	home, _ := appdirs.Home()
	outDir := filepath.Join(home, "Music")
	return &Config{
		OutputDir:        outDir,
		Format:           "opus",
		AudioQuality:     "0",
		ArtistInFilename: true,
		ReplayGainAlways: false,
		LyricsAlways:     false,
		SkipAlways:       false,
		ThumbnailSize:    16,
		CookiesBrowser:   "",
		CookiesProfile:   "",
	}
}

// Path returns the config file location.
func Path() (string, error) {
	dir, err := appdirs.ConfigDir("smytm")
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, "config.yaml"), nil
}

// Load reads the config file. Missing file → defaults, nil error.
// Malformed file → error (we do not silently fall back).
func Load() (*Config, string, error) {
	path, err := Path()
	if err != nil {
		return nil, "", err
	}

	cfg := defaults()

	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return cfg, path, nil
		}
		return nil, path, err
	}

	// Decode into defaults so any field omitted keeps its default.
	if err := yaml.Unmarshal(data, cfg); err != nil {
		return nil, path, fmt.Errorf("parse %s: %w", path, err)
	}

	// Expand ~ in the output directory so it's always an absolute path
	cfg.OutputDir = appdirs.ExpandPath(cfg.OutputDir)

	if cfg.ThumbnailSize < 1 {
		return nil, path, fmt.Errorf("%s: thumbnail_size must be >= 1", path)
	}
	return cfg, path, nil
}

const defaultTemplate = `# smytm configuration

# Default downloads directory.
# Supports absolute path; or '~' for your home directory
# ('~' won't work on Windows, use absolute path instead).
output_dir: %q

# "opus" and "m4a" need no re-encoding.
# Other values (mp3, flac, ogg, wav) require re-encoding using ffmpeg.
format: %q

# yt-dlp-style quality selector. "0" = best.
audio_quality: %q

# Append " - <artist>" to the filename.
artist_in_filename: %v

# Always tag ReplayGain (needs rsgain installed).
replaygain_always: %v

# Always fetch and write an .lrc sidecar when available.
lyrics_always: %v

# Skip the download if the target file already exists.
skip_always: %v

# Thumbnail size (in terminal cells) for the search preview.
thumbnail_size: %d

# Browser cookie extraction (for age-restricted or rate-limited videos).

# Set cookies_browser to: chrome, firefox, edge, brave, chromium,
# opera, vivaldi, safari, or "auto" to auto-discover.
# Leave empty to disable cookie extraction entirely.
cookies_browser: %q

# Optional: explicit path to the browser's cookie store or profile directory.
# Leave empty to use the browser's default location.
# Supports absolute path; or '~' for your home directory
# ('~' won't work on Windows, use absolute path instead).
cookies_profile: %q
`

// Ensure creates the config file with defaults if it does not exist.
func Ensure() (string, error) {
	path, err := Path()
	if err != nil {
		return "", err
	}
	if _, err := os.Stat(path); err == nil {
		return path, nil
	} else if !os.IsNotExist(err) {
		return path, err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return path, err
	}
	d := defaults()
	content := fmt.Sprintf(defaultTemplate,
		d.OutputDir, d.Format, d.AudioQuality,
		d.ArtistInFilename, d.ReplayGainAlways,
		d.LyricsAlways, d.SkipAlways,
		d.ThumbnailSize,
		d.CookiesBrowser, d.CookiesProfile,
	)
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		return path, err
	}
	return path, nil
}
