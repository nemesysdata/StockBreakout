package main

import (
	"baixar_stock/finazon"
	"encoding/csv"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/gocarina/gocsv"
	"github.com/joho/godotenv"
)

type Stock struct {
	Ticker    string  `csv:"ticker" json:"ticker"`
	Timestamp string  `csv:"timestamp" json:"timestamp"`
	Open      float32 `csv:"open" json:"open"`
	High      float32 `csv:"high" json:"high"`
	Low       float32 `csv:"low" json:"low"`
	Close     float32 `csv:"close" json:"close"`
	Volume    int32   `csv:"volume" json:"volume"`
}

func readCSV(file string) ([]Stock, error) {
	// Open the file
	csvFile, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	defer csvFile.Close()

	stocks := []Stock{}
	if err := gocsv.UnmarshalFile(csvFile, &stocks); err != nil {
		return nil, err
	}

	return stocks, nil
}

func main() {
	var fin *finazon.Finazon

	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	today := time.Now().Format("2006-01-02")

	startDateP := flag.String("start", "2023-08-01", "Start date")
	endDateP := flag.String("end", today, "Start date")
	tickerListP := flag.String("tickers", "AAPL,AMZN,META,MSFT,TSLA", "Comma separated list of tickers")
	flag.Parse()

	startDate, err := time.Parse("2006-01-02", *startDateP)
	if err != nil {
		log.Fatal(err)
	}

	endDate, err := time.Parse("2006-01-02", *endDateP)
	if err != nil {
		log.Fatal(err)
	}

	tickerList := strings.Split(*tickerListP, ",")

	fin = finazon.NewFinazon(os.Getenv("FINAZON_API_KEY"))

	for _, ticker := range tickerList {
		fmt.Printf("Processing %s\n", ticker)

		stocks, err := readCSV(fmt.Sprintf("../dados/complementar/%s_1min_firstratedata.csv", ticker))
		if err != nil {
			log.Fatal(err)
		}

		fmt.Println(len(stocks))

		file, err := os.Create(fmt.Sprintf("../dados/%s.csv", ticker))
		if err != nil {
			panic(err)
		}
		defer file.Close()

		writer := csv.NewWriter(file)
		defer writer.Flush()

		writer.Write([]string{"ticker", "timestamp", "open", "high", "low", "close", "volume"})
		writer.Flush()

		start := startDate

		for _, stock := range stocks {
			err = writer.Write([]string{
				ticker,
				stock.Timestamp,
				fmt.Sprintf("%f", stock.Open),
				fmt.Sprintf("%f", stock.High),
				fmt.Sprintf("%f", stock.Low),
				fmt.Sprintf("%f", stock.Close),
				fmt.Sprintf("%d", stock.Volume),
			})

			if err != nil {
				panic(err)
			}
			start, err = time.Parse("2006-01-02", stock.Timestamp[:10])
			if err != nil {
				panic(err)
			}
		}

		start = start.AddDate(0, 0, 1)

		for start.Before(endDate) {
			fmt.Printf("  Downloading %s...", start.Format("02-01-2006 15:04:05"))
			if start.Weekday() == time.Saturday || start.Weekday() == time.Sunday {
				fmt.Printf("%s SKIP\n", start.Weekday())
				start = start.AddDate(0, 0, 1)
				continue
			}

			stocks, err := fin.DownloadAllDay(ticker, start)
			if err != nil {
				fmt.Printf("ERROR: %s\n", err)
				return
			}

			// time.Sleep(2 * time.Second)
			for _, stock := range stocks {
				writer.Write([]string{
					stock.Ticker,
					stock.Timestamp.Format("2006-01-02 15:04:05"),
					fmt.Sprintf("%f", stock.Open),
					fmt.Sprintf("%f", stock.High),
					fmt.Sprintf("%f", stock.Low),
					fmt.Sprintf("%f", stock.Close),
					fmt.Sprintf("%d", stock.Volume),
				})
			}

			fmt.Printf("%d OK\n", len(stocks))
			start = start.AddDate(0, 0, 1)
		}

		writer.Flush()
		file.Close()
		// break
	}
}
