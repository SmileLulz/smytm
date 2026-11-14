package ytm

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
)

// GetLyrics fetches lyrics from YouTube Music.
// Returns (lyrics, isSynced, error).
func (c *Client) GetLyrics(ctx context.Context, videoID string) (string, bool, error) {
	payload := map[string]any{
		"videoId": videoID,
		"context": c.contextPayload(),
	}
	raw, err := c.post(ctx, "next", payload)
	if err != nil {
		return "", false, err
	}

	var root any
	if err := json.Unmarshal(raw, &root); err != nil {
		return "", false, err
	}

	// The "Lyrics" tab's browse ID sits inside a musicWatchNextTabbedResultsRenderer.
	// YTM localizes the tab title, so match on substring.
	var lyricsBrowseID string
	for _, tab := range findKey(root, "tabRenderer") {
		title := firstString(tab, "title")
		if strings.Contains(strings.ToLower(title), "lyrics") {
			if endpoint, ok := tab["endpoint"].(map[string]any); ok {
				if browse, ok := endpoint["browseEndpoint"].(map[string]any); ok {
					lyricsBrowseID, _ = browse["browseId"].(string)
					break
				}
			}
		}
	}

	if lyricsBrowseID == "" {
		return "", false, fmt.Errorf("no lyrics available for this track")
	}

	browsePayload := map[string]any{
		"browseId": lyricsBrowseID,
		"context":  c.contextPayload(),
	}
	rawBrowse, err := c.post(ctx, "browse", browsePayload)
	if err != nil {
		return "", false, err
	}

	var browseRoot any
	if err := json.Unmarshal(rawBrowse, &browseRoot); err != nil {
		return "", false, err
	}

	// Lyrics text lives in a musicDescriptionShelfRenderer (newer) or
	// musicLyricsRenderer (older), as a sequence of text runs.
	shelves := findKey(browseRoot, "musicDescriptionShelfRenderer")
	if len(shelves) == 0 {
		shelves = findKey(browseRoot, "musicLyricsRenderer")
	}
	if len(shelves) == 0 {
		return "", false, fmt.Errorf("could not parse lyrics from YTM response")
	}

	var sb strings.Builder
	for _, run := range findKey(shelves[0], "runs") {
		if text, ok := run["text"].(string); ok {
			sb.WriteString(text)
		}
	}

	lyrics := sb.String()
	if lyrics == "" {
		return "", false, fmt.Errorf("empty lyrics returned")
	}

	isSynced := strings.Contains(lyrics, "[00:")
	return lyrics, isSynced, nil
}
