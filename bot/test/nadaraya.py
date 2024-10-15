import ccxt
import time
from datetime import datetime
import json
import math

# Initialize your exchange
exchange = ccxt.binance({
    # 'apiKey': 'your_api_key',
    # 'secret': 'your_api_secret',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'  # Use 'spot' for spot trading, 'future' for Futures
    }
})

# Load the JSON file
# with open('2024-03-11.json', 'r') as file:
#     ohlcv_data = json.load(file)


symbol = 'BTC/USDT'
timeframe = '1m'
amount_usdt = 10  # Amount in USDT to spend


def fetch_candles(symbol, timeframe):
    return exchange.fetch_ohlcv(symbol, timeframe, limit=499)

def timestamp_to_HHMM(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000
    
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp_s)
    
    # Format the datetime object to HH:MM
    formatted_time = dt_object.strftime('%H:%M')
    
    return formatted_time



def check_trade_signals():
    candles = fetch_candles(symbol, timeframe)
    # candles = ohlcv_data
    opens = [candle[1] for candle in candles]
    highs = [candle[2] for candle in candles]
    lows = [candle[3] for candle in candles]
    closes = [candle[4] for candle in candles]
    top = [True]
    bottom = [True]
    side = None


        # Input parameters
    h = 8.0
    mult = 3.0
    upCss = "green"  # Color for up condition
    dnCss = "red"   # Color for down condition
    src = closes
    n = len(src)
    

    # Functions
    def gauss(x, h):
        return math.exp(-(math.pow(x, 2) / (h * h * 2)))

    # Initialize variables
    nwe = []
    mae_history = []


    sae = 0.0

    # Compute and set NWE point
    for i in range(min(499, n - 1) + 1):
        sum = 0.0
        sumw = 0.0

        # Compute weighted mean
        for j in range(min(499, n - 1) + 1):
            w = gauss(i - j, h)
            sum += src[j] * w
            sumw += w

        y2 = sum / sumw
        sae += abs(src[i] - y2)
        nwe.append(y2)

    sae = sae / min(499, n - 1) * mult
    


    # Loop to print lines instead of drawing
    for i in range(min(499, n - 1) + 1):
        # print(timestamp_to_HHMM(candles[i][0]), src[i])
        # if i % 2 == 0:
        #     print(f"Line: {n-i+1} -> {n-i}, y1 + sae: {nwe[i] + sae}, color: {upCss}")
        #     print(f"Line: {n-i+1} -> {n-i}, y1 - sae: {nwe[i] - sae}, color: {dnCss}")

        # Check conditions and print labels
        if src[i] > nwe[i] + sae and i + 1 < n and src[i+1] < nwe[i] + sae:
            print(f"Label ▼ at {timestamp_to_HHMM(candles[i][0])} (close: {src[i]}), color: {dnCss}")
            if n-1 == i: side = 'SHORT'
        if src[i] < nwe[i] - sae and i + 1 < n and src[i+1] > nwe[i] - sae:
            print(f"Label ▲ at {timestamp_to_HHMM(candles[i][0])} (close: {src[i]}), color: {upCss}")
            if n-1 == i: side = 'LONG'
        



    # for i, cand in enumerate(candles):
    #     # print(f"Index: {index}, cand: {cand}")
    #     if i < per*2 : continue
    #     end = i == len(candles)-1
    #     open = opens[:i+1]
    #     high = highs[:i+1]
    #     low = lows[:i+1]
    #     close = closes[:i+1]
    #     time = timestamp_to_HHMM(cand[0])

     
    #     pass

    return side, candles[-1]
# end of analyses


def check_balance():
    # Fetch balance information
    balance = exchange.fetch_balance()
    
    # Fetch USDT balance in Futures account
    usdt_balance = balance['total'].get('USDT', 0)
    
    return usdt_balance

def long(symbol, amount_usdt):
    # Check balance
    usdt_balance = check_balance()
    
    if usdt_balance < amount_usdt:
        print(f"Insufficient balance. Available: {usdt_balance} USDT, Required: {amount_usdt} USDT")
        return None
    
    # Calculate the amount of BTC to buy based on the current price
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']  # Last price of the symbol
    amount_btc = amount_usdt / price
    
    # Create a market buy order
    order = exchange.create_market_order(symbol, 'buy', amount_btc)
    
    return order

def short(symbol, amount_usdt):
    # Check balance
    usdt_balance = check_balance()
    
    if usdt_balance < amount_usdt:
        print(f"Insufficient balance. Available: {usdt_balance} USDT, Required: {amount_usdt} USDT")
        return None
    
    # Calculate the amount of BTC to short based on the current price
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']  # Last price of the symbol
    amount_btc = amount_usdt / price
    
    # Create a market sell order to open a short position
    order = exchange.create_market_order(symbol, 'sell', amount_btc)
    
    return order

def close_position(symbol, amount_btc, side):
    # Create a market order to close the position
    # If side is 'buy', it will close a short position
    # If side is 'sell', it will close a long position
    order = exchange.create_market_order(symbol, side, amount_btc)
    
    return order



def run_bot():
    last_signal = None


    while True:
        print(datetime.now().strftime('%H:%M'))

        side, cand = check_trade_signals()
        if side == 'LONG':
            print(f"{timestamp_to_HHMM(cand[0])}  ▲  LONG at {cand[1]}", )
        if side == 'SHORT':
            print(f"{timestamp_to_HHMM(cand[0])}  ▼  SHORT at {cand[1]}", )
        
        time.sleep(60)  # Run every 15 minutes
        # break;
        continue



        amount_btc = 0
        if last_signal != 'LONG' and side == 'LONG':
            last_signal = side

            # exit
            if last_signal: 
                print('Close the short position')
                close_order = close_position(symbol, amount_btc, 'buy')
                if close_order:
                    print("short closed successfully:", close_order)
                    time.sleep(2)


            # entry
            print('LONG')
            long_order = long(symbol, amount_usdt)
            if long_order:
                print("Long order created successfully:", long_order)
            # Calculate the amount of BTC to sell
            amount_btc = long_order['amount']  # Amount to close
            pass


        if last_signal != 'SHORT' and side == 'SHORT':
            last_signal = side

            # exit
            if last_signal: 
                print('Close the long position')
                close_order = close_position(symbol, amount_btc, 'sell')
                if close_order:
                    print("long closed successfully:", close_order)
                    time.sleep(2)

            # entry
            print('SHORT')
            short_order = short(symbol, amount_usdt)
            if short_order:
                print("Short order created successfully:", short_order)
            amount_btc = long_order['amount']  # Amount to close
            pass 
        
        time.sleep(60)  # Run every 15 minutes
    
  
if __name__ == "__main__":
    run_bot()
