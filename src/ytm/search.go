package ytm

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
)

// SearchResult is one song returned by the search endpoint.
type SearchResult struct {
	VideoID   string
	Title     string
	Artists   []string
	Duration  string
	Thumbnail string
}

// Search queries YouTube Music for songs matching query and returns up to limit items.
//
// The songs-only filter is the `params` value used by ytmusicapi; hard-coding it
// keeps the request tiny. Response shape is parsed by walking the JSON tree for
// "musicResponsiveListItemRenderer" nodes, which is stable against container
// renames that would break a fixed path.
func (c *Client) Search(ctx context.Context, query string, limit int) ([]SearchResult, error) {
	if limit <= 0 {
		limit = 3
	}
	payload := map[string]any{
		"query":   query,
		"context": c.contextPayload(),
		"params":  "EgWKAQIIAWoKEAkQBRAKEAMQBA==",
	}
	raw, err := c.post(ctx, "search", payload)
	if err != nil {
		return nil, err
	}
	return parseSearch(raw, limit)
}

func parseSearch(raw []byte, limit int) ([]SearchResult, error) {
	var root any
	if err := json.Unmarshal(raw, &root); err != nil {
		return nil, fmt.Errorf("parse search response: %w", err)
	}
	items := findKey(root, "musicResponsiveListItemRenderer")
	var out []SearchResult
	for _, item := range items {
		r := parseItem(item)
		if r.VideoID == "" || r.Title == "" {
			continue
		}
		out = append(out, r)
		if len(out) >= limit {
			break
		}
	}
	return out, nil
}

// findKey walks arbitrary JSON and returns every value stored under key.
func findKey(v any, key string) []map[string]any {
	var out []map[string]any
	switch t := v.(type) {
	case map[string]any:
		for k, child := range t {
			if k == key {
				if m, ok := child.(map[string]any); ok {
					out = append(out, m)
				}
			}
			out = append(out, findKey(child, key)...)
		}
	case []any:
		for _, child := range t {
			out = append(out, findKey(child, key)...)
		}
	}
	return out
}

// firstString walks a subtree and returns the first non-empty string stored under key.
func firstString(v any, key string) string {
	switch t := v.(type) {
	case map[string]any:
		if s, ok := t[key].(string); ok && s != "" {
			return s
		}
		for _, child := range t {
			if s := firstString(child, key); s != "" {
				return s
			}
		}
	case []any:
		for _, child := range t {
			if s := firstString(child, key); s != "" {
				return s
			}
		}
	}
	return ""
}

func parseItem(item map[string]any) SearchResult {
	r := SearchResult{
		VideoID: firstString(item, "videoId"),
	}

	// flexColumns[0] is the title line, flexColumns[1] is "Artist • Album • Duration".
	if flex, ok := item["flexColumns"].([]any); ok {
		if len(flex) > 0 {
			r.Title = flexText(flex[0])
		}
		if len(flex) > 1 {
			r.Artists = splitArtists(flexText(flex[1]))
		}
	}

	if thumb, ok := item["thumbnail"].(map[string]any); ok {
		if inner, ok := thumb["musicThumbnailRenderer"].(map[string]any); ok {
			if th, ok := inner["thumbnail"].(map[string]any); ok {
				if arr, ok := th["thumbnails"].([]any); ok && len(arr) > 0 {
					if last, ok := arr[len(arr)-1].(map[string]any); ok {
						r.Thumbnail, _ = last["url"].(string)
					}
				}
			}
		}
	}

	if dur := firstString(item, "text"); dur != "" && isDuration(dur) {
		r.Duration = dur
	}

	return r
}

func flexText(v any) string {
	m, ok := v.(map[string]any)
	if !ok {
		return ""
	}
	inner, ok := m["musicResponsiveListItemFlexColumnRenderer"].(map[string]any)
	if !ok {
		return ""
	}
	text, ok := inner["text"].(map[string]any)
	if !ok {
		return ""
	}
	runs, ok := text["runs"].([]any)
	if !ok || len(runs) == 0 {
		return ""
	}
	var sb strings.Builder
	for _, run := range runs {
		rm, ok := run.(map[string]any)
		if !ok {
			continue
		}
		if s, ok := rm["text"].(string); ok {
			sb.WriteString(s)
		}
	}
	return strings.TrimSpace(sb.String())
}

// splitArtists extracts artist names from an "Artist • Album • 3:42" line.
func splitArtists(s string) []string {
	parts := strings.Split(s, " • ")
	var artists []string
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p == "" || isDuration(p) {
			continue
		}
		if len(artists) < 2 {
			artists = append(artists, p)
		}
	}
	return artists
}

// isDuration reports whether s looks like "m:ss" or "h:mm:ss".
func isDuration(s string) bool {
	if len(s) < 4 {
		return false
	}
	colons := 0
	for _, r := range s {
		switch {
		case r == ':':
			colons++
		case r >= '0' && r <= '9':
		default:
			return false
		}
	}
	return colons >= 1
}
