from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly as pl
import plotly.express as px
import yfinance as yf
from dash import Dash, html, dcc
import plotly.graph_objects as go
import warnings
from dash.dependencies import Input, Output

warnings.filterwarnings("ignore")
pd.options.plotting.backend = "plotly"

# initializing a blank string to pass to yahoo finance library

tickers = ""
# initialize an array of (tenor) month codes

tenors = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

tenor_to_month_dict = dict(zip(tenors, months))
print(tenor_to_month_dict)

def tenor_to_month(ten):
    return tenor_to_month_dict[ten]

# initialize an array of desired product statements

instruments = ['CL', 'BZ']

# double for loop through both arrays and append product_symbol + tenor combo to tickers string
def generare_ticker_list(symbol, tenors):
    tickers = ''
    for ten in tenors:
        tickers += f"{symbol}{ten}23.NYM "
    return tickers

# Create seperate tickers for crude and brent

crude_tickers = generare_ticker_list('CL', tenors)
brent_tickers = generare_ticker_list('BZ', tenors)

# pass list of tickers to yfinance library, download daily close prices over the last 30 days

crude_df = yf.download(tickers=crude_tickers, period="30d", interval="1d")
brent_df = yf.download(tickers=brent_tickers, period="30d", interval="1d")

# drop columns where all values are #NA

crude_df = crude_df['Adj Close'].dropna(how='all', axis=1)
brent_df = brent_df['Adj Close'].dropna(how='all', axis=1)

# drop last row of dataframe due to incomplete data from yahoo finance

crude_df.drop(crude_df.tail(1).index, inplace=True)
brent_df.drop(brent_df.tail(1).index, inplace=True)

# reformat column names for clarity

crude_df.columns = [tenor_to_month(x[2]) + x[3:5] for x in crude_df.columns]
brent_df.columns = [tenor_to_month(x[2]) + x[3:5] for x in brent_df.columns]

# gather columns into rows using melt

brent_df = pd.melt(brent_df, ignore_index=False)
brent_df.columns = ["Tenor", "Price"]
brent_df['Product'] = "Brent"

crude_df = pd.melt(crude_df, ignore_index=False)
crude_df.columns = ["Tenor", "Price"]
crude_df['Product'] = "WTI"

# Concatenate the rows of the dataframe to search through one aggregate dataframe

df = pd.concat([brent_df, crude_df])

# Create new Date column and convert date to timestamp as the Dash slider component does not support date comparisons
df.reset_index(inplace=True)
df['Date'] = pd.to_datetime(df['Date']).map(pd.Timestamp.timestamp)

# Initialize the dash frontend

app = Dash(__name__)

# Format HTML for frontent, and add desired components
app.layout = html.Div([
    html.H1(children='Futures Curve for Brent and WTI'),

    html.Div(children='''
    By sliding to the desired day, the graph displays the futures curve for both Brent and WTI on that date, 
    Created by Amr Tarek Sayed
'''),
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        df['Date'].min(),
        df['Date'].max(),
        step=None,
        value=df['Date'].max(),
        marks={int(date): {"label": datetime.utcfromtimestamp(date).strftime('%b-%d'),
                           "style": {
                                     "margin": 'auto',
                                     'color': 'black',
                                     'font-weight': 'bold',
                                     }}
                            for date in df['Date'].unique()},
        id='date-slider'
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('date-slider', 'value'))
def update_figure(selected_date):
    filtered_df = df[df['Date'] == selected_date]
    fig = px.line(filtered_df, x="Tenor", y="Price",
                     color="Product")

    return fig
if __name__ == '__main__':
    app.run_server(debug=True)

x=1
