import streamlit as st
from millify import millify

import graficos

def overview(stocks, tickers):
    if stocks.empty:
        return
    
    for ticker in tickers:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])

        abertura = stocks[stocks["ticker"] == ticker].iloc[0]["openv"]
        fechamento = stocks[stocks["ticker"] == ticker].iloc[-1]["closev"]
        variacao = (fechamento - abertura) / abertura * 100
        breakouts = stocks[(stocks["ticker"] == ticker) & (stocks["breakout"] == True)]

        last_date = stocks[stocks["ticker"] == ticker].iloc[-1]["datetime"]

        with col1:
            st.header(ticker)
            st.caption(last_date.strftime("%d/%m/%Y"))
        with col2:
            st.altair_chart(graficos.value_stocks(stocks[stocks["ticker"] == ticker]), use_container_width=True)
        with col3:
            st.metric("Abertura", f"{abertura:.2f}")
        with col4:
            st.metric("Fechamento", f"{fechamento:.2f}", f"{variacao:.2f}%")
    
        with col5:
            st.caption("Breakouts")
            texto = ""

            for breakout in breakouts.iterrows():
                dt = breakout[1]["datetime"]
                texto += dt.strftime("%d/%m/%Y") + "\n"
            st.text(texto)
            
