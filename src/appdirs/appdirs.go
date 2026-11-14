package appdirs

import (
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

// Home returns the user's home directory, preferring $HOME so Termux
// does not resolve to "/" via os.UserHomeDir().
func Home() (string, error) {
	if home := os.Getenv("HOME"); home != "" {
		return home, nil
	}
	return os.UserHomeDir()
}

// ConfigDir returns the per-app config directory.
// Linux/macOS/Termux: $XDG_CONFIG_HOME/<app> or ~/.config/<app>
// Windows:             %APPDATA%\<app>
func ConfigDir(app string) (string, error) {
	if runtime.GOOS == "windows" {
		if appdata := os.Getenv("APPDATA"); appdata != "" {
			return filepath.Join(appdata, app), nil
		}
	}
	if xdg := os.Getenv("XDG_CONFIG_HOME"); xdg != "" {
		return filepath.Join(xdg, app), nil
	}
	home, err := Home()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".config", app), nil
}

// CacheDir returns the per-app cache directory.
func CacheDir(app string) (string, error) {
	if runtime.GOOS == "windows" {
		if local := os.Getenv("LOCALAPPDATA"); local != "" {
			return filepath.Join(local, app), nil
		}
	}
	if xdg := os.Getenv("XDG_CACHE_HOME"); xdg != "" {
		return filepath.Join(xdg, app), nil
	}
	home, err := Home()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".cache", app), nil
}

// ExpandPath expands a leading tilde (~) to the user's home directory.
func ExpandPath(path string) string {
	if path == "~" {
		home, err := Home()
		if err == nil {
			return home
		}
	} else if strings.HasPrefix(path, "~/") || strings.HasPrefix(path, `~\`) {
		home, err := Home()
		if err == nil {
			return filepath.Join(home, path[2:])
		}
	}
	return path
}
