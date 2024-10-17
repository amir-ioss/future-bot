import ccxt
import time
from datetime import datetime
import json
import math
import logging
from ccxt.base.errors import NetworkError

# from help.utils import encrypt, decrypt 

# Set up the logger to write to log.txt
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(action, details=""):
    """
    Logs CRUD actions with optional details.
    """
    logging.info(f"{action} - {details}")

# CRUD Functions
def log(item):
    log_action("LOG", f"{item}")
    # Your create logic here
    print(item)
    return f"Created {item}"

from plyer import notification
def trigger_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='Scalping Bot',  # Optional, for Linux and macOS
        timeout=10                 # Duration in seconds for the notification to appear
    )

# Initialize your exchange
exchange = ccxt.binance({
    'apiKey': 'h5J8MK5WP5t2DKADpFvOhoE98chuKJxsSB7ny239DWaO49amJmkmzFgus7wEZPpH',
    'secret': 'JEk6zkYmIrwOS1JswoIdPfwndqpfXRsfc00dS4F8rJS6c93qa8PRpLecOpCc8peb',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'  # Use 'spot' for spot trading, 'future' for Futures
    }
})

# Load the JSON file
# with open('2024-03-11.json', 'r') as file:
#     ohlcv_data = json.load(file)


symbol = 'XRP/USDT'
timeframe = '5m'
leverage = 20
amount_usdt = 10 * leverage  # Amount in USDT to spend
minRange = 499



# def fetch_candles(symbol, timeframe):
    # return exchange.fetch_ohlcv(symbol, timeframe, limit=minRange)

def fetch_candles(symbol, timeframe=timeframe, limit=minRange, retries=5, delay=5):
    attempt = 0  # To track the retry attempts
    while attempt < retries:
        try:
            # Try to fetch the OHLCV data
            candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return candles  # If successful, return the data
        except NetworkError as e:
            attempt += 1  # Increment the attempt counter
            print(f"Network error: {e}. Attempt {attempt} of {retries}. Retrying in {delay} seconds...")

            # Wait for the specified delay before retrying
            time.sleep(delay)

    # If all retries fail, return None or a fallback value
    print("Failed to fetch OHLCV data after multiple retries.")
    return None


def check_balance():
    # Fetch balance information
    balance = exchange.fetch_balance()
    
    # Fetch USDT balance in Futures account
    usdt_balance = balance['total'].get('USDT', 0)
    
    return usdt_balance

def long(symbol, amount_usdt):
    # Check balance
    usdt_balance = check_balance()
    log(f'Balance : {usdt_balance}')
    
    # if usdt_balance < amount_usdt:
    #     print(f"Insufficient balance. Available: {usdt_balance} USDT, Required: {amount_usdt} USDT")
    #     return None
    
    # Calculate the amount of BASE to buy based on the current price
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']  # Last price of the symbol
    amount = amount_usdt / price
    
    # Create a market buy order
    order = exchange.create_market_order(symbol, 'buy', amount)
    trigger_notification('LONG', f'{symbol}, buy, {amount}')

    
    return order

def short(symbol, amount_usdt):
    # Check balance
    usdt_balance = check_balance()
    log(f'Balance : {usdt_balance}')

    
    # if usdt_balance < amount_usdt:
    #     print(f"Insufficient balance. Available: {usdt_balance} USDT, Required: {amount_usdt} USDT")
    #     return None
    
    # Calculate the amount of BASE to short based on the current price
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']  # Last price of the symbol
    amount = amount_usdt / price # base currency
    
    # Create a market sell order to open a short position
    order = exchange.create_market_order(symbol, 'sell', amount)
    trigger_notification('SHORT', f'{symbol}, sell, {amount}')

    
    return order

def close_position(symbol, amount, side):
    print("CLOSE AMOUNT:", amount)
    # Create a market order to close the position
    # If side is 'buy', it will close a short position
    # If side is 'sell', it will close a long position
    order = exchange.create_market_order(symbol, side, amount)
    trigger_notification(f'CLOSE {side}', f'{symbol}, {amount}')

    usdt_balance = check_balance()
    log(f'Balance :::::: {usdt_balance}')

    return order



def timestamp_to_HHMM(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000
    
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp_s)
    
    # Format the datetime object to HH:MM
    formatted_time = dt_object.strftime('%H:%M')
    
    return formatted_time



class TradingBot:
    def __init__(self, test=False):
        # self.candles = fetch_candles(symbol, timeframe)
        # candles = ohlcv_data
        # self.opens = [candle[1] for candle in self.candles]
        # self.highs = [candle[2] for candle in self.candles]
        # self.lows = [candle[3] for candle in self.candles]
        # self.closes = [candle[4] for candle in self.candles]
        self.test = test
        
        self.side = None
        self.isOrderPlaced = False
        self.entryPrice = None
        self.sell_amount = 0
        self.targetReach = False
        self.initialTarget = 0
       
        

    # Functions
    def gauss(self, x, h):
        return math.exp(-(math.pow(x, 2) / (h * h * 2)))



    def analyse(self, ohlcv = None):
        candles = fetch_candles(symbol, timeframe)
        # candles = ohlcv_data
        # self.opens = [candle[1] for candle in self.candles]
        # self.highs = [candle[2] for candle in self.candles]
        # self.lows = [candle[3] for candle in self.candles]
        closes = [candle[4] for candle in candles]


        # Input parameters
        h = 8.0
        mult = 3.0
        src = closes
        n = len(src)

        # Functions
        def gauss(x, h):
            return math.exp(-(math.pow(x, 2) / (h * h * 2)))

        # Initialize variables
        nwe = []
        sae = 0.0

        # Compute and set NWE point
        for i in range(min(minRange, n - 1) + 1):
            sum = 0.0
            sumw = 0.0

            # Compute weighted mean
            for j in range(min(minRange, n - 1) + 1):
                w = gauss(i - j, h)
                sum += src[j] * w
                sumw += w

            y2 = sum / sumw
            sae += abs(src[i] - y2)
            nwe.append(y2)

        sae = sae / min(minRange, n - 1) * mult

        def ENTRY(type='LONG'):
            self.isOrderPlaced = True
            self.targetReach = False
            if not self.test:
                new_order = long(symbol, amount_usdt) if type == 'LONG' else short(symbol, amount_usdt)
                if new_order:
                    log(f"{type} order created successfully:")
                    log(str(new_order))
                # Calculate the amount of BTC to sell
                self.sell_amount = new_order['amount']  # Amount to close
                pass # entry 


        def EXIT():
            self.isOrderPlaced = False
            self.targetReach = False
            if not self.test:
                close_order = close_position(symbol, self.sell_amount,  'buy' if self.side == 'SHORT' else 'sell')
                if close_order:
                    log(f"{self.side} closed successfully:")
                    log(str(close_order))
                    time.sleep(2)
                    self.side = None
                pass # exit 
                   
        # Loop to print lines instead of drawing
        for i in range(min(minRange, n - 1) + 1):

            diff = (nwe[i] + sae) - (nwe[i] - sae)
            ch = diff * (25 / 100)  # value + (value * (percentage / 100))
            # ch = diff + (diff * .10) #10%
            t = timestamp_to_HHMM(candles[i][0])
            price = src[i]
            end = True if self.test else i == n-1
            end2 = True if self.test else i == n-2
          
            top = nwe[i] + sae
            bot = nwe[i] - sae
            targetL = top - (ch * .5)
            targetS = bot + (ch * .5)
            isBullish = candles[i-1][1] < candles[i-1][4]


            if self.side == "SHORT" and end and self.isOrderPlaced:
                sl = self.entryPrice + ch
                # TRAILING
                if price < bot or candles[i-1][3] < bot:
                    self.targetReach = True
                    if isBullish:
                        log(f"{t} EXIT WIN {price}")
                        EXIT()
                    pass

                # STOP LOSS
                if price > sl:
                    log(f"{t} EXIT SL {price}")
                    EXIT()
                    pass

                # Target hit
                if (price < targetS or candles[i-1][3] < targetS) and self.isOrderPlaced: self.targetReach = True
                if self.targetReach and price > targetS:
                    log(f"{t} MIN TARGET EXIT SHORT {price}")
                    EXIT()


        
            if self.side == "LONG" and end and self.isOrderPlaced:
                sl = self.entryPrice - ch
                # TRAILING
                if price > top or candles[i-1][2] > top:
                    self.targetReach = True
                    if not isBullish:
                        log(f"{t} EXIT WIN {price}")
                        EXIT()
                    pass

                # STOP LOSS
                if price < sl:
                    log(f"{t} EXIT SL {price}")
                    EXIT()
                    pass

                # Target hit
                if (price > targetL or candles[i-1][2] > targetL) and self.isOrderPlaced: self.targetReach = True
                if self.targetReach and price < targetL:
                    log(f"{t} MIN TARGET EXIT LONG {price}")
                    EXIT()



            if(t == datetime.now().strftime('%H:%M')):
                print(t, end='\r', flush=True) 
                pass


        
            # Check conditions and print labels
            if price > top and i + 1 < n and src[i + 1] < top and end2:        
            # if src[i] > nwe[i] + sae and end2:
                print(datetime.now().strftime('%H:%M'), f"▼ at {t} (open: {price}) {i} n-{n-1}")
                if self.side != "SHORT":
                    # print(self.isOrderPlaced, self.side, self.targetReach)
                    log(f"\n{t} ============ SHORT =============== {price}")
                    self.side = "SHORT"
                    self.entryPrice = price
                    self.initialTarget = top
                    ENTRY("SHORT")


            if price < bot and i + 1 < n and src[i + 1] > bot and end2:        
            # if src[i] < nwe[i] - sae and end2:
                print(datetime.now().strftime('%H:%M'), f"▲ at {t} (open: {price}) {i} n{n-1}")
                if self.side != "LONG":
                    # print(self.isOrderPlaced, self.side, self.targetReach)
                    log(f"\n{t} ============ LONG =============== {price}" )
                    self.side = "LONG"
                    self.entryPrice = price
                    self.initialTarget = bot
                    ENTRY("LONG")


        return self.side, candles[-1]
        # end of analyses



    # R U N
    def run(self):
        # Fetch positions for all symbols
        def get_open_positions(user_exchange, symbol):
            try:
                balance = user_exchange.fetch_balance({'type': 'future'})
                positions = balance['info']['positions']

                # Find the position for the specific symbol
                for position in positions:
                    if position['symbol'] == symbol:
                        if float(position['positionAmt']) != 0:
                            return position
                        else:
                            return None
            except Exception as e:
                print(f"Error: {e}")
                return None


        # Call the function to get open positions
        open_positions = get_open_positions(exchange, symbol)

        # Print the open positions
        if open_positions:
            print(f"Symbol: {open_positions['symbol']}")
            print(f"Position Amount: {open_positions['positionAmt']}")
            print(f"Entry Price: {open_positions['entryPrice']}")
            print(f"Unrealized PnL: {open_positions['unrealizedProfit']}")
            print(f"Leverage: {open_positions['leverage']}")
            print(f"Side: {'Long' if float(open_positions['positionAmt']) > 0 else 'Short'}")
        else:
            print(f"No open position for {symbol}.")


        return
    
        while True:
            this_minute = datetime.today().minute
            abs_num = this_minute/1
            
            if abs_num == round(abs_num):
                self.analyse()
                time.sleep(60)  # 5min ,Run every 15 minutes
                # break;



def main():
    bot = TradingBot(test=False)
    bot.run()


if __name__ == "__main__":
    main()
