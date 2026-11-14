package ytm

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const (
	baseURL       = "https://music.youtube.com/youtubei/v1/"
	apiKey        = "AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30"
	clientName    = "WEB_REMIX"
	clientVersion = "1.20240101.00.00"
)

type Client struct {
	HTTP     *http.Client
	APIKey   string
	Language string
	Region   string
}

func New() *Client {
	return &Client{
		HTTP:     &http.Client{Timeout: 30 * time.Second},
		APIKey:   apiKey,
		Language: "en",
		Region:   "US",
	}
}

func (c *Client) post(ctx context.Context, endpoint string, payload map[string]any) ([]byte, error) {
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	url := baseURL + endpoint + "?prettyPrint=false&key=" + c.APIKey
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Origin", "https://music.youtube.com")
	req.Header.Set("Referer", "https://music.youtube.com/")
	req.Header.Set("X-YouTube-Client-Name", "67")
	req.Header.Set("X-YouTube-Client-Version", clientVersion)

	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 4096))
		return nil, fmt.Errorf("ytmusic %s: HTTP %d: %s", endpoint, resp.StatusCode, string(b))
	}
	return io.ReadAll(resp.Body)
}

func (c *Client) contextPayload() map[string]any {
	return map[string]any{
		"client": map[string]any{
			"clientName":    clientName,
			"clientVersion": clientVersion,
			"hl":            c.Language,
			"gl":            c.Region,
		},
	}
}
