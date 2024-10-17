
import ccxt
from config import accounts, symbols, timeframe, leverage, amount_usdt 
from help import log 
import time

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
    
    if usdt_balance < (amount_usdt/leverage) :
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

    
# async def close_position(user_exchange, symbol, amount, side):
#     order = user_exchange.create_market_order(symbol, side, amount)
#     return order

import asyncio

async def close_position(user_exchange, symbol, side, max_retries=3, delay=2):
    """
    Attempts to close a position asynchronously. If the position is not closed,
    it retries up to 'max_retries' times with a non-blocking delay using asyncio.

    :param user_exchange: The Binance exchange object (ccxt).
    :param symbol: The trading pair symbol (e.g., 'BTCUSDT').
    :param side: 'buy' or 'sell', depending on the position direction.
    :param max_retries: Maximum number of retries if closing fails.
    :param delay: Delay in seconds between retry attempts.
    :return: The final order response or an error message.
    """
    try:
        # Initial attempt to close the position
        for attempt in range(max_retries):
            position = get_position(user_exchange, symbol)  # Check if position still exists

            if position and float(position['positionAmt']) != 0:
                amount = abs(float(position['positionAmt']))  # Get the amount of the position
                order = user_exchange.create_market_order(symbol, side, amount)
                print(f"Position close attempt {attempt + 1} for {symbol} with amount {amount} and side {side}")

                # Wait for the specified delay before checking again
                await asyncio.sleep(delay)

                # Check if the position was closed
                new_position = get_position(user_exchange, symbol)
                if not new_position or float(new_position['positionAmt']) == 0:
                    print(f"Position for {symbol} successfully closed.")
                    return order
            else:
                print(f"No open position for {symbol} to {side}. Exiting...")
                return None

            print(f"Retrying to close position for {symbol} ({attempt + 1}/{max_retries})...")

        print(f"Max retries reached. Position for {symbol} could not be fully closed.")
        return None

    except Exception as e:
        print(f"Error while closing position for {symbol}: {e}")
        return None


def get_position(user_exchange, symbol):
    """
    Fetch the specific position for the given symbol and check if it's open.

    :param user_exchange: The Binance exchange object (ccxt).
    :param symbol: The trading pair symbol (e.g., 'BTCUSDT').
    :return: Position if open, otherwise None.
    """
    try:
        balance = user_exchange.fetch_balance({'type': 'future'})
        positions = balance['info']['positions']

        for position in positions:
            if position['symbol'] == symbol.replace("/", "") and float(position['positionAmt']) != 0:
                return position
        return None

    except Exception as e:
        print(f"Error fetching position for {symbol}: {e}")
        return None

