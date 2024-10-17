import ccxt
from ccxt.base.errors import NetworkError
import time
from datetime import datetime
import json
import math
import logging
import asyncio
import pytz
from order import get_position 


from config import accounts, symbols, timeframe, leverage, amount_usdt 
from order import long, short, close_position, check_balance, create_exchange_instances
from help import log, timestamp_to_HHMM, trigger_notification


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






class TradingBot:
    def __init__(self, test=False):
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
                        #     'leverage': leverage
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


        async def EXIT():
            self.isOrderPlaced = False
            self.targetReach = False
            self.active_pair = None

            tasks = []
            if not self.test:
               
                for username, user_exchange in self.users:
                    try:
                        task = close_position(user_exchange, symbol, 'buy' if self.side == 'SHORT' else 'sell')
                        tasks.append((username, task))  # Keep track of username for logging
                    except Exception as e:
                        log(f"Error closing order for account {username}: {e}")
                
                # Run all tasks concurrently
                results = await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
                # Process results
                for (username, _), result in zip(tasks, results):
                    if isinstance(result, Exception):
                        log(f"Error closing order for account {username}: {result}")
                    else:
                        log(f"{self.side} closed successfully for account {username}:\n{str(result)}")
                        await asyncio.sleep(1)  # Non-blocking sleep

               
               
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
                        asyncio.run(EXIT())
                    pass

                # STOP LOSS
                if price > sl:
                    log(f"{t} EXIT SL {price}")
                    asyncio.run(EXIT())
                    pass

                # Target hit
                if (price < targetS or candles[i-1][3] < targetS) and self.isOrderPlaced: self.targetReach = True
                if self.targetReach and price > targetS:
                    log(f"{t} MIN TARGET EXIT SHORT {price}")
                    asyncio.run(EXIT())


        
            if self.side == "LONG" and end and self.isOrderPlaced:
                sl = self.entryPrice - ch
                # TRAILING
                if price > top or candles[i-1][2] > top:
                    self.targetReach = True
                    if not isBullish:
                        log(f"{t} EXIT WIN {price}")
                        asyncio.run(EXIT())
                    pass

                # STOP LOSS
                if price < sl:
                    log(f"{t} EXIT SL {price}")
                    asyncio.run(EXIT())
                    pass

                # Target hit
                if (price > targetL or candles[i-1][2] > targetL) and self.isOrderPlaced: self.targetReach = True
                if self.targetReach and price < targetL:
                    log(f"{t} MIN TARGET EXIT LONG {price}")
                    asyncio.run(EXIT())



            # if(t == datetime.now().strftime('%H:%M')):
            #     print(t, end='\r', flush=True) 
            #     pass


        
            # Check conditions and print labels
            if price > top and i + 1 < n and src[i + 1] < top and end2:        
            # if src[i] > nwe[i] + sae and end2:
                print(datetime.now().strftime('%H:%M'), f"▼ at {t} (open: {price}) {i} n-{n-1}")
                if self.side != "SHORT":
                    # print(self.isOrderPlaced, self.side, self.targetReach)
                    log(f"\n\n\n\n\n{t} ============ {symbol} SHORT =============== {price}")
                    self.side = "SHORT"
                    self.entryPrice = price
                    self.initialTarget = top
                    ENTRY("SHORT")


            if price < bot and i + 1 < n and src[i + 1] > bot and end2:        
            # if src[i] < nwe[i] - sae and end2:
                print(datetime.now().strftime('%H:%M'), f"▲ at {t} (open: {price}) {i} n{n-1}")
                if self.side != "LONG":
                    # print(self.isOrderPlaced, self.side, self.targetReach)
                    log(f"\n\n\n\n\n{t} ============ {symbol} LONG =============== {price}" )
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
                        print(datetime.today().strftime('%H:%M') + ' ' + symbol, end='\r', flush=True)
                        self.analyse(symbol)
                        time.sleep(2) 
                
                time.sleep(60)  # 5min ,Run every 15 minutes
            
            



def main():
    bot = TradingBot(test=False)
    bot.run()

if __name__ == "__main__":
    main()
