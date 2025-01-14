import sys
import os
# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Clear console for Windows or Unix-based systems
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


import ccxt
from ccxt.base.errors import NetworkError
import time
from datetime import datetime
import json
import math
import asyncio
from luxalgo_support_resistance import luxalgo_support_resistance

from config import accounts, symbols, timeframe, leverage, amount_usdt, no_btc_dependent,support_resist_bar_width, from_date
from order import long, short, close_position, check_balance, create_exchange_instances
from help import log, timestamp_to_HHMM, trigger_notification, perc_diff, perc_diff_not_abs, convert_binance_ohlcv_last_time_to_local

# from utils.trv import pivot_low, pivot_high
from db.store import Store, checkInSL  # Use absolute import


# Initialize your exchange
exchange = ccxt.binance({
    # 'apiKey': accounts[0]['api_key'], # master account
    # 'secret': accounts[0]['api_secret'], # master account
    'enableRateLimit': True,
    'options': {
        # 'defaultType': 'future'  # Use 'spot' for spot trading, 'future' for Futures
    }
})

# Load the JSON file
with open('data.json', 'r') as file:
    ohlcv_data = json.load(file)


# def fetch_candles(symbol, timeframe):
    # return exchange.fetch_ohlcv(symbol, timeframe, limit=minRange)



def candles_obj(candles, length):
    time, open_, high, low, close, volume = zip(*candles)
    return {
        "time": time[:length],
        "open": open_[:length],
        "high": high[:length],
        "low": low[:length],
        "close": close[:length],
        "volume": volume[:length],
    }


def fetch_candles(symbol, timeframe='5m', limit=1000, retries=5, delay=5):
    attempt = 0  # To track the retry attempts

    if from_date: since = int(datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    else: since = None

    while attempt < retries:
        try:
            # Try to fetch the OHLCV data
            candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
            return candles  # If successful, return the data
        except NetworkError as e:
            attempt += 1  # Increment the attempt counter
            print(f"Network error: {e}. Attempt {attempt} of {retries}. Retrying in {delay} seconds...")

            # Wait for the specified delay before retrying
            time.sleep(delay)

    # If all retries fail, return None or a fallback value
    print("Failed to fetch OHLCV data after multiple retries.")
    return None

# Define color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"  # Reset color to default




class TradingBot:
    def __init__(self, test=False):
        self.test = test
        self.users = None
        self.active_pair = None

        self.side = None
        self.isOrderPlaced = False
        self.entryPrice = None
        # self.store = Store()
        self.super_tp = 0
        self.super_sl = 0
        self.trailing = False
        self.pnl = 0
        self.sl = None
        self.brakeout = "AWAIT"



    # Functions
    def gauss(self, x, h):
        return math.exp(-(math.pow(x, 2) / (h * h * 2)))



    def analyse(self, symbol):
        candles = fetch_candles(symbol, timeframe)
        # candles = ohlcv_data
        #opens = [candle[1] for candle in candles]
        #highs = [candle[2] for candle in candles]
        #lows = [candle[3] for candle in candles]
        closes = [candle[4] for candle in candles]
        source = [candle[1] for candle in candles]


        # Support & Resist
        # low_pivot, high_pivot, breaks, wick_breaks, osc = luxalgo_support_resistance(candles_obj(candles, len(candles)), left_bars=support_resist_bar_width, right_bars=support_resist_bar_width)
        # low_pivot_30m, high_pivot_30m, breaks, wick_breaks, osc = luxalgo_support_resistance(candles_obj(candles, len(candles)), left_bars=120, right_bars=120)
        # resist_super = high_pivot_30m[-1]
        # support_super = low_pivot_30m[-1]
        # print(F"resist : {resist_30m} support : {support_30m}")



      

        async def ENTRY(type='LONG'):
            self.isOrderPlaced = True
            self.targetReach = False
            self.active_pair = symbol
            if not self.test:
                # Iterate over the accounts and place the long order
                # for account in accounts:
                tasks = []
                for username, user_exchange in self.users:
                    try:
                        # Set leverage if needed (optional)
                        # user_exchange.fapiPrivate_post_leverage({
                        #     'symbol': symbol.replace('/', ''),  # Remove '/' from symbol
                        #     'leverage': leverage
                        # })

                        # Place the long order
                        new_order = long(user_exchange, symbol, amount_usdt) if type == 'LONG' else short(user_exchange, symbol, amount_usdt)
                        tasks.append((username, new_order))
                        # if new_order:
                        #         log(f"Order placed for account {username}:\n{str(new_order)}")
                        #         # Calculate the amount of BTC to sell
                        #         self.sell_amount = new_order['amount']  # Amount to close
                        #         time.sleep(1)
                    except Exception as e:
                        log(f"Error placing order for account {username}: {e}")

                # Run all tasks concurrently
                results = await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
                # Process results
                for (username, _), result in zip(tasks, results):
                    if isinstance(result, Exception):
                        log(f"Error placing order for account {username}: {result}")
                    else:
                        log(f"{self.side} order placed for account {username}:\n{str(result)}")
                        # await asyncio.sleep(1)  # Non-blocking sleep


                trigger_notification(type, f'{symbol}, size: {amount_usdt}* USDT')
                pass # entry


        async def EXIT():
            self.isOrderPlaced = False
            self.super_tp, self.super_sl = 0,0
            self.trailing = False
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
                        # await asyncio.sleep(1)  # Non-blocking sleep



                trigger_notification(f'CLOSE {self.side}', f'{symbol}, {self.sell_amount}')
                self.side = None
                pass # exit

        # Loop to print lines instead of drawing
        for i in range(len(source)):
            if i < 20 : continue

    
            # Support & Resist
            trimmed_candles = candles[max(0, i - 300):i]
            low_pivot, high_pivot, breaks, wick_breaks, osc = luxalgo_support_resistance(candles_obj(trimmed_candles, i), left_bars=support_resist_bar_width, right_bars=support_resist_bar_width)
            resist = high_pivot[-1]
            support = low_pivot[-1]


            # targetL = top - (ch/2)
            # targetS = bot + (ch/2)
            isBullish = candles[i-1][1] < candles[i-1][4]
            price = source[i] # open
            # t = timestamp_to_HHMM(candles[i][0])
            t = convert_binance_ohlcv_last_time_to_local(candles[i][0], local_tz_name="Asia/Kolkata")

            end = len(source)-1 == i 

            # tp = 2 # %
            tp = abs(perc_diff_not_abs(resist, support))/2 # %
            sl = tp*.5  # 50% of tp



            # print(price>resist)
            # if support == 0 or resist == 0 or support_super == 0 or resist_super == 0 : continue
            if support == 0 or resist == 0 : continue

            if end:
                print(t,f"\n\n--- {symbol} --- PNL : ", self.pnl)
            


        
            log  = False
            # if end : print(datetime.now().strftime('%H:%M:%S') , symbol, "targetL:", targetL, "targetS:", targetS,  price, "Trade:",self.isOrderPlaced, "top:", top, "bot:", bot)

            if self.side == "SHORT" and self.isOrderPlaced:
                cur_change = perc_diff_not_abs(self.entryPrice, price)
                # print(cur_change)

                if self.trailing:
                    self.side = None
                    self.isOrderPlaced = False
                    print(t, f"{GREEN}WIN", cur_change, f'\n{RESET}')if log else None
                    self.pnl += abs(cur_change)
                    self.trailing = False

                if cur_change < -tp and self.isOrderPlaced:
                # if cur_change > tp:  # LONG         
                    print("trailing s....")if log else None
                    self.trailing = True

                # if cur_change < -sl: # LONG
                if cur_change > sl:                
                    self.side = None
                    self.isOrderPlaced = False
                    print(t, f"{RED}LOS", cur_change, f'\n{RESET}')if log else None
                    self.pnl -= cur_change
                    self.trailing = False
                    self.sl= "SHORT"
                
                pass



            if self.side == "LONG" and self.isOrderPlaced:
                    cur_change = perc_diff_not_abs(self.entryPrice, price)
                    # print(cur_change)

                    if self.trailing:
                        self.side = None
                        self.isOrderPlaced = False
                        print(t, f"{GREEN}WIN", cur_change, f'\n{RESET}')if log else None
                        self.pnl += cur_change
                        self.trailing = False

                    # if cur_change < -tp:
                    if cur_change > tp and self.isOrderPlaced:  # LONG         
                        print("trailing l....")if log else None
                        self.trailing = True

                    if cur_change < -sl: # LONG
                    # if cur_change > sl:                
                        self.side = None
                        self.isOrderPlaced = False
                        print(t, f"{RED}LOS", cur_change, f'\n{RESET}')if log else None
                        self.pnl += cur_change
                        self.trailing = False
                        self.sl = "LONG"
                    
                    pass



            if not self.isOrderPlaced:
                self.brakeout  = "BULLISH" if price > resist else "BEARISH" if price < support else "AWAIT"
            diff_price = resist-support

            ch_from_resist = perc_diff_not_abs(resist, price)
            # resist_bot = resist - (diff_price*0.25) 
            resist_bot = resist 
            resist_top = resist + (diff_price) 


            if self.brakeout == "BULLISH" and price < resist  and not self.isOrderPlaced :
            # if price > resist_bot and price < resist_top and not self.isOrderPlaced and not isBullish:
            # and not price < resist_super:
                # if price > resist and abs(ch_from_resist) > tp: continue
                # if (price < support or self.sl == "LONG" and price > support):
                self.side =  "LONG"
                self.entryPrice = price
                self.isOrderPlaced = True
                self.trailing = False

                trend = "bullish" if price > resist else "zone"

                print(t, F"{self.side} ENTRY {symbol} brk:{trend} ch_from_resist: {ch_from_resist}")if log else None



            ch_from_support = perc_diff_not_abs(support, price)
            # support_top = support + (diff_price*0.25) 
            support_top = support  
            resist_bot = support - (diff_price) 

            if self.brakeout == "BEARISH" and price > support  and not self.isOrderPlaced:
            # if price < support_top and price > resist_bot and not self.isOrderPlaced and isBullish: 
            # if (price < support or self.sl == "LONG" and price > support):
                # if price < support and abs(ch_from_support) > tp: continue
                # self.side = "SHORT" if self.sl == "LONG" else "LONG" 
                self.side = "SHORT" 
                self.entryPrice = price
                self.isOrderPlaced = True
                self.trailing = False
                self.sl = None

                trend = "bearish" if price < support else "zone"
                print(t, F"{self.side} ENTRY {symbol} brk:{trend} ch_from_support: {ch_from_support}")if log else None


        return self.side, candles[-1]
        # end of analyses


    # R U N
    def run(self):
        for symbol in symbols:
            self.pnl = 0
            self.sl = None
            self.isOrderPlaced = False
            self.trailing = False
            self.analyse(symbol)
            time.sleep(1)
        return

        # Create exchange instances
        self.users = create_exchange_instances(accounts).items()

        while True:

            this_minute = datetime.today().minute
            abs_num = this_minute/1


            if abs_num == round(abs_num):

                if self.isOrderPlaced:
                    side, candle, targetL, targetS = self.analyse(self.active_pair)
                    print(f"\n{datetime.today().strftime('%H:%M')}  min-target: {(targetS if side == 'SHORT' else targetL):.4f} TP:{self.super_tp} SL:{self.super_sl} trailing:{self.trailing} targetReach:{self.targetReach}")
                else:
                    for symbol in symbols:
                        if self.isOrderPlaced:
                            break;
                        self.analyse(symbol)
                        print(f"{datetime.today().strftime('%H:%M')} {symbol}", end='\r', flush=True)
                        time.sleep(2)

                time.sleep(15)  # 5min ,Run every 15 minutes




def main():
    clear_console()
    bot = TradingBot(test=False)
    bot.run()



if __name__ == "__main__":
    main()
