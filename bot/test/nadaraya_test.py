import ccxt
import time
from datetime import datetime
import json
import math
import logging
from ccxt.base.errors import NetworkError

from config import accounts, symbols, timeframe, leverage, amount_usdt 



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
    'apiKey': accounts[0]['api_key'], # master account
    'secret': accounts[0]['api_secret'], # master account
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'  # Use 'spot' for spot trading, 'future' for Futures
    }
})

# Load the JSON file
# with open('2024-03-11.json', 'r') as file:
#     ohlcv_data = json.load(file)

# symbol = 'XRP/USDT'
# leverage = 10
# amount_usdt = 3 * leverage  # Amount in USDT to spend
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


def check_balance(user_exchange):
    """
    Function to check USDT balance.
    """
    balance = user_exchange.fetch_balance()
    return balance['total']['USDT']

def create_exchange_instances(accounts):
    """
    Create and store ccxt Binance futures exchange instances for all accounts.
    """
    exchange_instances = {}
    
    for account in accounts:
        _exchange = ccxt.binance({
            'apiKey': account['api_key'],
            'secret': account['api_secret'],
            'options': {
                'defaultType': 'future',  # Futures mode
            }
        })
        exchange_instances[account['username']] = _exchange
    
    return exchange_instances




def long(user_exchange, symbol, amount_usdt):
    # Check balance
    usdt_balance = check_balance(user_exchange)
    log(f'Balance : {usdt_balance}')
    
    if usdt_balance < (amount_usdt/leverage):
        log(f"Insufficient balance. Available: {usdt_balance} USDT, Required: {amount_usdt} USDT")
        return None
    
    # Calculate the amount of BASE to buy based on the current price
    ticker = user_exchange.fetch_ticker(symbol)
    price = ticker['last']  # Last price of the symbol
    amount = amount_usdt / price
    
    # Create a market buy order
    order = user_exchange.create_market_order(symbol, 'buy', amount)

    
    return order

def short(user_exchange, symbol, amount_usdt):
    # Check balance
    usdt_balance = check_balance(user_exchange)
    log(f'Balance : {usdt_balance}')

    if usdt_balance < (amount_usdt/leverage):
        log(f"Insufficient balance. Available: {usdt_balance} USDT, Required: {amount_usdt} USDT")
        return None
    
    # Calculate the amount of BASE to short based on the current price
    ticker = user_exchange.fetch_ticker(symbol)
    price = ticker['last']  # Last price of the symbol
    amount = amount_usdt / price # base currency
    
    # Create a market sell order to open a short position
    order = user_exchange.create_market_order(symbol, 'sell', amount)


    return order

    
def close_position(user_exchange, symbol, amount, side):
    # Create a market order to close the position
    # If side is 'buy', it will close a short position
    # If side is 'sell', it will close a long position
    order = user_exchange.create_market_order(symbol, side, amount)

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
        self.users = None
        self.active_pair = None
        
        self.side = None
        self.isOrderPlaced = False
        self.entryPrice = None
        self.sell_amount = 0
        self.targetReach = False
        self.initialTarget = 0
       
        

    # Functions
    def gauss(self, x, h):
        return math.exp(-(math.pow(x, 2) / (h * h * 2)))



    def analyse(self, symbol):
        candles = fetch_candles(symbol, timeframe)
        # candles = ohlcv_data
        # self.opens = [candle[1] for candle in self.candles]
        # self.highs = [candle[2] for candle in self.candles]
        # self.lows = [candle[3] for candle in self.candles]
        closes = [candle[4] for candle in candles]


        # Input parameters
        h = 8.0
        mult = 3 #3.0
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
            self.active_pair = symbol
            if not self.test:
                # Iterate over the accounts and place the long order
                # for account in accounts:
                for username, user_exchange in self.users:
                    try:
                        # Set leverage if needed (optional)
                        # user_exchange.fapiPrivate_post_leverage({
                        #     'symbol': symbol.replace('/', ''),  # Remove '/' from symbol
                        #     'leverage': 20
                        # })

                        # Place the long order
                        new_order = long(user_exchange, symbol, amount_usdt) if type == 'LONG' else short(user_exchange, symbol, amount_usdt)
                        if new_order:
                                log(f"Order placed for account {username}:\n{str(new_order)}")
                                # Calculate the amount of BTC to sell
                                self.sell_amount = new_order['amount']  # Amount to close
                                time.sleep(1)
                    except Exception as e:
                        log(f"Error placing order for account {username}: {e}")
                trigger_notification(type, f'{symbol}, size: {amount_usdt}* USDT')
                pass # entry 


        def EXIT():
            self.isOrderPlaced = False
            self.targetReach = False
            self.active_pair = None

            if not self.test:
                for username, user_exchange in self.users:
                    try:
                        close_order = close_position(user_exchange, symbol, self.sell_amount,  'buy' if self.side == 'SHORT' else 'sell')
                        if close_order:
                                log(f"{self.side} closed successfully for account {username}:\n{str(close_order)}")
                                time.sleep(1)
                    except Exception as e:
                        log(f"Error closing order for account {username}: {e}")
                trigger_notification(f'CLOSE {self.side}', f'{symbol}, {self.sell_amount}')
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
                    log(f"\n{t} ============ {symbol} SHORT =============== {price}")
                    self.side = "SHORT"
                    self.entryPrice = price
                    self.initialTarget = top
                    ENTRY("SHORT")


            if price < bot and i + 1 < n and src[i + 1] > bot and end2:        
            # if src[i] < nwe[i] - sae and end2:
                print(datetime.now().strftime('%H:%M'), f"▲ at {t} (open: {price}) {i} n{n-1}")
                if self.side != "LONG":
                    # print(self.isOrderPlaced, self.side, self.targetReach)
                    log(f"\n{t} ============ {symbol} LONG =============== {price}" )
                    self.side = "LONG"
                    self.entryPrice = price
                    self.initialTarget = bot
                    ENTRY("LONG")


        return self.side, candles[-1]
        # end of analyses



    # R U N
    def run(self):
        # Create exchange instances
        self.users = create_exchange_instances(accounts).items()

        while True:
            this_minute = datetime.today().minute
            abs_num = this_minute/1
            
            if abs_num == round(abs_num):

                if self.isOrderPlaced:
                    self.analyse(self.active_pair)

                else:
                    for symbol in symbols:
                        if self.isOrderPlaced:
                            break;
                        print(symbol, end='\r\n', flush=True) 
                        self.analyse(symbol)
                        time.sleep(2) 
                
                time.sleep(60)  # 5min ,Run every 15 minutes
                



def main():
    bot = TradingBot(test=False)
    bot.run()


if __name__ == "__main__":
    main()
