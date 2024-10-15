import sys
import os

# Get the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Add the parent directory to the system path
sys.path.insert(0, parent_dir)
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import ccxt
from datetime import datetime
import asyncio
import pandas as pd
import time

# from bot import TradingBot

# bot = TradingBot()


# with open("../../src/data/ohlcv/2022-01-11.json", "r") as file:
#     # with open('../../src/live.json', 'r') as file:
#     ohlcv_data = json.load(file)
# print("hi", ohlcv_data[:10])



exchange = ccxt.binance({
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
exchange.load_markets()  # Load markets to ensure symbol is correct


def fetch_ohlcv_data(exchange, symbol, start_date, end_date, timeframe='15m'):
    """
    Fetch OHLCV data for a given symbol, timeframe, and date range using ccxt.
    """
    ohlcv_data = []
    since = exchange.parse8601(start_date)
    end_time = exchange.parse8601(end_date)
    
    while since < end_time:
        data = exchange.fetch_ohlcv(symbol, timeframe, since)
        if len(data) == 0:
            break
        
        ohlcv_data += data
        since = data[-1][0] + 15 * 60 * 1000  # Move to the next 15-minute interval in milliseconds
        time.sleep(1)
        pass

    return ohlcv_data[:3200]

def save_ohlcv_data_to_json(ohlcv_data, filename):
    """
    Save OHLCV data to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(ohlcv_data, f, indent=4)

def fetch_and_save_ohlcv_data(symbol='XRP/USDT'):
    # exchange = ccxt.binance()  # You can change the exchange if needed
    year = 2023
    name = symbol.split('/')[0]
    for month in range(1, 13):
        # Set the start and end dates for each month
        start_date = f'{year}-{month:02d}-01T00:00:00Z'
        if month == 12:
            end_date = f'{year+1}-01-01T00:00:00Z'
        else:
            end_date = f'{year}-{month+1:02d}-01T00:00:00Z'
        
        # Fetch the OHLCV data for the month with 15-minute intervals
        ohlcv_data = fetch_ohlcv_data(exchange, symbol, start_date, end_date, timeframe='15m')
        
        # Save the data as a JSON file for the current month
        filename = f'{name.lower()}/{name}_{year}_{month:02d}.json'
        save_ohlcv_data_to_json(ohlcv_data, filename)
        print(f'Saved: {filename}')
        print(start_date, end_date)
        time.sleep(2)


# Call the function to fetch and save the OHLCV data with 15-minute intervals
fetch_and_save_ohlcv_data()


