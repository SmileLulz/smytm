package replaygain

import (
	"context"
	"fmt"
	"os"
	"os/exec"
)

// Available reports whether rsgain is on PATH.
func Available() bool {
	_, err := exec.LookPath("rsgain")
	return err == nil
}

// Apply runs rsgain's custom preset against path.
// format == "opus" selects the RS tags that Opus players expect.
//
// Returns (applied bool, err error). If rsgain is not installed, applied is
// false and err is nil — this is the "optional tool missing" path.
func Apply(ctx context.Context, path, format string) (bool, error) {
	bin, err := exec.LookPath("rsgain")
	if err != nil {
		return false, nil
	}
	args := []string{"custom", "-s", "i"}
	if format == "opus" {
		args = append(args, "-o", "r")
	}
	args = append(args, path)

	cmd := exec.CommandContext(ctx, bin, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return false, fmt.Errorf("rsgain: %w", err)
	}
	return true, nil
}
