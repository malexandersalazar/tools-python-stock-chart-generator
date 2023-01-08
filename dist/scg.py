import sys as _s

# %%
import yfinance as yf

import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc

import seaborn as sns
import numpy as np

# Configurando los estílos de los gráficos
plt.ioff()
sns.set_style("darkgrid")
sns.set(rc={'axes.facecolor':'#263238', 'figure.facecolor':'#263238'})
sns.set_context('talk')

# %%
# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
# Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
# Intraday data cannot extend last 60 days


def run(yahoo_symbol, period, interval):

    # %%
    def _get_yfinance_data(yahoo_symbol,period,interval):
        print(f'Retreiving {period}/{interval} data for {yahoo_symbol} from yfinance...')
        tick = yf.Ticker(yahoo_symbol)
        history_df = tick.history(period=period,interval=interval)
        history_df.dropna(inplace=True)
        history_df = history_df[~history_df.index.duplicated(keep='last')]
        return history_df

    # %%
    require_4h_transform = False
    if(interval == '4H'):
        interval = '1H'
        require_4h_transform = True

    stock_data = _get_yfinance_data(yahoo_symbol,period,interval)

    # %%
    if require_4h_transform:
        stock_data = stock_data[::-1]
        stock_data['Open'] = stock_data['Open'].rolling(4).agg(lambda rows: rows[-1])
        stock_data['High'] = stock_data['High'].rolling(4).max()
        stock_data['Low'] = stock_data['Low'].rolling(4).min()
        stock_data['Close']  = stock_data['Close'].rolling(4).agg(lambda rows: rows[0])
        stock_data = stock_data[::-1].copy()
        stock_data.dropna(inplace=True)
        skip = (len(stock_data) - 1) % 4
        stock_data = stock_data.iloc[skip::4]
        interval = '4H'

    # %%
    chart_data_df = stock_data.reset_index()

    # %%
    chart_data_df.rename(columns={"index": "Date" }, inplace=True)

    # %%
    chart_data_df['Timestamp'] = chart_data_df['Date']
    chart_data_df['Order'] = chart_data_df['Date'].apply(mpl_dates.date2num)
    chart_data_ohlc_df = chart_data_df[['Order', 'Open', 'High', 'Low', 'Close']].copy()

    # %%
    chart_data_ohlc_df.sort_values(by='Order',ascending=True, inplace=True)

    # %%
    chart_data_ohlc_df.loc[:,'Order'] = chart_data_df.index.values

    # %%
    size = int(len(chart_data_ohlc_df)  / 12)

    # %%
    plt.clf()
    fig, ax = plt.subplots(figsize=(20,10))

    candlestick_ohlc(ax, chart_data_ohlc_df.values, width=0.5, colorup='#24A06B', colordown='#CC2E3C', alpha=1.0)

    ax.set_xticks(range(len(chart_data_df))[::size])
    ax.set_xticklabels(chart_data_df['Timestamp'][::size].dt.strftime('%Y.%m.%d'))

    current_values = ax.get_yticks()
    ax.set_yticks(current_values)
    ax.set_xlim(0,len(chart_data_df))

    decimals = int(max(0,np.floor(5 - np.log10(np.mean(current_values)))))
    ax.set_yticklabels(['{0:.{precision}f}'.format(x, precision=decimals) for x in current_values])
    ax.set_ylim(min(current_values)+0.000001,max(current_values)-0.000001)

    fig.tight_layout()

    text_interval_props = dict(boxstyle='round', facecolor='#172327',edgecolor='#172327')
    ax.text(0.02, 0.97, f'{yahoo_symbol} [{interval}]', transform=ax.transAxes,verticalalignment='top',bbox=text_interval_props, color='w')
    ax.tick_params(axis='x', colors='white',labelrotation=0)
    ax.tick_params(axis='y', colors='white')
    ax.grid(color='#455A64')
    sns.despine(left=False, bottom=False)

    fig.savefig(f'{yahoo_symbol}_{period}_{interval}.png', bbox_inches='tight')


if __name__ == "__main__":
    yahoo_symbol = str.upper(_s.argv[1])
    period = str.upper(_s.argv[2])
    interval = str.upper(_s.argv[3])
    
    run(yahoo_symbol,period,interval)