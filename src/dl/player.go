package dl

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strings"

	"github.com/kkdai/youtube/v2"
)

// Play streams the audio for a video ID directly to the speakers via ffplay.
// It does not write any files to disk.
func Play(ctx context.Context, videoID string, volume int, httpClient *http.Client) error {
	ffplay, err := exec.LookPath("ffplay")
	if err != nil {
		return fmt.Errorf("ffplay not found in PATH (it is bundled with ffmpeg)")
	}

	youtube.DefaultClient = visionOSClient
	client := youtube.Client{}
	if httpClient != nil {
		client.HTTPClient = httpClient
	}

	video, err := client.GetVideoContext(ctx, videoID)
	if err != nil {
		return fmt.Errorf("fetch video info: %w", err)
	}

	format := pickAudioFormat(video)
	if format == nil {
		return fmt.Errorf("no audio-only stream found for %s", videoID)
	}

	stream, _, err := client.GetStreamContext(ctx, video, format)
	if err != nil {
		return fmt.Errorf("open stream: %w", err)
	}
	defer stream.Close()

	args := []string{
		"-hide_banner",
		"-loglevel", "error",
		"-nodisp",
		"-autoexit",
		"-volume", fmt.Sprintf("%d", volume),
		"-i", "-",
	}
	cmd := exec.CommandContext(ctx, ffplay, args...)
	cmd.Stdin = stream
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	fmt.Printf("▶ Playing : %s\n", video.Title)
	fmt.Printf("  Artist  : %s\n", strings.TrimSuffix(video.Author, " - Topic"))
	fmt.Printf("  Volume  : %d%%\n", volume)
	fmt.Println("  (Press Ctrl+C to stop)")

	if err := cmd.Run(); err != nil {
		// Ctrl+C cancels ctx, killing ffplay; that's a clean stop, not an error.
		if ctx.Err() != nil {
			fmt.Println("\nPlayback stopped.")
			return nil
		}
		return fmt.Errorf("playback failed: %w", err)
	}

	return nil
}
