from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import ccxt
from datetime import datetime
import asyncio
import pandas as pd
import json

from bot import TradingBot

bot = TradingBot(symbol='BTC/USDT', live=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(bot.run())
    yield


# API
app = FastAPI(lifespan=lifespan)


# Update the origins to include the correct React app origin
origins = [
    "http://localhost:5173",  # Common default port for React, adjust if necessary
    "http://192.168.23.63:5173",  # Your React app's origin
]

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/bot")
async def bot_backend():
    response = {
        "supports": bot.supports,
        "resists": bot.resists,
        "marks": bot.marks,
        "text": bot.text,
        "strong_supports": bot.strong_supports,
        "strong_resists": bot.strong_resists,
        "breakouts": bot.breakouts,
        "positions": bot.positions,
        "h_points": bot.h_points,
        "l_points": bot.l_points,
        "candles": bot.candles,
        # 'times': bot.times
    }
    return response


@app.get("/test")
async def bot_backend():
    dates = range(12)
    response = []
    
    for date in dates:
        # file_path = f"../src/data/ohlcv/{date}.json"
        # file_path = f"./test/btc/BTC_2023_{date+1:02d}.json"
        # file_path = f"./test/btc/BTC_2024_{date+1:02d}.json"
        file_path = f"./test/xrp/XRP_2023_{date+1:02d}.json"

        try:
            with open(file_path, "r") as file:
                ohlcv_data = json.load(file)
                # print(ohlcv_data[:10])  # Display first 10 records for debugging

            if ohlcv_data:
                bot = TradingBot(symbol='XRP/USDT')
                await bot.run(True, ohlcv_data)
                response.append(
                    {
                        "date": date,
                        "positions": bot.positions,
                    }
                )
                del bot # cleanup

        except FileNotFoundError:
            response.append(
                {
                    "date": date,
                    "error": f"File {file_path} not found",
                }
            )
        except json.JSONDecodeError:
            response.append(
                {
                    "date": date,
                    "error": f"Error decoding JSON from {file_path}",
                }
            )

    return response


# uvicorn main:app --reload


@app.get("/ping")
async def ping():
    return {"message": "pong"}
