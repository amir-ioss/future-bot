def paper_trading(long, long_exit, short, short_exit, ohlcv, starting_balance=10000, position_size=0.1, fee=0.001):
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

    balance = starting_balance
    open_position = None
    trade_log = []

    for i in range(len(ohlcv['open'])):
        price = ohlcv['open'][i]
        time = ohlcv['time'][i]

        # print(f"Index: {i}, Price: {price}, Time: {time}")
        # print(f"Signals -> Long: {long[i]}, Long Exit: {long_exit[i]}, Short: {short[i]}, Short Exit: {short_exit[i]}")
        # print(f"Open Position: {open_position}, Balance: {balance}")

        if long is not None and bool(long[i]) and not open_position:  # Open a long position
            trade_amount = balance * position_size
            quantity = trade_amount / price
            open_position = {
                "type": "long",
                "entry_price": price,
                "entry_index": i,
                "quantity": quantity,
                "entry_time": time,
                "trade_amount": trade_amount
            }
            print(i, f"Opening Long Position: {open_position}")

        elif long_exit is not None and long_exit[i] and open_position and open_position['type'] == "long":
            exit_price = price
            pnl = (exit_price - open_position['entry_price']) * open_position['quantity']
            entry_fee = fee * open_position['trade_amount']
            exit_fee = fee * (open_position['quantity'] * exit_price)
            total_fee = entry_fee + exit_fee
            balance += pnl - total_fee

            trade_log.append({
                "type": "long",
                "entry_price": open_position['entry_price'],
                "exit_price": exit_price,
                "entry_index": open_position['entry_index'],
                "exit_index": i,
                "quantity": open_position['quantity'],
                "entry_time": open_position['entry_time'],
                "exit_time": time,
                "pnl": pnl - total_fee,
                "fee": total_fee
            })

            print(i, f"Exiting Long Position, PnL: {pnl - total_fee}")
            open_position = None

        elif short is not None and short[i] and not open_position:
            trade_amount = balance * position_size
            quantity = trade_amount / price
            open_position = {
                "type": "short",
                "entry_price": price,
                "entry_index": i,
                "quantity": quantity,
                "entry_time": time,
                "trade_amount": trade_amount
            }
            print(i, f"Opening Short Position: {open_position}")

        elif short_exit is not None and short_exit[i] and open_position and open_position['type'] == "short":
            exit_price = price
            pnl = (open_position['entry_price'] - exit_price) * open_position['quantity']
            entry_fee = fee * open_position['trade_amount']
            exit_fee = fee * (open_position['quantity'] * exit_price)
            total_fee = entry_fee + exit_fee
            balance += pnl - total_fee

            trade_log.append({
                "type": "short",
                "entry_price": open_position['entry_price'],
                "exit_price": exit_price,
                "entry_index": open_position['entry_index'],
                "exit_index": i,
                "quantity": open_position['quantity'],
                "entry_time": open_position['entry_time'],
                "exit_time": time,
                "pnl": pnl - total_fee,
                "fee": total_fee
            })

            print(i, f"Exiting Short Position, PnL: {pnl - total_fee}")
            open_position = None

    print(f"Final Balance: {balance}")
    return {
        "final_balance": balance,
        "trades": trade_log,
    }



# ohlcv = {
#     "open": [100, 105, 110, 115, 120, 100, 105, 110, 115, 120],
#     "time": ["2025-01-01 10:00", "2025-01-01 10:01", "2025-01-01 10:02", "2025-01-01 10:03", "2025-01-01 10:04", "2025-01-01 10:00", "2025-01-01 10:01", "2025-01-01 10:02", "2025-01-01 10:03", "2025-01-01 10:04"]
# }
# long =       [True, True, False, False, False, False, False, True, False, False]
# long_exit =  [False, False, True, True, True, False, False, True, False, False]
# short =      [True, False, False, False, False, True, False, False, False, False]
# short_exit = [False, False, True, False, False, False, False, False, False, True]

# result = paper_trading(long, long_exit, short, short_exit, ohlcv)
# # print(result)