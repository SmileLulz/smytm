package cmd

import (
	"fmt"
	"os"
	"path/filepath"

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

func newPlaylistCmd() *cobra.Command {
	var (
		format    string
		outputDir string
		doLyrics  bool
		doReplay  bool
		skipExist bool
	)
	cmd := &cobra.Command{
		Use:     "playlist <id-or-url>",
		Aliases: []string{"pl"},
		Short:   "Download an entire playlist",
		Args:    cobra.ExactArgs(1),
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
			client := ytm.New()
			if httpClient != nil {
				client.HTTP = httpClient
			}

			fmt.Printf("Fetching playlist: %s\n", args[0])
			items, err := client.GetPlaylist(ctx, args[0])
			if err != nil {
				return fmt.Errorf("fetch playlist: %w", err)
			}
			if len(items) == 0 {
				return fmt.Errorf("no tracks found in playlist")
			}

			fmt.Printf("Found %d tracks. Starting download...\n\n", len(items))

			for i, item := range items {
				fmt.Printf("[%d/%d] %s\n", i+1, len(items), item.Title)

				res, err := dl.Download(ctx, dl.Options{
					VideoID:       item.VideoID,
					OutputDir:     outputDir,
					Format:        format,
					IncludeArtist: cfg.ArtistInFilename,
					SkipExisting:  skipExist,
					HTTPClient:    httpClient,
				})
				if err != nil {
					fmt.Fprintf(os.Stderr, "  error: %v\n\n", err)
					continue
				}
				if res.Skipped {
					fmt.Printf("  Skipped (exists)\n\n")
					continue
				}
				fmt.Printf("  Saved: %s\n", filepath.Base(res.Path))

				thumbURL := res.Thumbnail
				if ytURL, err := client.ThumbnailFor(ctx, item.VideoID); err == nil && ytURL != "" {
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
					fmt.Fprintf(os.Stderr, "  warning: tag write failed: %v\n", err)
				}

				if doLyrics {
					body, synced, err := lyrics.FetchLyrics(ctx, client, lyrics.Track{
						VideoID: item.VideoID,
						Title:   res.Title,
						Artist:  res.Artist,
					})
					if err == nil && body != "" {
						p, err := lyrics.WriteLRC(res.Path, body)
						if err == nil {
							kind := "plain"
							if synced {
								kind = "synced"
							}
							fmt.Printf("  Lyrics (%s): %s\n", kind, filepath.Base(p))
						}
					}
				}

				if doReplay {
					if !replaygain.Available() {
						// Print once per run, not per track.
						if i == 0 {
							fmt.Println("  rsgain not installed; skipping ReplayGain.")
						}
					} else if ok, err := replaygain.Apply(ctx, res.Path, format); err == nil && ok {
						fmt.Println("  ReplayGain tags applied.")
					}
				}
				fmt.Println()
			}

			fmt.Println("Playlist download complete.")
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
	return cmd
}
