import numpy as np
import pandas as pd
from contextlib import asynccontextmanager
import ccxt
from datetime import datetime
import asyncio
import pandas as pd
import json
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
# exchange.set_sandbox_mode(True)

def non_num(value, default=0):
    return default if value is None else float(value)

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

# # Generate random data
# close = np.random.random(100)


inputs = {
    "0": "fetch_ohlcv('BTC/USDT', '1m', 300)",
    "1": "paper_trading(paper_trading_node, output['0'], starting_balance=10, position_size=1, fee=0.01)",
    "2": "np.array([non_num(output['0']['open'][i]) > non_num(output['0']['low'][i]) for i in range(len(output['0']['open']))])",
    "3": "np.array([non_num(output['0']['high'][i]) < non_num(output['0']['close'][i]) for i in range(len(output['0']['high']))])",
    "4": "np.logical_and(output['2'], output['3'])"
}

# # Initialize the output dictionary
ohlcv = None
output = {}
results = {}


# Function to resolve dependencies dynamically
def resolve_dependencies(queries):
    inputs = queries.copy()
    # Keep processing until all inputs are resolved
    while inputs:
        for key, formula in list(inputs.items()):
            try:
                if "paper_trading" in formula: 
                    del inputs[key]
                    output[key] = 'paper_trading'
                    continue
                if "-1" in formula: 
                    del inputs[key]
                    continue


                # Attempt to evaluate the formula
                if "->" in formula:
                    expression, keys_str = formula.split("->")
                    print("Expression:", expression.strip())
                    print("Keys:", keys_str.strip())

                    out = {}
                    keys = eval(keys_str.strip())  # Evaluate keys part
                    res = eval(expression.strip())
                    print(res)
                    for i, key_name in enumerate(keys):
                        out[key_name] = res[i]

                    output[key] = out
                else:
                    output[key] = eval(formula)

                if "fetch_ohlcv" in formula: 
                    ohlcv = output[key] 
                 
                del inputs[key]  # Remove resolved item
                print('\n\n\n\n\n==================================')
                print(key, formula)
                # print(output[key])
                break
            except KeyError:
                # Skip if dependencies are not resolved yet
                pass
                
    return output


# Resolve all inputs
# resolve_dependencies(inputs)
# print("---", output['2'])


def paper_trading(signals, ohlcv, starting_balance=10000, position_size=0.1, fee=0.001):
    # 0.1000% fee

    """
    Simulates paper trading based on a boolean array of signals with switching between long and short positions.

    Args:
        signals (list or np.ndarray): Boolean array where True indicates a buy signal, False indicates a sell/short signal.
        ohlcv (dict): Dictionary with keys 'open', 'time', etc., corresponding to OHLCV data.
        starting_balance (float): Initial account balance (default: 10,000).
        position_size (float): Percentage of balance to use per trade (default: 10%).

    Returns:
        dict: Contains final balance and executed trades.
    """
    if len(signals) != len(ohlcv['open']):
        raise ValueError("Length of signals and OHLCV data must match.")
    
    # Initialize variables
    balance = starting_balance
    position = None  # Tracks active position (dictionary for long/short)
    trades = []  # Tracks executed trades
    current_position = None  # "long" or "short"

    for i in range(len(signals)):
        price = ohlcv['open'][i]
        signal = signals[i]
        time = ohlcv['time'][i]

        # Process signal only when there's a switch
        if signal and current_position != "long":  # Switch to long
            if current_position == "short":  # Close short position
                entry_fee = position['quantity'] * position['entry_price'] * fee
                exit_fee = position['quantity'] * price * fee
                pnl_with_fee = (position['entry_price'] - price) * position['quantity'] - entry_fee - exit_fee
                balance += pnl_with_fee
                position['exit_price'] = price
                position['exit_time'] = time
                position['pnl'] = pnl_with_fee
                trades.append(position)
                position = None

            # Open long position
            trade_amount = balance * position_size
            quantity = trade_amount / price
            position = {
                "type": "long",
                "entry_price": price,
                "quantity": quantity,
                "entry_time": time,
                "trade_amount": trade_amount
            }
            current_position = "long"

        elif not signal and current_position != "short":  # Switch to short
            if current_position == "long":  # Close long position
                entry_fee = position['quantity'] * position['entry_price'] * fee
                exit_fee = position['quantity'] * price * fee
                pnl_with_fee = (price - position['entry_price']) * position['quantity'] - entry_fee - exit_fee
                balance += pnl_with_fee
                position['exit_price'] = price
                position['exit_time'] = time
                position['pnl'] = pnl_with_fee
                trades.append(position)
                position = None


            # Open short position
            trade_amount = balance * position_size
            quantity = trade_amount / price
            position = {
                "type": "short",
                "entry_price": price,
                "quantity": quantity,
                "entry_time": time,
                "trade_amount": trade_amount
            }
            current_position = "short"

    # Close remaining positions at the end of the loop
    if position:
        final_price = ohlcv['open'][-1]
        final_time = ohlcv['time'][-1]
        if current_position == "long":
            pnl = position['quantity'] * (final_price - position['entry_price'])
            balance += pnl
        elif current_position == "short":
            pnl = position['quantity'] * (position['entry_price'] - final_price)
            balance += pnl

        position['exit_price'] = final_price
        position['exit_time'] = final_time
        position['pnl'] = pnl
        trades.append(position)

    return {
        "final_balance": balance,
        "trades": trades
    }


# ohlcv = output['0']
# signals = output['2']
# fee = 0.001  # 0.1000% fee

# result = paper_trading(signals, ohlcv, starting_balance=10, position_size=1, fee=fee)

# print("Trades:", len(result["trades"]))
# for trade in result["trades"]:
#     change = ((trade['exit_price'] - trade['entry_price']) / trade['entry_price']) * 100
#     print(f"{trade['pnl']:.2f}, {change:.2f}%")

# print("Final Balance:", result["final_balance"])


# LIVE

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from fastapi.responses import JSONResponse

import math
# Initialize FastAPI app
app = FastAPI()

# List of allowed origins (you can add more if needed)
origins = [
    "http://localhost:3001",  # Your React app's address
    "http://127.0.0.1:3001",  # Another common address for local React app
]

# Add CORSMiddleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins listed in the `origins` list
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Your FastAPI endpoint and other code here
class DynamicData(BaseModel):
    data: Dict[str, str]


def make_serializable(obj):
    """Convert non-serializable types to JSON serializable, including handling NaN, Inf, -Inf, and ndarray."""
    if isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        # Convert numpy arrays to lists
        return obj.tolist()
    elif isinstance(obj, (np.int64, np.float64, np.bool_)):
        # Convert numpy types to native Python types
        return obj.item()
    elif isinstance(obj, float):
        # Check for NaN, Inf, -Inf and handle accordingly
        if math.isinf(obj) or math.isnan(obj):
            return None  # or you could use 'NaN' or 'Infinity' as a string
    return obj



def process(query):
    response = {}
    # output = resolve_dependencies(dynamic_data.data)
    output = resolve_dependencies(query)


    # Convert the nested object to a JSON serializable format
    serializable_obj = make_serializable(output)

    # Convert to JSON string for API response
    json_response = json.dumps(serializable_obj, indent=4)
    
    response['query'] = query
    response['outputs'] = json_response.replace("NaN", 'null')

    _, last = list(query.items())[-1]
    
    if 'paper_trading' in last:
        # result = paper_trading(output['3'], output['1'], starting_balance=10, position_size=1, fee=0.001)
        result = eval(last)
        # print(result)

        # print("Trades:", len(result["trades"]))
        # for trade in result["trades"]:
        #     change = ((trade['exit_price'] - trade['entry_price']) / trade['entry_price']) * 100
        #     print(f"{trade['pnl']:.2f}, {change:.2f}%")

        # print("Final Balance:", result["final_balance"])

        response['result'] = make_serializable(result)

    return response


@app.post("/process/")
async def receive_data(dynamic_data: DynamicData):
   
    try:
       response = process(dynamic_data.data)

    except KeyError as e:
        # Handle missing keys or invalid access in `data`
        raise HTTPException(status_code=400, detail=f"KeyError: {str(e)}")
    except TypeError as e:
        # Handle type issues, such as unexpected data types
        raise HTTPException(status_code=400, detail=f"TypeError: {str(e)}")
    except Exception as e:
        # Handle any other unanticipated exceptions
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


    return response

_inputs = {
    "0": "fetch_ohlcv('BTC/USDT', '1m', 10)",
    "1":"talib.WCLPRICE(output['0']['high'], output['0']['low'], output['0']['close'])"
    # "2": "np.array([non_num(output['0']['open'][i]) > non_num(output['0']['low'][i]) for i in range(len(output['0']['open']))])",
    # "4": "np.logical_and(output['2'], output['3'])",
    # "5": "talib.SAM(output['0']['open'])"
}

# res = process(_inputs)
# res = resolve_dependencies(_inputs)
# print(res['1'])

# def test():
#     output = {
#         '0': {'close': [None, 5, 6]},
#         '1': '1.1'
#     }

#     result = [non_num(output['0']['close'][i]) * non_num(output['1']) for i in range(len(output['0']['close']))]
#     print(result)

# test()




# uvicorn app:app --reload

# lsof -i :8000
# kill -9