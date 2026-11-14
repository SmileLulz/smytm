package dl

import (
	"context"
	"fmt"
	"os/exec"
)

// convertViaFFmpeg converts or remuxes src to dst.
// It compares nativeExt and targetExt to decide whether a direct stream
// copy is possible or a re-encode is required.
func convertViaFFmpeg(ctx context.Context, src, dst, nativeExt, targetExt string) error {
	bin, err := exec.LookPath("ffmpeg")
	if err != nil {
		return fmt.Errorf("cannot convert %s → %s: ffmpeg not found in PATH "+
			"(needed for non-native formats; m4a needs no ffmpeg)", src, dst)
	}

	args := []string{"-y", "-i", src, "-vn"}

	switch targetExt {
	case "opus":
		if nativeExt == "webm" {
			// Opus-in-WebM → Ogg Opus: container swap only.
			args = append(args, "-c:a", "copy")
		} else {
			// Source is AAC; must transcode to Opus.
			args = append(args, "-c:a", "libopus", "-b:a", "128k")
		}
	case "m4a":
		if nativeExt == "m4a" {
			args = append(args, "-c:a", "copy")
		} else {
			// Source is Opus; must transcode to AAC.
			args = append(args, "-c:a", "aac", "-b:a", "192k")
		}
	case "mp3":
		// No YouTube source container is MP3-compatible; always transcode.
		args = append(args, "-c:a", "libmp3lame", "-q:a", "0")
	case "flac":
		args = append(args, "-c:a", "flac")
	case "ogg":
		args = append(args, "-c:a", "libvorbis", "-q:a", "6")
	case "wav":
		args = append(args, "-c:a", "pcm_s16le")
	default:
		args = append(args, "-c:a", "copy")
	}

	args = append(args, dst)
	cmd := exec.CommandContext(ctx, bin, args...)
	if out, err := cmd.CombinedOutput(); err != nil {
		return fmt.Errorf("ffmpeg convert failed: %w\n%s", err, string(out))
	}
	return nil
}
