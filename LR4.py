import pandas as pd
import ta
import matplotlib.pyplot as plt
from binance import Client
from matplotlib.dates import DateFormatter

# Loading data
k_lines = Client().get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 day ago UTC",
    end_str="now UTC"
)

# Creating DataFrame
k_lines = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')
k_lines[['close', 'high', 'low', 'open']] = k_lines[['close', 'high', 'low', 'open']].astype(float)

# Calculation of indicators
periods = [14, 27, 100]
for period in periods:
    rsi_indicator = ta.momentum.RSIIndicator(k_lines['close'], window=period)
    k_lines[f'RSI_{period}'] = rsi_indicator.rsi()

# Visualization of closing prices and indicators
plt.figure(figsize=(14, 10))
plt.subplot(4, 1, 1)
plt.plot(k_lines['time'], k_lines['close'], label='Close Price')
plt.title('Close Price')
plt.ylabel('Price')

for period in periods:
    plt.subplot(4, 1, periods.index(period) + 2)
    plt.plot(k_lines['time'], k_lines[f'RSI_{period}'], label=f'RSI_{period}', color='purple')
    plt.title(f'RSI_{period}')
    plt.ylabel('RSI')
    plt.legend()

# Format x-axis dates
date_form = DateFormatter("%m-%d %H:%M")
plt.gca().xaxis.set_major_formatter(date_form)

plt.tight_layout()
plt.show()
