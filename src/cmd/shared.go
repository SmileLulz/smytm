package cmd

import (
	"context"
	"fmt"
	"net/http"
	"regexp"
	"strings"

	"github.com/SmileLulz/smytm/src/dl"
	"github.com/SmileLulz/smytm/src/ytm"
)

var (
	idRegex  = regexp.MustCompile(`^[A-Za-z0-9_-]{11}$`)
	urlRegex = regexp.MustCompile(`(?:v=|/)([A-Za-z0-9_-]{11})`)
)

// resolveVideoInput determines whether input is a video ID, URL, or search query.
// For ID-shaped strings, it verifies against YouTube before treating them as IDs,
// so song names that happen to be 11 chars (e.g. "GangnamStyle") still fall back
// to search if the video doesn't exist.
func resolveVideoInput(ctx context.Context, input string, httpClient *http.Client) (string, error) {
	if strings.Contains(input, "youtube.com/watch") || strings.Contains(input, "youtu.be/") {
		matches := urlRegex.FindStringSubmatch(input)
		if len(matches) > 1 {
			return matches[1], nil
		}
	}

	if len(input) == 11 && idRegex.MatchString(input) {
		if dl.IsValidVideoID(ctx, input, httpClient) {
			return input, nil
		}
	}

	fmt.Printf("Searching: %s\n", input)
	ytmClient := ytm.New()
	if httpClient != nil {
		ytmClient.HTTP = httpClient
	}
	results, err := ytmClient.Search(ctx, input, 1)
	if err != nil {
		return "", fmt.Errorf("search failed: %w", err)
	}
	if len(results) == 0 {
		return "", fmt.Errorf("no results found for: %s", input)
	}

	fmt.Printf("Found: %s\n", results[0].Title)
	return results[0].VideoID, nil
}
