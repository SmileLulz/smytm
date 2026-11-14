// Package cookies extracts browser cookies and builds an HTTP client
// pre-configured with a cookie jar for YouTube requests.
package cookies

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/Code-Hex/browsercookie"
	"github.com/SmileLulz/smytm/src/appdirs"
)

// NewClient returns an *http.Client with cookies loaded from the specified
// browser. If browser is empty, it auto-discovers any installed browser.
// profilePath overrides the auto-discovered cookie store location.
//
// Returns nil and no error if browser is empty and no cookies are found,
// allowing the caller to fall back to an unauthenticated client.
func NewClient(browser, profilePath string) (*http.Client, error) {
	browser = strings.ToLower(strings.TrimSpace(browser))

	if profilePath != "" {
		profilePath = appdirs.ExpandPath(profilePath)
	}

	if browser == "" && profilePath == "" {
		return nil, nil
	}

	var (
		cookies []*http.Cookie
		err     error
	)

	domainOpt := browsercookie.WithDomains(
		"youtube.com",
		"music.youtube.com",
		"google.com",
		"googleapis.com",
	)

	fileOpt := func(opts []browsercookie.Option) []browsercookie.Option {
		if profilePath != "" {
			return append(opts, browsercookie.WithCookieFiles(profilePath))
		}
		return opts
	}

	switch browser {
	case "", "auto":
		cookies, err = browsercookie.Load(domainOpt)
	case "chrome":
		cookies, err = browsercookie.Chrome(fileOpt([]browsercookie.Option{domainOpt})...)
	case "firefox":
		cookies, err = browsercookie.Firefox(fileOpt([]browsercookie.Option{domainOpt})...)
	case "edge":
		cookies, err = browsercookie.Edge(fileOpt([]browsercookie.Option{domainOpt})...)
	case "brave":
		cookies, err = browsercookie.Brave(fileOpt([]browsercookie.Option{domainOpt})...)
	case "chromium":
		cookies, err = browsercookie.Chromium(fileOpt([]browsercookie.Option{domainOpt})...)
	case "opera":
		cookies, err = browsercookie.Opera(fileOpt([]browsercookie.Option{domainOpt})...)
	case "vivaldi":
		cookies, err = browsercookie.Vivaldi(fileOpt([]browsercookie.Option{domainOpt})...)
	case "safari":
		cookies, err = browsercookie.Safari(domainOpt)
	default:
		return nil, fmt.Errorf("unsupported browser %q (use chrome, firefox, edge, brave, chromium, opera, vivaldi, safari, or auto)", browser)
	}

	if err != nil {
		return nil, fmt.Errorf("read cookies from %s: %w", browser, err)
	}

	if len(cookies) == 0 {
		return nil, fmt.Errorf("no YouTube cookies found in %s", browser)
	}

	jar, err := browsercookie.Jar(cookies)
	if err != nil {
		return nil, fmt.Errorf("build cookie jar: %w", err)
	}

	return &http.Client{Jar: jar}, nil
}
