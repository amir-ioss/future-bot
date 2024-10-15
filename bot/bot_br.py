import ccxt
from datetime import datetime
import asyncio
import pandas as pd
import json
import config
from help.utils import percentage_difference, is_saturday, is_between_saturday_sunday_noon
# Load the JSON file
# with open('test/btc/BTC_2023_07.json', 'r') as file:
with open('test/xrp/XRP_2023_01.json', 'r') as file:
    ohlcv_data = json.load(file)

from help.trv import pivot_high, pivot_low

class TradingBot:
    def __init__(self, symbol='XRP/USDT', live = False):
        if live :
            self.exchange = ccxt.binance({
                # 'apiKey': api_key,
                # 'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'  # Use futures market type
                },
                'urls': {
                    'api': {
                        'public': 'https://testnet.binancefuture.com/fapi/v1',
                        'private': 'https://testnet.binancefuture.com/fapi/v1',
                    }
                }
            })
            self.exchange.load_markets()  # Load markets to ensure symbol is correct
            pass

        self.symbol = symbol
        self.timeframe = '15m'
        self.candles = []
        self.resists = [{}] #view
        self.supports = [{}] #view
        self.strong_resists = [{}] #view
        self.strong_supports = [{}] #view
        self.l_points = []
        self.h_points = []
        self.hl = 0
        self.lh = 0
        self.strong_support = None
        self.strong_resist = None
        self.position_temp = {}
        self.positions = []
        self.current_trade = None
        self.marks = [] #view
        self.text = [] #view
        self.breakout = 'await'
        self.isOrderPlaced = False
        self.breakouts = []
        self.trailing = False
        self.live = live


    def fetch_candles(self, candles = None):
        # Fetch OHLCV data
        if candles:
                    self.candles = candles
        elif self.live :
            # Set your symbol, timeframe, and total desired number of candles
            timeframe = '15m'  # Replace with your desired timeframe
            total_candles = 3200  # Total number of candles you want to fetch
            # Fetching in chunks
            all_candles = []  # This will store all the candles
            since_date = '2024-06-01T00:00:00Z'  # Input your start date in ISO format
            since = self.exchange.parse8601(since_date)

            while True:
                # Fetch a batch of candles from the since date
                candles = self.exchange.fetch_ohlcv(self.symbol, timeframe, since=since, limit=1000)

                # Break the loop if no candles are returned (end of data)
                if not candles:
                    break

                # Append the fetched candles to the list
                all_candles.extend(candles)

                # Update the since date to the timestamp of the last candle fetched + 1 millisecond
                since = candles[-1][0] + 1
                    # Avoid fetching more than needed
                if len(all_candles) >= total_candles:
                    break

                asyncio.sleep(1)
            self.candles = all_candles
            # # print(len(self.candles))
        else:
            # self.candles = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=1000)
            # self.candles = ohlcv_data[:1100]
            # self.candles = ohlcv_data[1100:(1100*2)]
            # self.candles = ohlcv_data[(1100*2):]
            self.candles = ohlcv_data

     
        # Unpack the OHLCV data into separate lists
        self.times, self.opens, self.highs, self.lows, self.closes, self.volumes = zip(*self.candles)
        # Convert them back to lists, if necessary (as zip returns tuples)
        self.times = list(self.times)
        self.opens = list(self.opens)
        # self.highs = list(self.highs)
        # self.lows = list(self.lows)
        self.closes = list(self.closes)
        # self.volumes = list(self.volumes)
        return self.candles


    def check_trade_signal(self, test = False):
        self.h_points = pivot_high(self.closes, config.period, config.period)
        self.l_points = pivot_low(self.closes, config.period, config.period)
        hl_top = 0
        hl_bot = 0
        lh_top = 0
        lh_bot = 0
        rangeStart = 0
        topEdge = 0
        bottomEdge = 0
        hls_keys = []
        lhs_keys = []
        hls_keys_range = []
        lhs_keys_range = []

        MForm = False
   

        for index, cand in enumerate(self.candles):
            # print(f"Index: {index}, cand: {cand}")
            self.breakouts.append(self.breakout)

            if index < config.period : continue
            end = index == len(self.candles)-1
            delay_index = max(1, index - config.period)

       
            
            # Member functions
            def resist(price):
                # change = percentage_difference(price, self.lh)
                # if abs(change) < 1: return
                self.hl = price # update 
                height = self.hl - self.lh
               
                hl_top = price + (height * config.s_r_tolerance / 100) if self.hl is not None else None
                hl_bot = price - (height * config.s_r_tolerance / 100) if self.hl is not None else None
                self.resists[-1]["end_index"] = index
                self.resists.append({"price": price, "start_index": index, "hl_top": hl_top, "hl_bot": hl_bot, "breakout": self.breakout})
                return hl_top, hl_bot
            
            def support(price):
                # change = percentage_difference(self.hl,price)
                # if abs(change) < 1: return
                self.lh = price # update 
                height = self.hl - self.lh   

                lh_top = price + (height * config.s_r_tolerance / 100) if self.lh is not None else None
                lh_bot = price - (height * config.s_r_tolerance / 100) if self.lh is not None else None
                self.supports[-1]["end_index"] = index
                self.supports.append({"price": price, "start_index": index, "lh_top": lh_top, "lh_bot": lh_bot, "breakout": self.breakout})
                return lh_top, lh_bot
            
            def ENTRY(type='LONG'):
                if self.isOrderPlaced: return
                self.isOrderPlaced = True
                self.position_temp = {"entryPrice": cand[1], "startTime": cand[0], "startIndex": index, "type": type}
                self.positions.append({"entryPrice": cand[1], "startTime": cand[0], "startIndex": index, "type": type})
                pass

            def EXIT(msg = None, exitPrice = cand[1]):
                if not self.isOrderPlaced: return
                self.positions[-1]["exitPrice"] = exitPrice 
                self.positions[-1]["endIndex"] = index
                self.isOrderPlaced = False
                if msg : self.text.append({"index": index, "price": cand[1], 'text': msg, 'color': '#fff'})
                pass


            # HIGHS
            hls = self.h_points[:delay_index]
            # hls_keys = [x for x in hls if x != '']
            if hls[-1]: 
                hls_keys.append(hls[-1])
                hls_keys_range.append(hls[-1])
                hl_top, hl_bot = resist(hls[-1])
                # if self.breakout != 'await' : lh_top, lh_bot = support(self.lh) #update box

                # STRONG RESIST
                related_highs = [x for x in hls_keys[-6:] if x < hl_top and x > hl_bot]
                # avg_highs = [value for value in hls_keys if abs(((value - hls[-1]) / hls[-1]) * 100) < (range_change/2)]
                if len(related_highs) > 1:
                    self.strong_resists[-1]["end_index"] = index
                    self.strong_resists.append({"price": max(hls_keys[-6:]), "start_index": index, "top": hl_top, "bot": hl_bot})
                    self.strong_resist = max(hls_keys[-6:]) #hls[-1]
                    pass #end


            
            # LOWS
            lhs = self.l_points[:delay_index]
            # lhs_keys = [x for x in lhs if x != '']
            if lhs[-1]: 
                lhs_keys.append(lhs[-1])
                lhs_keys_range.append(lhs[-1])
                lh_top, lh_bot = support(lhs[-1])
                # if self.breakout != 'await' : hl_top, hl_bot = resist(self.hl) #update box

                # STRONG SUPPORT
                related_lows = [x for x in lhs_keys[-6:] if x < lh_top and  x > lh_bot]
                # if index < 325 : print(index, hls)
                range_change = abs(percentage_difference(lhs[-1], self.strong_resist if self.strong_resist else max(lhs_keys)))
                # range_change = abs(percentage_difference(lhs[-1], hls[-1]))
                avg_lows = [value for value in lhs_keys[-6:] if abs(((value - lhs[-1]) / lhs[-1]) * 100) < (range_change/2)]
                if index > 550  and index < 640:
                    print(index, avg_lows, min(avg_lows))
                
                # support = min(avg_lows) if avg_lows else lhs[-1]
                support_ = min(lhs_keys[-6:]) # lhs[-1]
                print("support:", support)

                if len(related_lows) > 1:
                    self.strong_supports[-1]["end_index"] = index
                    self.strong_supports.append({"price": support_, "start_index": index, "top": lh_top, "bot": lh_bot })
                    self.strong_support = support_
                    pass #end




                
            if len(self.supports) < 1 or len(self.resists) < 1 or hl_top == None or hl_bot == None or lh_top == None or lh_bot == None or len(hls_keys) < 3 or len(lhs_keys) < 3: continue;
            
            # height = self.hl - self.lh 
            height = hls_keys[-1] - lhs_keys[-1] if hls_keys and lhs_keys else  self.hl - self.lh 
            hl_range = [x for x in self.resists if 'start_index' in x and x['start_index'] > rangeStart]
            lh_range = [x for x in self.supports if 'start_index' in x and x['start_index'] > rangeStart]


            # if index > 200 and index < 260: print(index, self.strong_resist)
            

#   . . . . . . . . . . . . . . . . . .    B U L L I S H    . . . . . . . . . . . . . . . . . . 

            if cand[1] > hl_top and len(hls_keys) > 0 and len(lhs_keys) > 0 and self.breakout == 'await':
                if self.strong_resist and cand[1] > self.strong_resist:
                    self.breakout = 'bullish'
                    self.marks.append({"index": index, "price": cand[1], 'mark': 'bullish'})
                    ENTRY()
                    if self.hl < self.strong_resist:
                        resist(self.strong_resist)

                    rangeStart = index
                    topEdge = cand[1]
                    MForm = False
                    hls_keys_range.clear()
                    lhs_keys_range.clear()
                    self.trailing = False
                    continue;

            # analyse  
            if self.breakout == 'bullish':
                topEdge = cand[1] if cand[1] > topEdge else topEdge 
                lhs_keys_range_ = [x for x in lhs_keys_range if x > self.strong_resist]
                bearish_cand = cand[1] < self.candles[index-2][4] 
                change = percentage_difference(self.position_temp['entryPrice'], cand[1])


                def make_strong_support():
                    self.strong_supports[-1]["end_index"] = index
                    self.strong_supports.append({"price": self.lh, "start_index": index, "top": lh_top, "bot": lh_bot})
                    self.strong_support = self.lh

                    self.strong_resists[-1]["end_index"] = index
                    self.strong_resists.append({"price": self.hl, "start_index": index, "top": hl_top, "bot": hl_bot})
                    self.strong_resist = self.hl



                # swap last resist to support 
                if hls[-1] and self.resists[-1]['price'] > self.resists[-2]['price']:
                    lh_top, lh_bot = support(self.resists[-2]['price'])


                # level 1
                # reverse
                if len(lh_range) == 0 and cand[1] < hl_bot and self.position_temp['entryPrice'] > cand[1]: # if failed breakout
                    self.breakout = 'await'
                    # self.text.append({"index": index, "price": cand[1], 'text': 'EXIT', 'color': '#fff'})
                    EXIT('exit reverse') #EXIT(hl_bot)
                    pass


                # level n
                if len(lh_range) > 0 and cand[1] < lh_bot and bearish_cand:
                    EXIT('exit lvls')
                    self.breakout = 'await'
                    if self.position_temp['entryPrice'] < cand[1]: #if success breakout
                        hl_top, hl_bot = resist(topEdge)
                        lh_top, lh_bot = support(self.lh) 
                        make_strong_support()
                        pass 

                
                # MForm
                if len(lhs_keys_range_) > 0 and change:
                    if cand[1] > hl_bot: MForm = True
                    if cand[1] > hl_top: MForm = False

                    # if MForm and cand[1] < hl_top and bearish_cand:
                    if MForm and self.candles[index-2][4] < hl_bot and self.candles[index-2][1] > hl_bot and cand[1] < hl_top:
                        EXIT('M Form exit')
                        self.breakout = 'await'
                        make_strong_support()
                        pass 


                # Trailing
                if self.strong_support and self.strong_resist:
                    # range_change = percentage_difference(self.lh, self.hl)
                    range_change = abs(percentage_difference(self.strong_support, self.strong_resist))
                    range_change = range_change if range_change > 1 else 1
                    if change > range_change and len(lhs_keys_range_) == 0: self.trailing = True
                    if self.trailing:
                        trailing_change = percentage_difference(cand[1], topEdge)
                        if trailing_change > range_change/2: EXIT('Trailing')
                        pass
                
                # reduce loss
                if -.5 > change:
                    EXIT('reduce loss .5%')
                    # hl_top, hl_bot = resist(topEdge)
                    pass



                    

          



#   . . . . . . . . . . . . . . . . .    B E A R I S H    . . . . . . . . . . . . . . . . . . 

            if cand[1] < lh_bot and len(hls_keys) > 0 and len(lhs_keys) > 0 and self.breakout == 'await':
                if self.strong_support and cand[1] < self.strong_support:
                    self.breakout = 'bearish'
                    self.marks.append({"index": index, "price": cand[1], 'mark': 'bearish'})
                    # print(index, hl_top, hl_bot, lh_top, lh_bot)
                    ENTRY('SHORT')
                    if self.lh > self.strong_support:
                        support(self.strong_support)

                    rangeStart = index
                    bottomEdge = cand[1]
                    MForm = False
                    hls_keys_range.clear()
                    lhs_keys_range.clear()
                    self.trailing = False
                    continue;
            
            # analyse  
            if self.breakout == 'bearish':
                bottomEdge = cand[1] if cand[1] < bottomEdge else bottomEdge
                hls_keys_range_ = [x for x in lhs_keys_range if x < self.strong_support]
                bearish_cand = cand[1] < self.candles[index-2][4] 
                change = percentage_difference(self.position_temp['entryPrice'], cand[1])


                def make_strong_resist():
                    self.strong_resists[-1]["end_index"] = index
                    self.strong_resists.append({"price": self.hl, "start_index": index, "top": hl_top, "bot": hl_bot})
                    self.strong_resist = self.hl

                    self.strong_supports[-1]["end_index"] = index
                    self.strong_supports.append({"price": self.lh, "start_index": index, "top": lh_top, "bot": lh_bot})
                    self.strong_support = self.lh



                # swap last support to resist 
                if lhs[-1] and self.supports[-1]['price'] < self.supports[-2]['price']:
                    hl_top, hl_bot = resist(self.supports[-2]['price'])

                # level 1
                # reverse
                if len(hl_range) == 0 and cand[1] > lh_top and self.position_temp['entryPrice'] < cand[1]:
                        self.breakout = 'await'
                        self.text.append({"index": index, "price": cand[1], 'text': 'reverse', 'color': 'yellow'})
                        EXIT()
                        lh_top, lh_bot = support(bottomEdge)
                        self.strong_supports[-1]["end_index"] = index
                        self.strong_supports.append({"price": bottomEdge, "start_index": index, "top": lh_top, "bot": lh_bot})
                        self.strong_support = bottomEdge
                        pass   
                
                # level n
                if len(hl_range) > 0 and cand[1] > hl_top:
                    EXIT('exit s lvls')
                    self.breakout = 'await'
                    # self.text.append({"index": index, "price": cand[3], 'text': 'creates', 'color': '#fff'})
                    if self.position_temp['entryPrice'] < cand[1]: #if success breakout
                        hl_top, hl_bot = resist(self.resists[-2]['price'])
                        lh_top, lh_bot = support(bottomEdge)
                        make_strong_resist()
              
                
                # MForm
                if len(hls_keys_range_) > 0 :
                    if cand[1] < lh_bot: MForm = True
                    if cand[1] < lh_top: MForm = False

                    # if MForm and cand[1] > lh_top and bearish_cand: 
                    if MForm and self.candles[index-2][4] > lh_top and self.candles[index-2][1] < lh_top and cand[1] > lh_top :
                        EXIT('M Form exit')
                        self.breakout = 'await'
                        make_strong_resist()
                    pass 

                # if index > 300 and index < 375:
                #     print(index, len(hls_keys_range_)) 

                # Trailing
                if self.strong_support and self.strong_resist:
                    # range_change = abs(percentage_difference(self.lh, self.hl))
                    range_change = abs(percentage_difference(self.strong_support, self.strong_resist))
                    range_change = range_change if range_change > 1 else 1
                    if -range_change > change and len(hls_keys_range_) == 0: self.trailing = True
                    if self.trailing:
                        trailing_change = percentage_difference(bottomEdge, cand[1])
                        if trailing_change > range_change/2: EXIT(f'Trailing {trailing_change:.2f}, {(range_change / 2):.2f}')
                        pass

                        
                if self.isOrderPlaced == False and self.positions[-1]['entryPrice'] > cand[1] and cand[1] < lh_bot:
                    self.trailing = False
                    ENTRY('SHORT')
                    pass

                           
                # reduce loss
                if change > .5:
                    EXIT('reduce loss .5%')
                    # lh_top, lh_bot = support(bottomEdge)
                    pass




                
            # print(self.resists)
            if end and test: 
                if self.position_temp['type'] == 'LONG': EXIT('test exit', lh_top)
                if self.position_temp['type'] == 'SHORT': EXIT('test exit', hl_top)
            pass # end loop

   

    async def run(self, test = False, ohlcv = None):
        if test :
            self.fetch_candles(ohlcv)
            self.check_trade_signal(test)
        else :
            while True:
                self.fetch_candles()
                self.check_trade_signal()
                # self.h_points = pivot_high(pd.DataFrame(self.highs))
                await asyncio.sleep(900)  # 15 minutes
