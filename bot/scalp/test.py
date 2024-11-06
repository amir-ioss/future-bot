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
        # 'defaultType': 'future'  # Use 'spot' for spot trading, 'future' for Futures
    }
})

# Load the JSON file
with open('data.json', 'r') as file:
    ohlcv_data = json.load(file)


symbol = 'BTC/USDT'
timeframe = '5m'
amount_usdt = 10  # Amount in USDT to spend


def fetch_candles(symbol, timeframe):
    return ohlcv_data
    # return exchange.fetch_ohlcv(symbol, timeframe, limit=1000)

def timestamp_to_HHMM(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000
    
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp_s)
    
    # Format the datetime object to HH:MM
    formatted_time = dt_object.strftime('%H:%M')
    
    return formatted_time



def check_trade_signals(candles):
    # candles = fetch_candles(symbol, timeframe)
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
    # src = closes
    src = opens
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

    if src[-2] > nwe[i] + sae and src[-1] < nwe[i] + sae:
        print(f"Label ▼ at {timestamp_to_HHMM(candles[i][0])} {src[i]}")
        side = 'SHORT'
    if src[-2] < nwe[i] - sae and src[-1] > nwe[i] - sae:
        print(f"Label ▲ at {timestamp_to_HHMM(candles[i][0])} {src[i]}")
        side = 'LONG'



    # Loop to print lines instead of drawing
    for i in range(min(499, n - 1) + 1):
        break
        # print(timestamp_to_HHMM(candles[i][0]), src[i])
        # if i % 2 == 0:
        #     print(f"Line: {n-i+1} -> {n-i}, y1 + sae: {nwe[i] + sae}, color: {upCss}")
        #     print(f"Line: {n-i+1} -> {n-i}, y1 - sae: {nwe[i] - sae}, color: {dnCss}")

        # Check conditions and print labels
        if src[i] > nwe[i] + sae and i + 1 < n and src[i+1] < nwe[i] + sae:
            print(f"Label ▼ at {timestamp_to_HHMM(candles[i][0])} {src[i]}")
            if n-1 == i: side = 'SHORT'
        if src[i] < nwe[i] - sae and i + 1 < n and src[i+1] > nwe[i] - sae:
            print(f"Label ▲ at {timestamp_to_HHMM(candles[i][0])} {src[i]}")
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





def run_bot():
    last_signal = None
    n = len(ohlcv_data)
    print(n)
    for i in range(n):
        if i < n-499:continue
        candles = ohlcv_data[i-499:i+1]
        check_trade_signals(candles)
        # break
    return

    return

    while True:
        print(datetime.now().strftime('%H:%M'))

        side, cand = check_trade_signals()
        if side == 'LONG':
            print(f"{timestamp_to_HHMM(cand[0])}  ▲  LONG at {cand[1]}", )
        if side == 'SHORT':
            print(f"{timestamp_to_HHMM(cand[0])}  ▼  SHORT at {cand[1]}", )
        
        time.sleep(60)  # Run every 15 minutes
        # break;
       
  
if __name__ == "__main__":
    run_bot()
