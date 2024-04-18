# StockBreakout - Replay Stocks
Simulador de bolsa de valores. Envia cada linha dos arquivos de dados da pasta dados para o respectivo tópico Kafka.
O processo utiliza goroutines para tentar ser o mais paralelo possível, porém, existe uma difirença de desempenho devido o tamanho dos 
arquivos.

Para executar:
```bash
go run .
````

**Obs.:** Ativar o Pipeline antes de executar este aplicativo.
