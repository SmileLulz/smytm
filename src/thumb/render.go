package thumb

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/blacktop/go-termimg"
)

// RenderFromURL downloads a thumbnail and renders it sized to roughly
// size x size terminal cells, preserving aspect ratio.
func RenderFromURL(ctx context.Context, url string, size int) error {
	if size < 1 {
		size = 16
	}

	tmp, err := os.CreateTemp("", "smytm-thumb-*.img")
	if err != nil {
		return err
	}
	defer os.Remove(tmp.Name())
	defer tmp.Close()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return err
	}
	req.Header.Set("User-Agent", "smytm/1.0")
	resp, err := (&http.Client{Timeout: 20 * time.Second}).Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("thumbnail fetch: HTTP %d", resp.StatusCode)
	}
	if _, err := io.Copy(tmp, resp.Body); err != nil {
		return err
	}

	img, err := termimg.Open(tmp.Name())
	if err != nil {
		return err
	}

	if err := img.Width(size).Height(size / 2).Scale(termimg.ScaleFill).Print(); err != nil {
		return err
	}

	// Terminal image protocols don't advance the cursor past the image block.
	// Print a newline so the caller's text starts cleanly below the image.
	fmt.Println()
	return nil
}
