package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/fs"
	"log"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/gocarina/gocsv"
	"github.com/segmentio/kafka-go"
	"golang.org/x/text/language"
	"golang.org/x/text/message"

	"github.com/jedib0t/go-pretty/v6/progress"
	"github.com/jedib0t/go-pretty/v6/text"
)

type Stock struct {
	Ticker      string  `csv:"ticker" json:"ticker"`
	Description string  `csv:"description" json:"description,omitempty"`
	Timestamp   string  `csv:"timestamp" json:"datetime"`
	Open        float32 `csv:"open" json:"openv"`
	High        float32 `csv:"high" json:"highv"`
	Low         float32 `csv:"low" json:"lowv"`
	Close       float32 `csv:"close" json:"closev"`
	Volume      int32   `csv:"volume" json:"volume"`
}

type StockData struct {
	FileName string
	Stocks   []Stock
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

func Send2Kafka(pw progress.Writer, name string, stocks []Stock, kafkaReady chan bool, readySend chan bool) {
	tokens := strings.Split(name, ".")
	topic := tokens[0]

	tracker := progress.Tracker{Message: fmt.Sprintf("%s - %d", name, len(stocks)), Total: int64(len(stocks)), Units: progress.UnitsDefault, DeferStart: true}
	pw.AppendTracker(&tracker)
	fmt.Printf("%s waitting kafka\n", name)
	// Connect to Kafka
	conn, err := kafka.DialLeader(context.Background(), "tcp", "192.168.81.102:9092", topic, 0)
	if err != nil {
		log.Fatal("failed to dial leader:", err)
	}

	kafkaReady <- true

	<-readySend

	// fmt.Printf("%s sending %d stocks to Kafka\n", name, len(stocks))
	for _, stock := range stocks {
		msg, err := json.Marshal(stock)
		if err != nil {
			panic("failed to marshal message")
		}

		_, err = conn.WriteMessages(kafka.Message{Value: msg})
		if err != nil {
			panic("failed to write messages")
		}
		tracker.Increment(1)
		// time.Sleep(3 * time.Millisecond)
	}

	tracker.MarkAsDone()
}

func main() {
	text.EnableColors()
	stockFiles := make([]fs.DirEntry, 0)
	fmt.Println("Loading Stocks Data")

	path := "../dados" // replace with your directory

	files, err := os.ReadDir(path)
	if err != nil {
		fmt.Println(err)
		return
	}

	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".csv") {
			stockFiles = append(stockFiles, file)
		}
	}

	fmt.Println("Files found: ", len(stockFiles))
	fmt.Println("Reading files")

	p := message.NewPrinter(language.BrazilianPortuguese)

	stockData := make([]StockData, 0)
	for _, stockFile := range stockFiles {
		fmt.Printf("  %s... ", stockFile.Name())
		stocks, err := readCSV(path + "/" + stockFile.Name())
		if err != nil {
			fmt.Println(err)
			return
		}
		p.Printf("%d linhas carregadas\n", len(stocks))
		stockData = append(stockData, StockData{stockFile.Name(), stocks})
	}

	fmt.Println("Sending to Kafka")

	var wg sync.WaitGroup
	kafkaReady := make(chan bool, len(stockData))
	readySend := make(chan bool, len(stockData))
	//
	// Prepare progress bar
	//
	pw := progress.NewWriter()
	pw.SetAutoStop(true)
	pw.SetMessageLength(24)
	pw.SetNumTrackersExpected(len(stockData))
	pw.SetSortBy(progress.SortByPercentDsc)
	pw.SetStyle(progress.StyleDefault)
	pw.SetTrackerLength(25)
	pw.SetTrackerPosition(progress.PositionRight)
	pw.SetUpdateFrequency(time.Millisecond * 100)
	pw.Style().Colors = progress.StyleColorsExample
	pw.Style().Options.PercentFormat = "%4.1f%%"
	pw.Style().Visibility.ETA = true
	pw.Style().Visibility.ETAOverall = true
	pw.Style().Visibility.Percentage = true
	pw.Style().Visibility.Speed = true
	pw.Style().Visibility.SpeedOverall = true
	pw.Style().Visibility.Time = true
	pw.Style().Visibility.TrackerOverall = true
	pw.Style().Visibility.Value = true
	pw.Style().Visibility.Pinned = true

	for _, stock := range stockData {
		wg.Add(1)
		go func() {
			defer wg.Done()
			Send2Kafka(pw, stock.FileName, stock.Stocks, kafkaReady, readySend)
		}()
	}

	// Wait for Kafka to be ready
	for range stockData {
		<-kafkaReady
	}

	go pw.Render()

	for range stockData {
		readySend <- true
	}
	wg.Wait()

	for pw.IsRenderInProgress() {
		time.Sleep(1 * time.Second)
	}
}
