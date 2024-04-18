# StockBreakout - Download Stocker

Aplicação em GO para efetuar o Download de dados sobre ações utilizando a API da [Finazon](https://finazon.io/).
É necessário configurar uma variável de ambiente com a API KEY para isso:

```bash
FINAZON_API_KEY=<Finazon API KEY>
```

Para efetuar o download basta rodar o comando ```go run .``` neste diretório e os arquivos serão colocados na pasta dados.

**Obs.:** Os arquivos na pasta dados/complementar possuem dados mais antigos e é mesclado com o que será feito o donwload.
