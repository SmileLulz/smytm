package dl

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/kkdai/youtube/v2"
)

// visionOSClient mirrors yt-dlp's visionOS InnerTube client.
// The library defaults to ANDROID_VR, whose stream URLs are range-gated
// (≈1 MiB chunks) and return 403 to the open-ended read that kkdai performs.
// VISIONOS URLs serve open-ended requests, so downloads succeed.
var visionOSClient = youtube.ClientInfo{
	Name:        "VISIONOS",
	Version:     "1.02",
	DeviceModel: "RealityDevice17,1",
	UserAgent:   "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
}

// Options describes a single download.
type Options struct {
	VideoID       string
	OutputDir     string
	Format        string
	IncludeArtist bool
	SkipExisting  bool
	HTTPClient    *http.Client
}

// Result carries everything downstream steps need.
type Result struct {
	Path      string
	Title     string
	Artist    string
	Thumbnail string
	Skipped   bool
}

// Download fetches the best audio stream and writes it under OutputDir.
func Download(ctx context.Context, opts Options) (*Result, error) {
	if opts.Format == "" {
		opts.Format = "m4a"
	}

	youtube.DefaultClient = visionOSClient

	client := youtube.Client{}
	if opts.HTTPClient != nil {
		client.HTTPClient = opts.HTTPClient
	}

	video, err := client.GetVideoContext(ctx, opts.VideoID)

	format := pickAudioFormat(video)
	if format == nil {
		return nil, fmt.Errorf("no audio-only stream found for %s", opts.VideoID)
	}

	// Prefer m4a if requested and available, so taglib can write without conversion.
	if m := pickFormatMatching(video, "audio/mp4"); m != nil && opts.Format == "m4a" {
		format = m
	}

	nativeExt := extForMime(format.MimeType)
	desiredExt := opts.Format

	title := video.Title
	artist := strings.TrimSuffix(strings.TrimSpace(video.Author), " - Topic")
	base := sanitize(title)
	if opts.IncludeArtist && artist != "" {
		base += " - " + sanitize(artist)
	}
	expected := filepath.Join(opts.OutputDir, base+"."+desiredExt)
	if opts.SkipExisting {
		if _, err := os.Stat(expected); err == nil {
			return &Result{
				Path: expected, Title: title, Artist: artist,
				Thumbnail: bestThumb(video), Skipped: true,
			}, nil
		}
	}
	outPath := incremented(expected)

	stream, _, err := client.GetStreamContext(ctx, video, format)
	if err != nil {
		return nil, fmt.Errorf("open stream: %w", err)
	}
	defer stream.Close()

	// Download to a temp file first when a conversion is needed.
	tmpPath := outPath
	if nativeExt != desiredExt {
		tmpPath = outPath + ".part"
	}

	f, err := os.Create(tmpPath)
	if err != nil {
		return nil, err
	}
	if _, err := io.Copy(f, stream); err != nil {
		f.Close()
		os.Remove(tmpPath)
		return nil, err
	}
	if err := f.Close(); err != nil {
		return nil, err
	}

	if nativeExt != desiredExt {
		if err := convertViaFFmpeg(ctx, tmpPath, outPath, nativeExt, desiredExt); err != nil {
			os.Remove(tmpPath)
			return nil, err
		}
		os.Remove(tmpPath)
	}

	return &Result{
		Path:      outPath,
		Title:     title,
		Artist:    artist,
		Thumbnail: bestThumb(video),
	}, nil
}

func pickAudioFormat(v *youtube.Video) *youtube.Format {
	var best *youtube.Format
	for i := range v.Formats {
		f := &v.Formats[i]
		if !strings.HasPrefix(f.MimeType, "audio/") {
			continue
		}
		if best == nil || f.Bitrate > best.Bitrate {
			best = f
		}
	}
	return best
}

func pickFormatMatching(v *youtube.Video, mimePrefix string) *youtube.Format {
	for i := range v.Formats {
		f := &v.Formats[i]
		if strings.HasPrefix(f.MimeType, mimePrefix) {
			return f
		}
	}
	return nil
}

func extForMime(mime string) string {
	switch {
	case strings.HasPrefix(mime, "audio/mp4"):
		return "m4a"
	case strings.HasPrefix(mime, "audio/webm"):
		return "webm"
	default:
		return "audio"
	}
}

func bestThumb(v *youtube.Video) string {
	if len(v.Thumbnails) == 0 {
		return ""
	}
	return v.Thumbnails[len(v.Thumbnails)-1].URL
}

func sanitize(s string) string {
	r := strings.NewReplacer(
		"\\", "_", "/", "_", "*", "_", "?", "_", ":", "_",
		"\"", "_", "<", "_", ">", "_", "|", "_",
	)
	return strings.TrimSpace(r.Replace(s))
}

func incremented(path string) string {
	if _, err := os.Stat(path); err != nil {
		return path
	}
	ext := filepath.Ext(path)
	stem := strings.TrimSuffix(path, ext)
	for i := 1; ; i++ {
		cand := fmt.Sprintf("%s (%d)%s", stem, i, ext)
		if _, err := os.Stat(cand); err != nil {
			return cand
		}
	}
}

// IsValidVideoID checks if a video ID actually exists on YouTube.
// Uses the VisionOS client so it respects any provided cookies.
func IsValidVideoID(ctx context.Context, videoID string, httpClient *http.Client) bool {
	youtube.DefaultClient = visionOSClient
	client := youtube.Client{}
	if httpClient != nil {
		client.HTTPClient = httpClient
	}
	_, err := client.GetVideoContext(ctx, videoID)
	return err == nil
}
