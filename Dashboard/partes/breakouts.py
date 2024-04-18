import pandas as pd
import streamlit as st

from datetime import datetime, timedelta
from millify import millify

import graficos

def breakouts(stocks, ticker):
    if stocks.empty:        
        return
    
    col1, col2 = st.columns([0.9, 0.1], gap="large")
    breakouts = stocks[(stocks["ticker"] == ticker) & (stocks["breakout"] == True)]


    datas = []
    for breakout in breakouts.iterrows():
        dt = breakout[1]["datetime"]
        datas.append(dt.strftime("%d/%m/%Y"))

    with col2:
        data = st.radio("Breakout", datas)
        data_breakout = (datetime.strptime(data, "%d/%m/%Y") if data else datetime.now()).astimezone()

    delta = timedelta(days=30)
    periodo = stocks[stocks["datetime"] >= data_breakout - delta]
    periodo = periodo[periodo["datetime"] <= data_breakout + delta]

    with col1:
        st.altair_chart(graficos.candle_stick(periodo, data_breakout), use_container_width=True)

    colv, colp1, colp2 = st.columns([1, 1, 1])
    
    with colv:
        st.altair_chart(graficos.o_c_analysis(periodo, data_breakout), use_container_width=True)
    
    with colp1:
        st.altair_chart(graficos.perc_analysis1(periodo, data_breakout), use_container_width=True)

    with colp2:
        st.altair_chart(graficos.perc_analysis2(periodo, data_breakout), use_container_width=True)
