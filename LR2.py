import pandas as pd
from binance.client import Client


def calculate_rsi(prices, period):
    deltas = prices.diff()
    gains = deltas.where(deltas > 0, 0)
    losses = -deltas.where(deltas < 0, 0)
    avg_gain = gains.rolling(window=period, min_periods=1).mean()
    avg_loss = losses.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_rsi_data(asset, periods):
    client = Client()
    klines = client.get_historical_klines(
        symbol=asset,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str="1 day ago UTC",
        end_str="now UTC"
    )
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['close'] = df['close'].astype(float)
    result = pd.DataFrame({'time': df['time']})
    for period in periods:
        rsi_values = calculate_rsi(df['close'], period)
        result[f'RSI_{period}'] = rsi_values
    return result

asset = "BTCUSDT"
periods = [14, 27, 100]
rsi_data = get_rsi_data(asset, periods)
print(rsi_data)
