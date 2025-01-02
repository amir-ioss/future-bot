import numpy as np

class OrderBlockInfo:
    def __init__(self, top, bottom, obVolume, obType, startTime, endTime, obLowVolume, obHighVolume, breaker=False, breakTime=None):
        self.top = top
        self.bottom = bottom
        self.obVolume = obVolume
        self.obType = obType
        self.startTime = startTime
        self.endTime = endTime
        self.obLowVolume = obLowVolume
        self.obHighVolume = obHighVolume
        self.breaker = breaker
        self.breakTime = breakTime

class OrderBlock:
    def __init__(self, info):
        self.info = info

def find_order_blocks(prices, volumes, swing_length=1, max_order_blocks=10):
    bullish_order_blocks = []
    bearish_order_blocks = []
    
    max_distance_to_last_bar = 1750

    for i in range(swing_length, len(prices)):
        upper = np.max(prices[i-swing_length:i])  # Highest price in the last `swing_length` bars
        lower = np.min(prices[i-swing_length:i])  # Lowest price in the last `swing_length` bars

        # Detecting Bullish Order Block
        if prices[i] > upper:  # Higher price than the highest price in the swing
            top = prices[i]
            bottom = np.min(prices[i-swing_length:i])
            ob_volume = np.sum(volumes[i-swing_length:i])
            order_block = OrderBlockInfo(
                top=top, 
                bottom=bottom, 
                obVolume=ob_volume, 
                obType="Bull", 
                startTime=i, 
                endTime=None,  # We'll fill this in after the loop
                obLowVolume=np.min(volumes[i-swing_length:i]), 
                obHighVolume=np.max(volumes[i-swing_length:i])
            )
            if len(bullish_order_blocks) < max_order_blocks:
                bullish_order_blocks.append(OrderBlock(order_block))

        # Detecting Bearish Order Block
        if prices[i] < lower:  # Lower price than the lowest price in the swing
            top = np.max(prices[i-swing_length:i])
            bottom = prices[i]
            ob_volume = np.sum(volumes[i-swing_length:i])
            order_block = OrderBlockInfo(
                top=top, 
                bottom=bottom, 
                obVolume=ob_volume, 
                obType="Bear", 
                startTime=i, 
                endTime=None,  # We'll fill this in after the loop
                obLowVolume=np.min(volumes[i-swing_length:i]), 
                obHighVolume=np.max(volumes[i-swing_length:i])
            )
            if len(bearish_order_blocks) < max_order_blocks:
                bearish_order_blocks.append(OrderBlock(order_block))

    # Set endTime for each order block based on the next order block's startTime
    all_order_blocks = bullish_order_blocks + bearish_order_blocks
    for i in range(len(all_order_blocks) - 1):
        all_order_blocks[i].info.endTime = all_order_blocks[i + 1].info.startTime  # Next startTime is the endTime of the current block
    
    # The last order block will have None as the endTime
    if all_order_blocks:
        all_order_blocks[-1].info.endTime = None

    # Return the array of order blocks
    return [order_block.info.__dict__ for order_block in all_order_blocks]

# Example usage
# prices = np.array([100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150])
# volumes = np.array([500, 600, 550, 700, 800, 750, 900, 950, 1000, 1100, 1200])

# order_blocks = find_order_blocks(prices, volumes)
# for ob in order_blocks:
#     print(ob)

import numpy as np

def find_order_blocks2(data, threshold_volume=100, price_move_threshold=0.05):
    order_blocks = []
    current_block = None
    
    # Ensure your data arrays have the same length
    n = len(data["time"])
    
    for i in range(1, n):
        # Get the current and previous candle data
        current_candle = {
            'open': data["open"][i],
            'close': data["close"][i],
            'high': data["high"][i],
            'low': data["low"][i],
            'volume': data["volume"][i]
        }
        prev_candle = {
            'open': data["open"][i - 1],
            'close': data["close"][i - 1],
            'high': data["high"][i - 1],
            'low': data["low"][i - 1],
            'volume': data["volume"][i - 1]
        }

        # print(f"Current Candle: {current_candle}")
        # print(f"Previous Candle: {prev_candle}")
        
        # Check if the volume is above the threshold
        if current_candle['volume'] > threshold_volume:
            # Bullish Order Block: Current close > previous high by price_move_threshold
            if current_candle['close'] > prev_candle['high'] * (1 + price_move_threshold):
                print(f"Bullish Order Block Detected")
                if not current_block or current_block['obType'] != 'Bull':
                    if current_block:
                        order_blocks.append(current_block)
                    current_block = {
                        'obType': 'Bull',
                        'top': current_candle['high'],
                        'bottom': current_candle['low'],
                        'startTime': i - 1,
                        'endTime': i
                    }
                else:
                    current_block['endTime'] = i
                    current_block['top'] = max(current_block['top'], current_candle['high'])
                    current_block['bottom'] = min(current_block['bottom'], current_candle['low'])

            # Bearish Order Block: Current close < previous low by price_move_threshold
            elif current_candle['close'] < prev_candle['low'] * (1 - price_move_threshold):
                print(f"Bearish Order Block Detected")
                if not current_block or current_block['obType'] != 'Bear':
                    if current_block:
                        order_blocks.append(current_block)
                    current_block = {
                        'obType': 'Bear',
                        'top': current_candle['high'],
                        'bottom': current_candle['low'],
                        'startTime': i - 1,
                        'endTime': i
                    }
                else:
                    current_block['endTime'] = i
                    current_block['top'] = max(current_block['top'], current_candle['high'])
                    current_block['bottom'] = min(current_block['bottom'], current_candle['low'])
        else:
            print(f"Volume too low: {current_candle['volume']}")

    # Add the last detected order block if any
    if current_block:
        order_blocks.append(current_block)

    print(f"Final Order Blocks: {order_blocks}")
    return order_blocks
