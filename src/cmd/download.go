package cmd

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/SmileLulz/smytm/src/appdirs"
	"github.com/SmileLulz/smytm/src/config"
	"github.com/SmileLulz/smytm/src/cookies"
	"github.com/SmileLulz/smytm/src/dl"
	"github.com/SmileLulz/smytm/src/lyrics"
	"github.com/SmileLulz/smytm/src/replaygain"
	"github.com/SmileLulz/smytm/src/tag"
	"github.com/SmileLulz/smytm/src/ytm"
	"github.com/spf13/cobra"
)

func newDownloadCmd() *cobra.Command {
	var (
		format    string
		outputDir string
		doLyrics  bool
		doReplay  bool
		skipExist bool
	)
	cmd := &cobra.Command{
		Use:     "download <video-id | url | query>",
		Aliases: []string{"d"},
		Short:   "Download audio for one track",
		Args:    cobra.MinimumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, _, err := config.Load()
			if err != nil {
				return err
			}
			if format == "" {
				format = cfg.Format
			}
			if outputDir == "" {
				outputDir = cfg.OutputDir
			} else {
				outputDir = appdirs.ExpandPath(outputDir)
			}
			doLyrics = doLyrics || cfg.LyricsAlways
			doReplay = doReplay || cfg.ReplayGainAlways
			skipExist = skipExist || cfg.SkipAlways

			if err := os.MkdirAll(outputDir, 0o755); err != nil {
				return err
			}

			cookieBrowser, _ := cmd.Flags().GetString("cookies-browser")
			cookieProfile, _ := cmd.Flags().GetString("cookies-profile")
			if cookieBrowser == "" {
				cookieBrowser = cfg.CookiesBrowser
			}
			if cookieProfile == "" {
				cookieProfile = cfg.CookiesProfile
			}
			httpClient, err := cookies.NewClient(cookieBrowser, cookieProfile)
			if err != nil {
				return fmt.Errorf("cookie setup: %w", err)
			}
			if httpClient != nil {
				fmt.Println("Using browser cookies.")
			}

			ctx := cmd.Context()
			query := strings.Join(args, " ")

			videoID, err := resolveVideoInput(ctx, query, httpClient)
			if err != nil {
				return err
			}

			fmt.Printf("Downloading %s as %s ...\n", videoID, format)
			res, err := dl.Download(ctx, dl.Options{
				VideoID:       videoID,
				OutputDir:     outputDir,
				Format:        format,
				IncludeArtist: cfg.ArtistInFilename,
				SkipExisting:  skipExist,
				HTTPClient:    httpClient,
			})
			if err != nil {
				return err
			}
			if res.Skipped {
				fmt.Printf("Skipped (already exists): %s\n", res.Path)
				return nil
			}
			fmt.Printf("Saved: %s\n", res.Path)

			// Metadata + artwork. Prefer YTM album art (square) over kkdai's
			// YouTube thumbnail (16:9 video frame); fall back to kkdai's if
			// YTM has no entry for this video.
			thumbURL := res.Thumbnail
			ytmClient := ytm.New()
			if httpClient != nil {
				ytmClient.HTTP = httpClient
			}
			if ytURL, err := ytmClient.ThumbnailFor(ctx, videoID); err == nil && ytURL != "" {
				thumbURL = ytURL
			}
			var jpg []byte
			if thumbURL != "" {
				jpg, _ = fetchBytes(ctx, thumbURL, httpClient)
			}
			if err := tag.Write(res.Path, tag.Metadata{
				Title:        res.Title,
				Artist:       res.Artist,
				ThumbnailJPG: jpg,
			}); err != nil {
				fmt.Fprintf(os.Stderr, "warning: tag write failed: %v\n", err)
			}

			if doLyrics {
				body, synced, err := lyrics.FetchLyrics(ctx, ytmClient, lyrics.Track{
					VideoID: videoID,
					Title:   res.Title,
					Artist:  res.Artist,
				})
				switch {
				case err != nil:
					fmt.Fprintf(os.Stderr, "warning: lyrics lookup failed: %v\n", err)
				case body == "":
					fmt.Println("No lyrics found.")
				default:
					p, err := lyrics.WriteLRC(res.Path, body)
					if err != nil {
						fmt.Fprintf(os.Stderr, "warning: write lrc: %v\n", err)
					} else {
						kind := "plain"
						if synced {
							kind = "synced"
						}
						fmt.Printf("Lyrics (%s): %s\n", kind, p)
					}
				}
			}

			if doReplay {
				if !replaygain.Available() {
					fmt.Println("rsgain not installed; skipping ReplayGain.")
				} else if ok, err := replaygain.Apply(ctx, res.Path, format); err != nil {
					fmt.Fprintf(os.Stderr, "warning: replaygain: %v\n", err)
				} else if ok {
					fmt.Println("ReplayGain tags applied.")
				}
			}

			_ = filepath.Base // keep import when we add path formatting later
			return nil
		},
	}
	cmd.Flags().StringVarP(&format, "format", "f", "", "Audio format (default: from config)")
	cmd.Flags().StringVarP(&outputDir, "path", "p", "", "Output directory (default: from config)")
	cmd.Flags().BoolVar(&doLyrics, "lyrics", false, "Fetch synchronized lyrics as .lrc")
	cmd.Flags().BoolVar(&doReplay, "replaygain", false, "Apply ReplayGain 2.0 (needs rsgain)")
	cmd.Flags().BoolVarP(&skipExist, "skip", "s", false, "Skip download if file already exists")
	cmd.Flags().String("cookies-browser", "", "Browser to extract cookies from (overrides config)")
	cmd.Flags().String("cookies-profile", "", "Path to browser profile/cookie file (overrides config)")

	cmd.AddCommand(newPlaylistCmd())
	return cmd
}

func fetchBytes(ctx context.Context, u string, client *http.Client) ([]byte, error) {
	if client == nil {
		client = &http.Client{Timeout: 20 * time.Second}
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u, nil)
	if err != nil {
		return nil, err
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	return io.ReadAll(resp.Body)
}

// ensure strconv is used even if the tree later prunes duration handling
var _ = strconv.Itoa
var _ = strings.TrimSpace
