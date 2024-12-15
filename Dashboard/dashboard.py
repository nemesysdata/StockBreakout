import pandas as pd
import streamlit as st

import dados
import graficos
from partes.overview import overview
from partes.breakouts import breakouts

from streamlit_autorefresh import st_autorefresh
from vega_datasets import data
#
# Configurar Página e auto refresh
#
st.set_page_config(layout="wide", page_title='Kafka Meetup', page_icon=':chart_with_upwards_trend:')
st.title(":chart_with_upwards_trend: Stocks Dashboard")
#
# Criar tabs
#
tabOverview, tabBreakouts, tabMonitor = st.tabs(["Geral", "Breakouts", "Monitor"])
#
# Obter os dados
#

tickers = dados.tickers()
#
# Consifgurar sidebar
#
# dias = st.sidebar.slider("Janela Visualização", 30, 180, 90, step=30)

auto_refresh = st.sidebar.toggle("Auto Refresh", False)

if auto_refresh:
    st_autorefresh(interval=1000)

stocks = dados.stock_position(0)
ticker = st.sidebar.selectbox(
    'Ticker to Plot', 
    options = tickers
)
#
# Gerar os Gráficos
#
with tabOverview:
    overview(stocks, tickers)

with tabBreakouts:
    breakouts(dados.stock_full(ticker), ticker)
