package finazon

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

const PAGE_SIZE = 500

type Finazon struct {
	Key string
}

type Stock struct {
	ID          primitive.ObjectID `bson:"_id,omitempty"`
	Ticker      string             `json:"ticker"`
	Description string             `json:"description,omitempty"`
	Timestamp   time.Time          `json:"timestamp"`
	Open        float32            `json:"open"`
	High        float32            `json:"high"`
	Low         float32            `json:"low"`
	Close       float32            `json:"close"`
	Volume      int32              `json:"volume"`
}

type StockItem struct {
	Timestamp int64   `json:"t"`
	Open      float32 `json:"o"`
	High      float32 `json:"h"`
	Low       float32 `json:"l"`
	Close     float32 `json:"c"`
	Volume    int32   `json:"v"`
}

type FinazonResponse struct {
	Status int `json:"status,omitempty"`
}

type StockResponse struct {
	Data []StockItem `json:"data"`
}

type TickerResponse struct {
	Data []Ticker `json:"data"`
}

type Ticker struct {
	Ticker         string `json:"ticker"`
	Currency       string `json:"currency"`
	Security       string `json:"security"`
	Mic            string `json:"mic"`
	Asset_type     string `json:"asset_type"`
	Cik            string `json:"cik"`
	Composite_figi string `json:"composite_figi"`
	Share_figi     string `json:"share_figi"`
	Lei            string `json:"lei"`
}

type DownloadStocksOptions struct {
	StartAt int64
	EndAt   int64
	Page    int
}

const URL = "https://api.finazon.io/latest/"

func NewFinazon(key string) *Finazon {
	return &Finazon{Key: key}
}

func (f *Finazon) sendGet(path string) ([]byte, error) {
	for rep := 0; rep < 6; rep++ {
		url := fmt.Sprintf("%s/%s", URL, path)
		req, _ := http.NewRequest("GET", url, nil)
		req.Header.Add("Authorization", fmt.Sprintf("apikey %s", f.Key))
		res, err := http.DefaultClient.Do(req)

		if err != nil {
			return nil, err
		}

		defer res.Body.Close()
		body, err := io.ReadAll(res.Body)
		if err != nil {
			return nil, err
		}

		var response FinazonResponse
		err = json.Unmarshal(body, &response)
		if err != nil {
			return nil, err
		}

		if response.Status == 200 || response.Status == 0 {
			return body, nil
		}

		if response.Status == 429 {
			// log.Println("Rate limit exceeded. Waiting 60 seconds")
			time.Sleep(15 * time.Second)
			continue
		}

		return nil, fmt.Errorf("failed to get data from Finazon (code: %d)", response.Status)
	}

	return nil, fmt.Errorf("failed to get data from Finazon")
}

func (f *Finazon) GetTicker(ticker string) (*Ticker, error) {
	body, err := f.sendGet(fmt.Sprintf("tickers/us_stocks?ticker=%s", ticker))
	if err != nil {
		return nil, err
	}

	var tick TickerResponse
	err = json.Unmarshal(body, &tick)
	if err != nil {
		return nil, err
	}

	return &tick.Data[0], nil
}

// DownloadStocks downloads stocks from Finazon of a single page between the interval of startAt and endAt
func (f *Finazon) DownloadStocks(ticker string, options *DownloadStocksOptions) ([]Stock, error) {
	var stocks = make([]Stock, 0)

	uri := fmt.Sprintf("time_series?dataset=us_stocks_essential&ticker=%s&interval=1m&page_size=%d&order=asc", ticker, PAGE_SIZE)
	if options != nil && options.StartAt != 0 {
		uri += fmt.Sprintf("&start_at=%d", options.StartAt)
	}

	if options != nil && options.EndAt != 0 {
		uri += fmt.Sprintf("&end_at=%d", options.EndAt)
	}

	if options != nil {
		uri += fmt.Sprintf("&page=%d", options.Page)
	}

	body, err := f.sendGet(uri)
	if err != nil {
		return nil, err
	}

	var response StockResponse
	response.Data = make([]StockItem, 0)

	err = json.Unmarshal(body, &response)
	if err != nil {
		return nil, err
	}

	for _, item := range response.Data {
		stock := Stock{
			Ticker:    ticker,
			Timestamp: time.Unix(item.Timestamp, 0),
			Open:      item.Open,
			High:      item.High,
			Low:       item.Low,
			Close:     item.Close,
			Volume:    item.Volume,
		}
		stocks = append(stocks, stock)
	}

	return stocks, nil
}

// Download all of a day starting at 11:30 AM -0300 and finishing at 20:30 PM -0300 to a given ticker
func (f *Finazon) DownloadAllDay(ticker string, day time.Time) ([]Stock, error) {
	var stocks = make([]Stock, 0)
	startAt := time.Date(day.Year(), day.Month(), day.Day(), 0, 0, 0, 0, time.FixedZone("UTC", 0))
	endAt := time.Date(day.Year(), day.Month(), day.Day(), 23, 59, 590, 999, time.FixedZone("UTC", 0))

	// fmt.Printf("Baixando %s - %s\n", ticker, startAt)

	page := 0
	for {
		// fmt.Println("Downloading page ", page)

		options := &DownloadStocksOptions{
			StartAt: startAt.Unix(),
			EndAt:   endAt.Unix(),
			Page:    page,
		}

		stock, err := f.DownloadStocks(ticker, options)
		if err != nil {
			return nil, err
		}

		if len(stock) == 0 {
			break
		}

		stocks = append(stocks, stock...)
		startAt = startAt.Add(1 * time.Hour)

		if len(stock) < PAGE_SIZE {
			break
		}

		page++
	}

	return stocks, nil
}
