import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pio.renderers.default='browser'

def get_candlestick_plot(
        df: pd.DataFrame,
        ticker: str
):
    '''
    Create the candlestick chart with two moving avgs + a plot of the volume
    Parameters
    ----------
    df : pd.DataFrame
        The price dataframe
    ma1 : int
        The length of the first moving average (days)
    ma2 : int
        The length of the second moving average (days)
    ticker : str
        The ticker we are plotting (for the title).
    '''
    
    fig = make_subplots(
        rows = 2,
        cols = 1,
        shared_xaxes = True,
        vertical_spacing = 0.1,
        subplot_titles = (f'{ticker} Stock Price', 'Volume Chart'),
        row_width = [0.3, 0.7]
    )
    
    fig.add_trace(
        go.Candlestick(
            x = df['datetime'],
            open = df['openv'], 
            high = df['highv'],
            low = df['lowv'],
            close = df['closev'],
            name = 'Candlestick chart'
        ),
        row = 1,
        col = 1,
    )
        
    fig.add_trace(
        go.Bar(x = df['datetime'], y = df['volume'], name = 'Volume'),
        row = 2,
        col = 1,
    )
    
    fig['layout']['xaxis2']['title'] = 'Date'
    fig['layout']['yaxis']['title'] = 'Price'
    fig['layout']['yaxis2']['title'] = 'Volume'
    
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )
    
    return fig
