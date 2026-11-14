package cmd

import (
	"fmt"
	"strings"

	"github.com/SmileLulz/smytm/src/config"
	"github.com/SmileLulz/smytm/src/cookies"
	"github.com/SmileLulz/smytm/src/dl"
	"github.com/spf13/cobra"
)

func newPlayCmd() *cobra.Command {
	var volume int

	cmd := &cobra.Command{
		Use:     "play <video-id | url | query>",
		Aliases: []string{"p"},
		Short:   "Stream audio directly without saving to disk",
		Args:    cobra.MinimumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, _, err := config.Load()
			if err != nil {
				return err
			}

			// Setup cookies if configured
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

			ctx := cmd.Context()
			query := strings.Join(args, " ")

			videoID, err := resolveVideoInput(ctx, query, httpClient)
			if err != nil {
				return err
			}

			return dl.Play(ctx, videoID, volume, httpClient)
		},
	}

	cmd.Flags().IntVarP(&volume, "volume", "v", 50, "Playback volume (0-100)")
	cmd.Flags().String("cookies-browser", "", "Browser to extract cookies from (overrides config)")
	cmd.Flags().String("cookies-profile", "", "Path to browser profile/cookie file (overrides config)")

	return cmd
}
