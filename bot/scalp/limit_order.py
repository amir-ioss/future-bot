import ccxt
import time
import math

# Initialize Binance Futures with CCXT
exchange = ccxt.binance({
    'apiKey': 'h5J8MK5WP5t2DKADpFvOhoE98chuKJxsSB7ny239DWaO49amJmkmzFgus7wEZPpH',
    'secret': 'JEk6zkYmIrwOS1JswoIdPfwndqpfXRsfc00dS4F8rJS6c93qa8PRpLecOpCc8peb',
    # 'options': {'defaultType': 'future'},  # Use 'future' for Binance Futures
})


def get_price_precision(symbol):
    market = exchange.markets[symbol]
    return market['precision']['price']


def place_limit_order(symbol, side, amount, price):


# Understanding timeInForce
# The timeInForce parameter specifies how long an order remains active:

# GTC (Good-Til-Canceled): The order remains active until it is filled or canceled. (Default for limit orders).
# IOC (Immediate-Or-Cancel): The order must fill immediately, either partially or fully. Any unfilled portion is canceled.
# FOK (Fill-Or-Kill): The order must be completely filled immediately; otherwise, it is canceled.
# GTX (Good-Til-Canceled Post-Only): The order ensures it's a maker order (avoiding taker fees).

    try:
        # Get price precision
        price_precision = get_price_precision(symbol)

        # Round price to required precision
        rounded_price = round(price, price_precision)

        # Place limit order
        order = exchange.create_order(
            symbol=symbol,
            type='limit',
            side=side,
            amount=amount,
            price=rounded_price,
            params={'timeInForce': 'GTC'}  # Post-Only
        )
        print(f"Limit order placed: {order}")
        return order
    except Exception as e:
        print(f"Error placing limit order: {e}")
        return None



def check_order_status(symbol, order_id):
    """
    Checks the status of a specific order.
    :param symbol: Trading pair, e.g., 'BTC/USDT'
    :param order_id: The ID of the order
    :return: Order status
    """
    try:
        order = exchange.fetch_order(order_id, symbol)
        print(f"Order status: {order['status']}")
        return order['status']  # e.g., 'open', 'closed', 'canceled'
    except Exception as e:
        print(f"Error checking order status: {e}")
        return None



def cancel_order(symbol, order_id):
    """
    Cancels an unfilled order.
    :param symbol: Trading pair, e.g., 'BTC/USDT'
    :param order_id: The ID of the order
    :return: Cancellation result
    """
    try:
        result = exchange.cancel_order(order_id, symbol)
        print(f"Order canceled: {result}")
        return result
    except Exception as e:
        print(f"Error canceling order: {e}")
        return None
    


def sell_all_limit(symbol, limit_price):
    try:
        # Get the base currency from the trading pair (e.g., BTC from BTC/USDT)
        base_currency = symbol.split('/')[0]

        # Fetch balance for the base currency
        balance = exchange.fetch_balance()
        amount_to_sell = balance[base_currency]['free']  # Free balance available for trading

        # Ensure there is a sufficient balance to sell
        if amount_to_sell <= 0:
            raise ValueError(f"No {base_currency} balance available to sell.")

        # Place the limit sell order
        order = exchange.create_order(
            symbol=symbol,
            type='limit',
            side='sell',
            amount=amount_to_sell,
            price=limit_price
        )

        print(f"Limit sell order placed: {order}")
        return order
    except Exception as e:
        print(f"Error placing sell order: {e}")
        return None



# balance : 8.19
#  
symbol = 'ADA/USDT'
markets = exchange.load_markets()

market = exchange.markets[symbol]
min_notional = market['limits']['cost']['min']  # Minimum notional value

print(f"Minimum Notional Value for {symbol}: {min_notional}")

side = 'buy'  # Use 'sell' for selling
amount = 7
current_price = exchange.fetch_ticker(symbol)['last']
limit_price = current_price - (current_price*0.000099)
print(symbol, side, amount, current_price, limit_price)

# order  = place_limit_order(symbol, side, amount, limit_price)
order  = True
if order:
    # time.sleep(15)
    # id = order['info']['orderId']
    # cancel_order(symbol, id)

    side = 'sell'  # Use 'sell' for selling
    limit_price = current_price + (current_price*0.000099)
    print("limit_price:", limit_price)
    print(symbol, side, amount, current_price, limit_price)
    sell_all_limit(symbol, limit_price)

