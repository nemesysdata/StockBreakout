# StockBreakout - Stock Pipeline
Pipeline de processamento dos dados no Apache Flink

- stock_pipeline.py: definição do pipeline em si. Registra as tabelas no flink (kafka e postgres) e ativa o processamento.
- stock_pipeline.yaml: arquivo de definição para iniciar os pods do FLink.

**Obs.:**

1. É necessário fazer a imagem Docker antes de tentar iniciar e enviá-la para o registro de container (dockerhub por exemplo). O script ```buildall``` tem os comando para build.
2. Antes de aplicar o ```stock_pipeline.yaml``` pela primeira vez é necessário aplicar o arquivo ```serviceaccount.yaml``` para autoriza o Flink Operator a manipular os pods no kubernetes.
3. É importante ativar este pipeline antes de iniciar o Simulador de Bolsa.
4. É importante que antes de rodar os tópicos Kafka e as tabelas no Postgres estejam criadas
