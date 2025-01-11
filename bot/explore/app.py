import numpy as np
import pandas as pd
from contextlib import asynccontextmanager
import ccxt
from datetime import datetime
import asyncio
import pandas as pd
import talib
import ccxt
from paper import paper_trading
from order_block import find_order_blocks, find_order_blocks2
from support_resistance import support_resistance, support_resistance_levels
from luxalgo_support_resistance import luxalgo_support_resistance
from utils import offset_index
import json
with open('data.json', 'r') as file:
    mock_data = json.load(file)

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


def fetch_ohlcv(symbol="BTC/USDT", timeframe="1m", limit=1000):
    # ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    ohlcv = mock_data[:limit]

    # Convert to NumPy array and split into separate arrays
    ohlcv_np = np.array(ohlcv, dtype=np.float64)
    
    # Split columns directly for improved performance
    time, open_, high, low, close, volume = ohlcv_np.T
    
    return time, open_, high, low, close, volume


# # Generate random data
# close = np.random.random(100)


inputs = {
    # "0": "fetch_ohlcv('BTC/USDT', '1m', 300)",
    # "1": "paper_trading(paper_trading_node, output['0'], starting_balance=10, position_size=1, fee=0.01)",
    # "2": "np.array([non_num(output['0']['open'][i]) > non_num(output['0']['low'][i]) for i in range(len(output['0']['open']))])",
    # "3": "np.array([non_num(output['0']['high'][i]) < non_num(output['0']['close'][i]) for i in range(len(output['0']['high']))])",
    # "4": "np.logical_and(output['2'], output['3'])",
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
            print("keykeykeykeykey", key)
            try:
                if "paper_trading" in formula:
                    del inputs[key]
                    output[key] = "paper_trading"
                    continue
                # if "-1" in formula:
                #     del inputs[key]
                #     continue

                # Attempt to evaluate the formula
                if "->" in formula:
                    expression, keys_str = formula.split("->")
                    print("Expression:", expression.strip())
                    print("Keys:", keys_str.strip())

                    out = {}
                    keys = eval(keys_str.strip())  # Evaluate keys part
                    res = eval(expression.strip())
                    for i, key_name in enumerate(keys):
                        out[key_name] = res[i]

                    output[key] = out
                    # print("||||||||||||", out)
                else:
                    output[key] = eval(formula)

                # if "fetch_ohlcv" in formula:
                #     ohlcv = output[key]

                del inputs[key]  # Remove resolved item
                print("\n\n\n\n\n==================================")
                print(key, formula)
                # print(output[key])
                break
            except Exception as e:
                # Skip if dependencies are not resolved yet
                print(f"Error executing {key}: {formula}")
                # Assign a fallback value, e.g., None
                results[key] = None
                del inputs[key]
                pass

    return output


# Resolve all inputs
# resolve_dependencies(inputs)
# print("---", output['2'])


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

from fastapi import FastAPI, HTTPException, Response
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

    response["query"] = query
    response["outputs"] = json_response.replace("NaN", "null")

    _, last = list(query.items())[-1]

    if "paper_trading" in last:
        # result = paper_trading(output['3'], output['1'], starting_balance=10, position_size=1, fee=0.001)
        print("last", last)
        result = eval(last)
        # print(result)

        # print("Trades:", len(result["trades"]))
        # for trade in result["trades"]:
        #     change = ((trade['exit_price'] - trade['entry_price']) / trade['entry_price']) * 100
        #     print(f"{trade['pnl']:.2f}, {change:.2f}%")

        # print("Final Balance:", result["final_balance"])

        response["result"] = make_serializable(result)

    return response


_inputs = {
    # "0": "fetch_ohlcv('BTC/USDT', '5m', 50)",
    "0": "fetch_ohlcv('BTC/USDT', '5m', 50) -> ['time','open','high','low','close','volume']",
    # "1": "np.multiply(output['0']['high'],1.1)",
    "1": "talib.SMA(output['0']['high'],30)",
}


@app.post("/process/")
async def receive_data(dynamic_data: DynamicData, response: Response):
    response.headers["Cache-Control"] = "no-store"

    try:
        response = process(dynamic_data.data)
    #    response = process(_inputs)

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


# res = process(_inputs)
# output_ = resolve_dependencies(_inputs)
# print("----------", output_['1'])

# paper_trading(output['2'], output['3'], None, None, ohlcv=output['0'], starting_balance=1000, position_size=0.1, fee=0.001)


# print(res)
# serializable_obj = make_serializable(res)

# print(serializable_obj['1'])


# uvicorn app:app --reload

# lsof -i :8000
# kill -9