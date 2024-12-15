import sqlalchemy
import pandas as pd
import pandas.io.sql as psql

from k8s import K8S

# gets loadbalancer ip from k8s service called postgres-dw-ha on namespace stock-dw

k8s = K8S()
POSTGRES_HOST = k8s.get_service_ip('psql-dw-postgresql', 'stock-dw')
POSTGRES_PORT = '5432'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'mysecret'
POSTGRES_DBNAME = 'dw'
#
# Connectar to database
#

def stock_position(interval='30'):
    engine = sqlalchemy.create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DBNAME}")
    df = psql.read_sql(f"""
        select *
        from breakouts be
        -- where datetime >= (select (max(datetime) - interval '{interval} days') from breakouts bi where bi.ticker = be.ticker)
        order by datetime, ticker 
    """, con=engine)

    engine.dispose()

    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize('America/Sao_Paulo')
    
    return df

def stock_full(ticker):
    engine = sqlalchemy.create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DBNAME}")
    df = psql.read_sql(f"""
        select *
        from breakouts be
        where ticker = '{ticker}'
        order by datetime, ticker 
    """, con=engine)

    engine.dispose()

    # df["datetime"] = pd.to_datetime(df["datetime"]).dt.date
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize('America/Sao_Paulo')

    return df

def tickers():
    engine = sqlalchemy.create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DBNAME}")
    df = psql.read_sql("select distinct ticker from breakouts order by ticker", con=engine)
    engine.dispose()

    return df['ticker'].tolist()
