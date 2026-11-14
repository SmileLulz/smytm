package ytm

import (
	"context"
	"encoding/json"
	"strings"
)

// PlaylistItem represents a single track in a playlist.
type PlaylistItem struct {
	VideoID string
	Title   string
}

// GetPlaylist fetches up to the first 100 tracks of a playlist.
// Pagination via continuations is not yet implemented.
func (c *Client) GetPlaylist(ctx context.Context, playlistID string) ([]PlaylistItem, error) {
	if strings.Contains(playlistID, "list=") {
		parts := strings.Split(playlistID, "list=")
		if len(parts) > 1 {
			playlistID = strings.Split(parts[1], "&")[0]
		}
	}

	// YTM expects the "VL" prefix for playlist browse requests.
	browseID := playlistID
	if !strings.HasPrefix(browseID, "VL") {
		browseID = "VL" + browseID
	}

	payload := map[string]any{
		"browseId": browseID,
		"context":  c.contextPayload(),
	}

	raw, err := c.post(ctx, "browse", payload)
	if err != nil {
		return nil, err
	}

	var root any
	if err := json.Unmarshal(raw, &root); err != nil {
		return nil, err
	}

	// YTM playlists use musicResponsiveListItemRenderer; standard YouTube
	// playlists use playlistVideoRenderer. Try both.
	var items []PlaylistItem
	for _, r := range findKey(root, "musicResponsiveListItemRenderer") {
		vid := firstString(r, "videoId")
		if vid == "" {
			continue
		}
		title := ""
		if flex, ok := r["flexColumns"].([]any); ok && len(flex) > 0 {
			title = flexText(flex[0])
		}
		items = append(items, PlaylistItem{VideoID: vid, Title: title})
	}

	if len(items) == 0 {
		for _, r := range findKey(root, "playlistVideoRenderer") {
			vid := firstString(r, "videoId")
			if vid == "" {
				continue
			}
			items = append(items, PlaylistItem{VideoID: vid, Title: firstString(r, "title")})
		}
	}

	return items, nil
}
