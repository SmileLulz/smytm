package tag

import (
	"fmt"
	"net/http"
	"strconv"

	"go.senan.xyz/taglib"
)

// Metadata carries everything we want written into the audio file's tags.
type Metadata struct {
	Title        string
	Artist       string
	Album        string
	Year         int
	TrackNumber  int
	ThumbnailJPG []byte
}

// Write sets tags and (optionally) embedded cover art on path.
// Supported by go-taglib: mp3, flac, m4a, ogg, wav.
func Write(path string, md Metadata) error {
	tags := map[string][]string{}

	if md.Title != "" {
		tags[taglib.Title] = []string{md.Title}
	}
	if md.Artist != "" {
		tags[taglib.Artist] = []string{md.Artist}
	}
	if md.Album != "" {
		tags[taglib.Album] = []string{md.Album}
	}
	if md.Year > 0 {
		tags[taglib.Date] = []string{strconv.Itoa(md.Year)}
	}
	if md.TrackNumber > 0 {
		tags[taglib.TrackNumber] = []string{strconv.Itoa(md.TrackNumber)}
	}

	// Tags must be written before artwork; reversing this drops text tags on m4a.
	if err := taglib.WriteTags(path, tags, 0); err != nil {
		return err
	}

	if len(md.ThumbnailJPG) > 0 {
		ct := http.DetectContentType(md.ThumbnailJPG)
		if ct != "image/jpeg" && ct != "image/png" {
			return fmt.Errorf("embed artwork: unsupported thumbnail type %q (expected jpeg/png)", ct)
		}
		if err := taglib.WriteImage(path, md.ThumbnailJPG); err != nil {
			return fmt.Errorf("embed artwork: %w", err)
		}
	}

	return nil
}
