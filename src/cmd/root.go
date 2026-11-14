package cmd

import (
	"fmt"
	"os"
	"strings"

	"github.com/SmileLulz/smytm/src/config"
	"github.com/spf13/cobra"
)

var Version = "dev"

var rootCmd = &cobra.Command{
	Use:   "smytm",
	Short: "Search and download music from YouTube / YouTube Music",
	Long: `smytm searches YouTube Music, downloads audio with embedded metadata
and artwork, and can fetch synchronized lyrics as .lrc sidecars.

Run 'smytm <command> --help' for details on a specific command.`,
	SilenceUsage:  true,
	SilenceErrors: true,
	PersistentPreRun: func(cmd *cobra.Command, args []string) {
		if _, err := config.Ensure(); err != nil {
			fmt.Fprintf(os.Stderr, "warning: could not prepare config file: %v\n", err)
		}
	},
}

func init() {
	rootCmd.AddCommand(
		newSearchCmd(),
		newDownloadCmd(),
		newPlayCmd(),
		newVersionCmd(),
	)
}

func Execute() error {
	args := os.Args[1:]
	args = normalizeLeadingHyphenID(args)
	rootCmd.SetArgs(args)

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return err
	}
	return nil
}

// normalizeLeadingHyphenID injects "--" before an unknown flag that looks
// like a hyphenated video ID (e.g. -tR8sX7C1eI), so pflag doesn't try to
// parse it as a flag. Applies only to download/play and their aliases.
func normalizeLeadingHyphenID(args []string) []string {
	if len(args) == 0 {
		return args
	}

	isTargetCmd := false
	for _, arg := range args {
		if arg == "download" || arg == "d" || arg == "play" || arg == "p" {
			isTargetCmd = true
			break
		}
		if arg == "search" || arg == "s" || arg == "version" {
			break
		}
	}

	if !isTargetCmd {
		return args
	}

	valueOptions := map[string]bool{
		"-f": true, "--format": true,
		"-p": true, "--path": true,
		"-v": true, "--volume": true,
		"--cookies-browser": true, "--cookies-profile": true,
	}

	flagOptions := map[string]bool{
		"--lyrics": true, "--replaygain": true,
		"-s": true, "--skip": true,
		"-h": true, "--help": true,
	}

	for i := 0; i < len(args); i++ {
		token := args[i]
		if token == "--" {
			return args
		}

		if strings.HasPrefix(token, "-") {
			if valueOptions[token] {
				i++
				continue
			}
			if strings.HasPrefix(token, "--format=") ||
				strings.HasPrefix(token, "--path=") ||
				strings.HasPrefix(token, "--volume=") ||
				strings.HasPrefix(token, "--cookies-browser=") ||
				strings.HasPrefix(token, "--cookies-profile=") {
				continue
			}
			if flagOptions[token] {
				continue
			}

			out := make([]string, 0, len(args)+1)
			out = append(out, args[:i]...)
			out = append(out, "--")
			out = append(out, args[i:]...)
			return out
		}
	}
	return args
}
