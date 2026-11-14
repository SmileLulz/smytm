package lyrics

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/SmileLulz/smytm/src/ytm"
)

const (
	lrclibAPI = "https://lrclib.net/api/get"
	userAgent = "smytm/1.0 (https://github.com/SmileLulz/smytm)"
)

// Track identifies a song for lyrics lookup.
type Track struct {
	VideoID  string
	Title    string
	Artist   string
	Album    string
	Duration int
}

// FetchLyrics implements the fallback chain:
// 1. YTM Synced
// 2. LRCLIB Synced
// 3. LRCLIB Plain
func FetchLyrics(ctx context.Context, ytmClient *ytm.Client, t Track) (string, bool, error) {
	// 1. Try YouTube Music first
	if t.VideoID != "" {
		if body, synced, err := ytmClient.GetLyrics(ctx, t.VideoID); err == nil && body != "" {
			return body, synced, nil
		}
	}

	// 2. Try LRCLIB
	if t.Title == "" || t.Artist == "" {
		return "", false, nil
	}

	q := url.Values{}
	q.Set("track_name", t.Title)
	q.Set("artist_name", t.Artist)
	if t.Album != "" {
		q.Set("album_name", t.Album)
	}
	if t.Duration > 0 {
		q.Set("duration", fmt.Sprintf("%d", t.Duration))
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, lrclibAPI+"?"+q.Encode(), nil)
	if err != nil {
		return "", false, err
	}
	req.Header.Set("User-Agent", userAgent)
	req.Header.Set("Accept", "application/json")

	hc := &http.Client{Timeout: 20 * time.Second}
	resp, err := hc.Do(req)
	if err != nil {
		return "", false, err
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return "", false, nil
	}
	if resp.StatusCode != http.StatusOK {
		return "", false, fmt.Errorf("lrclib: HTTP %d", resp.StatusCode)
	}

	var r struct {
		SyncedLyrics string `json:"syncedLyrics"`
		PlainLyrics  string `json:"plainLyrics"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&r); err != nil {
		return "", false, err
	}

	if s := strings.TrimSpace(r.SyncedLyrics); s != "" {
		return s + "\n", true, nil
	}
	if s := strings.TrimSpace(r.PlainLyrics); s != "" {
		return s + "\n", false, nil
	}
	return "", false, nil
}

// WriteLRC writes lyrics as a .lrc sidecar next to the audio file.
func WriteLRC(audioPath, body string) (string, error) {
	lrcPath := strings.TrimSuffix(audioPath, filepath.Ext(audioPath)) + ".lrc"
	tmp := lrcPath + ".tmp"
	if err := os.WriteFile(tmp, []byte(body), 0o644); err != nil {
		return "", err
	}
	if err := os.Rename(tmp, lrcPath); err != nil {
		os.Remove(tmp)
		return "", err
	}
	return lrcPath, nil
}
