import pandas as pd
from binance import Client
from dataclasses import dataclass
from typing import List, Tuple

import ta  # Make sure to install with pip install ta

@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float = None
    closed_by: str = None

def perform_backtesting(k_lines: pd.DataFrame) -> List[Signal]:
    signals = create_signals(k_lines)
    results = []
    for signal in signals:
        data_slice = k_lines[k_lines['time'] >= signal.time].reset_index(drop=True)
        for index, row in data_slice.iterrows():
            if (signal.side == "sell" and row["low"] <= signal.take_profit) or \
               (signal.side == "buy" and row["high"] >= signal.take_profit):
                signal.result = (signal.take_profit - signal.entry) if signal.side == 'buy' else (signal.entry - signal.take_profit)
                signal.closed_by = "TP"
                break
            elif (signal.side == "sell" and row["high"] >= signal.stop_loss) or \
                 (signal.side == "buy" and row["low"] <= signal.stop_loss):
                signal.result = (signal.stop_loss - signal.entry) if signal.side == 'buy' else (signal.entry - signal.stop_loss)
                signal.closed_by = "SL"
                break
        if signal.result is not None:
            results.append(signal)
    return results

def calculate_pnl(trade_list: List[Signal]) -> float:
    return sum(trade.result for trade in trade_list if trade.result is not None)

def profit_factor(trade_list: List[Signal]) -> float:
    total_profit = sum(trade.result for trade in trade_list if trade.result > 0)
    total_loss = sum(-trade.result for trade in trade_list if trade.result < 0)
    return total_profit / total_loss if total_loss != 0 else float('inf')  # Avoid division by zero

def create_signals(k_lines: pd.DataFrame) -> List[Signal]:
    signals = []
    for index, row in k_lines.iterrows():
        current_price = row['close']
        if row['cci'] < -100 and row['adx'] > 25:
            side = 'sell'
        elif row['cci'] > 100 and row['adx'] > 25:
            side = 'buy'
        else:
            continue

        stop_loss_price = round((1 + 0.01) * current_price, 1) if side == 'sell' else round((1 - 0.01) * current_price, 1)
        take_profit_price = round((1 - 0.015) * current_price, 1) if side == 'sell' else round((1 + 0.015) * current_price, 1)
        
        signals.append(Signal(
            time=row['time'],
            asset='BTCUSDT',
            quantity=100,
            side=side,
            entry=current_price,
            take_profit=take_profit_price,
            stop_loss=stop_loss_price
        ))
    return signals

# Usage example:
client = Client()
k_lines = client.get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 week ago UTC",
    end_str="now UTC"
)

# Convert to DataFrame and preprocess
k_lines_df = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                            'taker_buy_quote_asset_volume', 'ignore'])
k_lines_df[['open', 'high', 'low', 'close']] = k_lines_df[['open', 'high', 'low', 'close']].astype(float)
k_lines_df['time'] = pd.to_datetime(k_lines_df['time'], unit='ms')

# Calculate indicators
adx_indicator = ta.trend.ADXIndicator(k_lines_df['high'], k_lines_df['low'], k_lines_df['close'], window=14)
cci_indicator = ta.trend.CCIIndicator(k_lines_df['high'], k_lines_df['low'], k_lines_df['close'], window=20)
k_lines_df['adx'] = adx_indicator.adx()
k_lines_df['cci'] = cci_indicator.cci()

results = perform_backtesting(k_lines_df)
for result in results:
    print(f"Time: {result.time}, Asset: {result.asset}, Quantity: {result.quantity}, Side: {result.side}, "
          f"Entry: {result.entry}, Take Profit: {result.take_profit}, Stop Loss: {result.stop_loss}, Result: {result.result}, Closed_by: {result.closed_by}")
print("Total PnL:", calculate_pnl(results))
print("Profit Factor:", profit_factor(results))
