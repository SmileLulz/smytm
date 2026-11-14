package ytm

import (
	"context"
	"encoding/json"
)

// ThumbnailFor returns the largest album-art thumbnail URL for a video ID,
// as served by YouTube Music. Unlike YouTube's i.ytimg.com thumbnails
// (16:9 video frames), YTM returns square album art from
// lh3.googleusercontent.com for tracks that are in the music catalog.
//
// Returns "" with no error if YTM has no thumbnail for the video.
func (c *Client) ThumbnailFor(ctx context.Context, videoID string) (string, error) {
	payload := map[string]any{
		"videoId":        videoID,
		"context":        c.contextPayload(),
		"racyCheckOk":    true,
		"contentCheckOk": true,
	}
	raw, err := c.post(ctx, "player", payload)
	if err != nil {
		return "", err
	}

	var resp struct {
		VideoDetails struct {
			Thumbnail struct {
				Thumbnails []struct {
					URL    string `json:"url"`
					Width  int    `json:"width"`
					Height int    `json:"height"`
				} `json:"thumbnails"`
			} `json:"thumbnail"`
		} `json:"videoDetails"`
	}
	if err := json.Unmarshal(raw, &resp); err != nil {
		return "", err
	}

	th := resp.VideoDetails.Thumbnail.Thumbnails
	if len(th) == 0 {
		return "", nil
	}

	// Prefer the largest square entry (album art). If none are square,
	// fall back to the largest overall.
	var bestSquare, bestAny string
	var bestSquareArea, bestAnyArea int
	for _, t := range th {
		area := t.Width * t.Height
		if area > bestAnyArea {
			bestAny, bestAnyArea = t.URL, area
		}
		if t.Width == t.Height && area > bestSquareArea {
			bestSquare, bestSquareArea = t.URL, area
		}
	}
	if bestSquare != "" {
		return bestSquare, nil
	}
	return bestAny, nil
}
