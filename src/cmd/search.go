package cmd

import (
	"fmt"
	"strings"

	"github.com/SmileLulz/smytm/src/config"
	"github.com/SmileLulz/smytm/src/thumb"
	"github.com/SmileLulz/smytm/src/ytm"
	"github.com/spf13/cobra"
)

func newSearchCmd() *cobra.Command {
	var (
		count     int
		thumbSize int
	)
	cmd := &cobra.Command{
		Use:     "search <query...>",
		Aliases: []string{"s"},
		Short:   "Search YouTube Music and print squared thumbnails + video IDs",
		Args:    cobra.MinimumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, _, err := config.Load()
			if err != nil {
				return err
			}
			size := thumbSize
			if size <= 0 {
				size = cfg.ThumbnailSize
			}

			query := strings.Join(args, " ")
			client := ytm.New()
			results, err := client.Search(cmd.Context(), query, count)
			if err != nil {
				return err
			}
			if len(results) == 0 {
				fmt.Println("No songs found.")
				return nil
			}

			for i, r := range results {
				if i > 0 {
					fmt.Println()
				}
				fmt.Println()
				if r.Thumbnail != "" {
					if err := thumb.RenderFromURL(cmd.Context(), r.Thumbnail, size); err != nil {
						fmt.Printf("[Thumbnail unavailable: %v]\n", err)
					}
				} else {
					fmt.Println("[Thumbnail unavailable]")
				}
				fmt.Println()
				fmt.Printf("Title  : %s\n", r.Title)
				fmt.Printf("Artist : %s\n", strings.Join(r.Artists, ", "))
				fmt.Printf("ID     : %s\n", r.VideoID)
				if r.Duration != "" {
					fmt.Printf("Length : %s\n", r.Duration)
				}
			}
			return nil
		},
	}
	cmd.Flags().IntVarP(&count, "count", "c", 3, "Number of results to show")
	cmd.Flags().IntVar(&thumbSize, "tsize", 0, "Thumbnail size in terminal cells (0 = from config)")
	return cmd
}
