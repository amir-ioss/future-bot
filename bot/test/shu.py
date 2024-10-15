import ccxt
import time
from datetime import datetime
import json
import logging


def percentage_difference(number1, number2):
    # difference = abs(number1 - number2)
    difference = number2 - number1 
    percentage_diff = (difference / number1) * 100
    return percentage_diff

# Set up the logger to write to log.txt
logging.basicConfig(filename='log_top_bot.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(action, details=""):
    """
    Logs CRUD actions with optional details.
    """
    logging.info(f"{action} - {details}")

# CRUD Functions
def log(item):
    log_action("LOG", f"{item}")
    # Your create logic here
    print(f"{item}")
    return f"Created {item}"


# Initialize your exchange
exchange = ccxt.binance({
    'apiKey': '#',
    'secret': '#',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'  # Use 'spot' for spot trading, 'future' for Futures
    }
})

# Load the JSON file
# with open('2024-03-11.json', 'r') as file:
#     ohlcv_data = json.load(file)


symbol = 'UNI/USDT'
timeframe = '30m'
amount_usdt = 4  # Amount in USDT to spend

per = 25
trailingStopLoss = .25 # 25% of current change

# Load the JSON file
# with open('xrp/XRP_2023_01.json', 'r') as file:
#     ohlcv_data = json.load(file)

def fetch_candles(symbol, timeframe):
    return exchange.fetch_ohlcv(symbol, timeframe, limit=300)
    # return ohlcv_data

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


    for index, cand in enumerate(candles):
        # print(f"Index: {index}, cand: {cand}")
        if index < per*2 : continue
        end = index == len(candles)-1
        open_ = opens[:index+1]
        high = highs[:index+1]
        low = lows[:index+1]
        close = closes[:index+1]
        time = timestamp_to_HHMM(cand[0])
       
        loc = low[-1] < min(low[-per+1:-1]) and low[-1] <= min(low[-per*2:-per])
        bottom.append(loc)
        last_true_index_bottom = len(bottom) - 1 - bottom[::-1].index(True)
        bottom_signal = len(bottom) - last_true_index_bottom - 1
        
        loc2 = high[-1] > max(high[-per+1:-1]) and high[-1] >= max(high[-per*2:-per])
        top.append(loc2)
        last_true_index_top = len(top) - 1 - top[::-1].index(True)
        top_signal = len(top) - last_true_index_top - 1

        # print(index, bottom_signal, top_signal)

        buy = bottom_signal > top_signal
        sell = bottom_signal < top_signal
        if buy and side != 'LONG': 
            # print(time, 'BUY')
            side = 'LONG'
        if sell and side != 'SHORT': 
            # print(time, 'SELL')
            side = 'SHORT'

        if end:
            pass

    return side, cand[1]
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
    amount_to_trade  = amount_usdt / price
    
    # Create a market buy order
    order = exchange.create_market_order(symbol, 'buy', amount_to_trade *10)
    
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
    amount_to_trade  = amount_usdt / price
    
    # Create a market sell order to open a short position
    order = exchange.create_market_order(symbol, 'sell', amount_to_trade *10)
    
    return order

def close_position(symbol, amount_to_trade , side):
    # Create a market order to close the position
    # If side is 'buy', it will close a short position
    # If side is 'sell', it will close a long position
    order = exchange.create_market_order(symbol, side, amount_to_trade)
    
    return order





def run_bot():
    # States
    last_signal = 'SHORT'
    isOrderPlaced = False
    amount_to_trade = 0
    entry = 0.1
    trailing = False
    edge = 0


    while True:
        t = datetime.now().strftime('%H:%M')
        print(t)

        side, open_ = check_trade_signals()
        
        # EDGE
        if last_signal == 'LONG': 
            edge = open_ if open_ > edge else edge
        elif last_signal == 'SHORT': 
            edge = open_ if edge == 0 else edge # initial
            edge = open_ if open_ < edge else edge

        change = abs(percentage_difference(entry, open_))

        if trailing:
            print(t, "Trailing Enabled")
            reject_change = percentage_difference(edge, open_)

            if reject_change < -change*trailingStopLoss and last_signal == 'LONG':
                close_order = close_position(symbol, amount_to_trade , 'sell')
                if close_order:
                    log(f"LONG EXIT on trailing {reject_change} < {-change*trailingStopLoss}")
                    log(str(close_order))
                    trailing = False
                    isOrderPlaced = False
                    time.sleep(2)

            if reject_change > change*trailingStopLoss and last_signal == 'SHORT':
                close_order = close_position(symbol, amount_to_trade , 'buy')
                if close_order:
                    log(f"LONG EXIT on trailing {reject_change} > {change*trailingStopLoss}")
                    log(str(close_order))
                    trailing = False
                    isOrderPlaced = False
                    time.sleep(2)

        # Trailing Enable                    
        if change > 1 and isOrderPlaced : trailing = True

        # Stop loss
        if change > .5 and  last_signal == 'LONG' and isOrderPlaced and open_ < entry:
            close_order = close_position(symbol, amount_to_trade , 'sell')
            if close_order:
                log(f"LONG EXIT on SL {change} > .5")
                log(str(close_order))
                isOrderPlaced = False
                time.sleep(2)
            pass

        if change > .5 and  last_signal == 'SHORT' and isOrderPlaced and open_ > entry :
            close_order = close_position(symbol, amount_to_trade , 'buy')
            if close_order:
                log(f"SHORT EXIT on SL {change} > .5")
                log(str(close_order))
                isOrderPlaced = False
                time.sleep(2)
            pass







        if last_signal != 'LONG' and side == 'LONG':

            # exit
            if last_signal and isOrderPlaced: 
                print('Close the short position', amount_to_trade )
                close_order = close_position(symbol, amount_to_trade , 'buy')
                if close_order:
                    log("short closed successfully")
                    log(str(close_order))
                    isOrderPlaced = False
                    trailing = False
                    time.sleep(2)


            # entry
            log("LONG")
            long_order = long(symbol, amount_usdt)
            if long_order:
                log("Long order created successfully:")
                log(str(long_order))
                last_signal = side
            # Calculate the amount of BTC to sell
            amount_to_trade  = long_order['amount']  # Amount to close
            entry = long_order['price']
            isOrderPlaced = True
            pass


        if last_signal != 'SHORT' and side == 'SHORT':

            # exit
            if last_signal and isOrderPlaced: 
                print('Close the long position', amount_to_trade )
                close_order = close_position(symbol, amount_to_trade , 'sell')
                if close_order:
                    log("long closed successfully:")
                    log(str(close_order))
                    isOrderPlaced = False
                    trailing = False
                    time.sleep(2)

            # entry
            log("SHORT")
            short_order = short(symbol, amount_usdt)
            if short_order:
                log("Short order created successfully:")
                log(str(short_order))
                last_signal = side
            amount_to_trade  = short_order['amount']  # Amount to close
            entry = long_order['price']
            isOrderPlaced = True

            pass 
        
        time.sleep(60*5)  # Run every 30 minutes
    
  
if __name__ == "__main__":
    run_bot()
