import pandas as pd
import ta
import matplotlib.pyplot as plt
from binance.client import Client
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

# Indicator calculation
k_lines['RSI'] = ta.momentum.RSIIndicator(k_lines['close']).rsi()
k_lines['CCI'] = ta.trend.CCIIndicator(k_lines['high'], k_lines['low'], k_lines['close']).cci()
k_lines['MACD'] = ta.trend.MACD(k_lines['close']).macd()
k_lines['ATR'] = ta.volatility.AverageTrueRange(k_lines['high'], k_lines['low'], k_lines['close']).average_true_range()
k_lines['ADX'] = ta.trend.ADXIndicator(k_lines['high'], k_lines['low'], k_lines['close']).adx()

# Creating signal columns
for indicator in ['RSI', 'CCI', 'MACD', 'ATR', 'ADX']:
    k_lines[f'{indicator}_buy_signal'] = (k_lines[indicator] < 30) & (k_lines[indicator].shift() >= 30)
    k_lines[f'{indicator}_sell_signal'] = (k_lines[indicator] > 70) & (k_lines[indicator].shift() <= 70)

# Visualization of closing prices and indicators with signals
fig, axs = plt.subplots(6, 1, figsize=(14, 10), sharex=True)

axs[0].plot(k_lines['time'], k_lines['close'], label='Close Price', color='purple')
axs[0].set_title('Close Price')
axs[0].legend()

for i, indicator in enumerate(['RSI', 'MACD', 'ATR', 'ADX', 'CCI']):
    axs[i+1].plot(k_lines['time'], k_lines[indicator], label=indicator, color='purple')
    axs[i+1].scatter(k_lines.loc[k_lines[f'{indicator}_buy_signal'], 'time'], k_lines.loc[k_lines[f'{indicator}_buy_signal'], indicator], marker='^', color='green', label='Buy Signal')
    axs[i+1].scatter(k_lines.loc[k_lines[f'{indicator}_sell_signal'], 'time'], k_lines.loc[k_lines[f'{indicator}_sell_signal'], indicator], marker='v', color='red', label='Sell Signal')
    axs[i+1].set_title(indicator)
    axs[i+1].legend()

# Format x-axis dates
date_form = DateFormatter("%m-%d %H:%M")
for ax in axs:
    ax.xaxis.set_major_formatter(date_form)

plt.tight_layout()
plt.show()
