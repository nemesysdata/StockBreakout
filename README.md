# StockBreakout
Demonstração de detecção de breakout em Stocks utilizando Apache Kafka e Apache Flink.

Diretórios:

- **deploy** (shell): scripts para a criação instalação do ambiente em um cluster kubernetes.
- **Download Stocks** (go): Download de dados das ações para criar os arquivos de simulação.
- **Replay Stocks** (go): Simulador de Bolsa de Valores. Envia cada linha dos arquivos de dados para um tópico Kafka.
- **Dasboard** (python/streamlit): Dashboard para aconpanhar o processamento dos dados.
- **StockPipeline** (PyFlink): Definição do pipeline para transformação dos dados.
