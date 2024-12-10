import numpy as np
import pandas as pd

import talib

import ccxt

# Initialize Binance Testnet
exchange = ccxt.binance(
#     {
#     "apiKey": "YOUR_API_KEY",  # Replace with your testnet API key
#     "secret": "YOUR_SECRET",  # Replace with your testnet secret
#     "options": {"defaultType": "future"},  # Use futures if needed
# }
)

# Switch to Testnet
exchange.set_sandbox_mode(True)
# def fetch_ohlcv(symbol = "BTC/USDT", timeframe = "1m", limit=10):
#     ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
#     # Unpack OHLCV data
#     time, open_, high, low, close, volume = zip(*ohlcv)
#     return {"time" : time, "open" : open_, "high" : high, "low" : low, "close" : close, "volume" : volume}

def fetch_ohlcv(symbol="BTC/USDT", timeframe="1m", limit=10):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    # Unpack OHLCV data
    time, open_, high, low, close, volume = zip(*ohlcv)
    return {
        "time": np.array(time),
        "open": np.array(open_),
        "high": np.array(high),
        "low": np.array(low),
        "close": np.array(close),
        "volume": np.array(volume),
    }

# time,open_,high,low,close,volume = fetch_ohlcv('BTC/USDT', '1m', 5)
# print(time[-1], open_[-1], high[-1], low[-1], close[-1], volume[-1])
# # Generate random data
# close = np.random.random(100)


inputs = {
    "0": "10000",
    "1": "100",
    "2": "output['0'] - output['1']",
    "3": "output['2'] - output['1']"
}
# # Initialize the output dictionary
output = {}
# Function to resolve dependencies dynamically
def resolve_dependencies(inputs):
    # Keep processing until all inputs are resolved
    while inputs:
        for key, formula in list(inputs.items()):
            try:
                # Attempt to evaluate the formula

                if "->" in formula:
                    expression, keys_str = formula.split("->")
                    # print("Expression:", expression.strip())
                    # print("Keys:", keys_str.strip())

                    out = {}
                    keys = eval(keys_str.strip())  # Evaluate keys part
                    res = eval(expression.strip())
                    for i, key_name in enumerate(keys):
                        out[key_name] = res[i]

                    output[key] = out
                else:
                    output[key] = eval(formula)

                    
                del inputs[key]  # Remove resolved item
                print('\n\n\n\n\n==================================')
                print(key, formula)
                # print(output[key])
                break
            except KeyError:
                # Skip if dependencies are not resolved yet
                pass

# Resolve all inputs
resolve_dependencies(inputs)


# Print the final output
print("---", output['3'])




# output = {'0': {'close': np.random.random(100)}}  # Replace with actual closing price data

ob = {

}

# def mcd():
#     return 1,2

# ob['0'] = eval("mcd()")

# print(ob['0'][0])


# formula = "talib.MACD(output['0']['close'], 12, 26, 9) -> ['hist', 'macd', 'signal']"

# if "->" in formula:
#     expression, keys_str = formula.split("->")
#     print("Expression:", expression.strip())
#     print("Keys:", keys_str.strip())

#     out = {}
#     keys = eval(keys_str.strip())  # Evaluate keys part
#     res = eval(expression.strip())
#     for i, key_name in enumerate(keys):
#         out[key_name] = res[i]
#     ob['1'] = out

# print(ob['1']['signal'][-1])



# np.random.seed(42)
# data = {
#     'close': np.cumsum(np.random.normal(0, 1, 100)) + 100  # Random walk around 100
# }
# df = pd.DataFrame(data)
# df['timestamp'] = pd.date_range(start="2024-01-01", periods=len(df), freq='1T')
# # Calculate SMA-25 and SMA-50
# df['sma25'] = df['close'].rolling(window=25).mean()
# df['sma50'] = df['close'].rolling(window=50).mean()

# # Generate crossover signals
# df['signal'] = (df['sma25'] > df['sma50']).astype(int)  # 1 for SMA-25 > SMA-50
# df['crossover'] = df['signal'].diff()  # 1 for buy, -1 for sell

# # SIMULATE 
# # Initialize variables
# initial_balance = 10000  # Starting capital
# balance = initial_balance
# trade_size = 1000  # Fixed trade size
# fees = 0.001  # 0.1% trading fee
# position = None  # Track the current position ('long' or None)
# entry_price = None
# total_trades = 0
# winning_trades = 0
# trade_log = []

# # Iterate through data
# for i, row in df.iterrows():
#     price = row['close']
#     crossover = row['crossover']
    
#     if crossover == 1 and position is None:  # Buy signal
#         # Open a long position
#         position = 'long'
#         entry_price = price
#         balance -= trade_size * (1 + fees)  # Deduct trade size and fees
#         trade_log.append(f"Buy at {price:.2f}")
#         total_trades += 1
    
#     elif crossover == -1 and position == 'long':  # Sell signal
#         # Close the long position
#         profit = (price - entry_price) * (trade_size / entry_price)
#         balance += trade_size + profit - (trade_size * fees)  # Add profit and deduct fees
#         if profit > 0:
#             winning_trades += 1
#         trade_log.append(f"Sell at {price:.2f}, Profit: {profit:.2f}")
#         position = None
#         entry_price = None

# # Final balance
# net_pnl = balance - initial_balance
# print(f"Final Balance: ${balance:.2f}")
# print(f"Net PnL: ${net_pnl:.2f}")
# print(f"Winning Trades: {winning_trades}/{total_trades}")


