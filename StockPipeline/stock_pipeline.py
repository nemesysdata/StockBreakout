################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################
import logging
import os
import sys

from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.table import StreamTableEnvironment

POSTGRES_HOST = "postgres-dw-ha.stock-dw.svc"
POSTGRES_PORT = "5432"
POSTGRES_DB = "dw"
POSTGRES_USER = "postgres"
POSTGRES_PASS = "SPNyVLLeqd3qLE8lgRw04Kua"

KAFKA_HOST = "demo-kafka-kafka-plain-bootstrap.kafka.svc"
KAFKA_PORT = "9092"

KAFKA_STARTUP_MODE = "earliest-offset"

def addJars(env):
    print("Adding jars")
    env.add_jars(
      "file:///opt/flink/usrlib/flink-sql-connector-kafka-3.1.0-1.18.jar", 
      "file:///opt/flink/usrlib/flink-connector-jdbc-3.1.2-1.18.jar", 
      "file:///opt/flink/usrlib/postgresql-42.7.3.jar"
    )

def createHiveTables(t_env):
    print("Creating Hive tables")
    print("  - stocks")
    t_env.execute_sql(f"""
      CREATE TABLE stocks_intraday (
        ticker        STRING,
        datetime      TIMESTAMP(3),
        openv         float,
        highv         float,
        lowv          float,
        closev        float,
        volume        float
      ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}',
        'table-name' = 'public.intraday',
        'username' = '{POSTGRES_USER}',
        'password' = '{POSTGRES_PASS}'
    )""")

    print("  - breakouts")
    t_env.execute_sql(f"""
      create table if not exists breakouts (
        ticker        		varchar,
        datetime      		timestamp,
        openv         		float,
        highv         		float,
        lowv          		float,
        closev        		float,
        volume        		float,
        o_to_c 		  		  float,
        OC_20D_Mean	  		float,
        OC_Perc_20D_Mean	float,
        MaxOC_Prev10D		  float,
        Vol_20D_Mean		  float,
        Vol_Perc_20D_Mean	float,
        breakout			    boolean,
        primary key (ticker, datetime) not enforced
    ) WITH (
      'connector' = 'jdbc',
      'url' = 'jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}',
      'table-name' = 'public.breakouts',
      'username' = '{POSTGRES_USER}',
      'password' = '{POSTGRES_PASS}'
    )""")
    
def createKafkaTables(t_env, topicos, TOPIC):
    print("Creating Kafka tables")
    for topico in topicos:
      print(f"  - {topico}")
      t_env.execute_sql(f"""
      CREATE TABLE {topico} (
        ticker        STRING,
        datetime      TIMESTAMP(3),
        openv         float,
        highv         float,
        lowv          float,
        closev        float,
        volume        float,
        watermark for datetime as datetime
      ) WITH (
        'connector' = 'kafka',
        'topic' = '{topico.upper()}',
        'properties.bootstrap.servers' = '{KAFKA_HOST}:{KAFKA_PORT}',
        'properties.group.id' = 'StockPipeline_{TOPIC}',
        'scan.startup.mode' = '{KAFKA_STARTUP_MODE}',
        'format' = 'json'
      )""")

      t_env.execute_sql(f"""
        CREATE TABLE if not exists diario_{topico} (
          ticker        STRING,
            datetime      TIMESTAMP(3),
            openv         float,
            highv         float,
            lowv          float,
            closev        float,
            volume        float,
            o_to_c		  float,
            watermark for datetime as datetime
        ) WITH (
          'connector' = 'kafka',
          'topic' = 'DIARIO_{topico.upper()}',
          'properties.bootstrap.servers' = '{KAFKA_HOST}:{KAFKA_PORT}',
          'properties.group.id' = 'StockPipeline_{TOPIC}',
          'scan.startup.mode' = '{KAFKA_STARTUP_MODE}',
          'format' = 'json'
        );
    """)

def main():
  STEP = os.getenv("STEP", "")
  TOPIC = os.getenv("TOPIC", "")

  if STEP not in ["INGESTION", "AGGREGATE"]:
    print("Invalid STEP")
    sys.exit(1)

  if TOPIC not in ["aapl", "amzn", "meta", "msft", "tsla", ""]:
    print("Invalid TOPIC")
    sys.exit(1)

  if STEP == "AGGREGATE" and TOPIC == "":
    print("Aggreate STEP needs TOPIC to be defined")
    sys.exit(1)
    
  topicos = ["aapl", "amzn", "meta", "msft", "tsla", "stocks"]
  env = StreamExecutionEnvironment.get_execution_environment()
  env.enable_checkpointing(1000)
  cfg = env.get_checkpoint_config()
  cfg.set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
  # env.set_parallelism(1)

  addJars(env)

  t_env = StreamTableEnvironment.create(stream_execution_environment=env)
  stmt_set = t_env.create_statement_set()

  createHiveTables(t_env)
  createKafkaTables(t_env, topicos, TOPIC)

  if STEP == "INGESTION":
    print("Inserting data into stocks topic")
    stmt_set.add_insert_sql(f"""
      INSERT INTO stocks
      SELECT * FROM aapl
      UNION ALL SELECT * FROM amzn
      UNION ALL SELECT * FROM meta
      UNION ALL SELECT * FROM msft
      UNION ALL SELECT * FROM tsla
    """)

    print("Inserting data into intraday table")
    stmt_set.add_insert_sql(f"""
      INSERT INTO stocks_intraday
      SELECT * FROM stocks
    """)

  if STEP == "AGGREGATE":
    print(f"Inserting data into diario_{TOPIC} table from {TOPIC}")
    stmt_set.add_insert_sql(f"""
      insert into diario_{TOPIC}
      select 
        ticker,
        tumble_start(datetime, interval '1' day) as window_start,
        first_value(openv) as openv,
        min(lowv) as minv,
        max(highv) as highv,
        last_value(closev) as closev,
        sum(volume) as volume,
        last_value(closev) - first_value(openv) as o_to_c
      from {TOPIC}
      group by ticker, tumble(datetime, interval '1' day);
    """)

    print("Inserting data into breakouts table")
    stmt_set.add_insert_sql(f"""
      insert into breakouts
      select
        *,
        case when o_to_c > 0 and o_to_c = MaxOC_Prev10D and OC_Perc_20D_Mean > 100 and Vol_Perc_20D_Mean > 50 then true else false end as breakout
      from (
        select 
          ticker,
          datetime,
          openv,
          highv,
          lowv,
          closev,
          volume,
          o_to_c,
          OC_20D_Mean,
          cast(100 * (o_to_c - OC_20D_Mean) / OC_20D_Mean as float) as OC_Perc_20D_Mean,	
          max(o_to_c) over (partition by ticker order by datetime rows between 9 preceding and current row) as MaxOC_Prev10D,
          Volume_20D_Mean,
          cast(100 * (volume - Volume_20D_Mean) / Volume_20D_Mean as float) as Vol_Perc_20D_Mean	
        from (
          select 
            *,
            cast(AVG(o_to_c) over (partition by ticker order by datetime rows between 19 preceding and current row) as float) as OC_20D_Mean,
            --cast((1 - o_to_c / AVG(o_to_c) over (partition by ticker order by datetime rows between 19 preceding and current row)) * 100.0 as float) as OC_Perc_20D_Mean,
            cast(AVG(volume) over (partition by ticker order by datetime rows between 19 preceding and current row) as float) as Volume_20D_Mean
            --cast((1 - volume / AVG(volume) over (partition by ticker order by datetime rows between 19 preceding and current row)) * 100.0 as float) as Vol_Perc_20D_Mean
          from diario_{TOPIC}
        )
      )
    """)

  table_result = stmt_set.execute()
  print(table_result.get_job_client().get_job_status())


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    main()
    