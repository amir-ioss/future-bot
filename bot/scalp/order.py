
import ccxt
from config import accounts, symbols, timeframe, leverage, amount_usdt 
from help import log 

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
