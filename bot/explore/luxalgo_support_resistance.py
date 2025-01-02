import numpy as np
import pandas as pd
import talib


def prepare_data_for_analysis(ohlcv_data):
    """
    Converts OHLCV dictionary data into a pandas DataFrame.

    :param ohlcv_data: Dictionary with keys 'time', 'open', 'high', 'low', 'close', 'volume' (numpy arrays).
    :return: pandas DataFrame with OHLCV data.
    """
    return pd.DataFrame({
        'time': ohlcv_data['time'],
        'open': ohlcv_data['open'],
        'high': ohlcv_data['high'],
        'low': ohlcv_data['low'],
        'close': ohlcv_data['close'],
        'volume': ohlcv_data['volume'],
    })
import numpy as np
import pandas as pd
import talib

def pivot_high(data, left_bars, right_bars):
    """
    Calculate pivot highs similar to Pine Script's pivothigh function
    """
    highs = np.zeros(len(data))
    
    for i in range(left_bars, len(data) - right_bars):
        # Check if current point is higher than all points in left and right windows
        left_check = all(data[i] >= data[j] for j in range(i - left_bars, i))
        right_check = all(data[i] >= data[j] for j in range(i + 1, min(i + right_bars + 1, len(data))))
        
        if left_check and right_check:
            highs[i] = data[i]
            
        # If we found a pivot, skip the next few bars to avoid clustering
        if highs[i] != 0:
            i += right_bars
            
    return highs

def pivot_low(data, left_bars, right_bars):
    """
    Calculate pivot lows similar to Pine Script's pivotlow function
    """
    lows = np.zeros(len(data))
    
    for i in range(left_bars, len(data) - right_bars):
        # Check if current point is lower than all points in left and right windows
        left_check = all(data[i] <= data[j] for j in range(i - left_bars, i))
        right_check = all(data[i] <= data[j] for j in range(i + 1, min(i + right_bars + 1, len(data))))
        
        if left_check and right_check:
            lows[i] = data[i]
            
        # If we found a pivot, skip the next few bars to avoid clustering
        if lows[i] != 0:
            i += right_bars
            
    return lows

def fixnan(arr):
    """
    Implement Pine Script's fixnan function - forward fill values
    """
    result = arr.copy()
    last_valid = 0
    
    for i in range(len(result)):
        if result[i] != 0:
            last_valid = result[i]
        elif last_valid != 0:
            result[i] = last_valid
            
    return result

def luxalgo_support_resistance(ohlcv, left_bars=15, right_bars=15, volume_threshold=20):
    """
    Calculate support and resistance levels using LuxAlgo's logic
    
    Parameters:
    df : pandas.DataFrame
        Must contain columns: ['open', 'high', 'low', 'close', 'volume']
    left_bars : int
        Number of bars to look left
    right_bars : int
        Number of bars to look right
    volume_threshold : int
        Volume threshold percentage
        
    Returns:
    DataFrame with support, resistance levels and break signals
    
    """
    df = prepare_data_for_analysis(ohlcv)
    # Calculate pivot points
    high_pivot = pivot_high(df['high'].values, left_bars, right_bars)
    low_pivot = pivot_low(df['low'].values, left_bars, right_bars)
    
    # Shift pivot points by 1 (similar to [1] in Pine Script)
    high_pivot = np.roll(high_pivot, 1)
    low_pivot = np.roll(low_pivot, 1)
    
    # Apply fixnan
    high_pivot = fixnan(high_pivot)
    low_pivot = fixnan(low_pivot)
    
    # Calculate volume indicators
    volume = df['volume'].values
    short = talib.EMA(volume, timeperiod=5)
    long = talib.EMA(volume, timeperiod=10)
    osc = 100 * (short - long) / long
    
    # Initialize break signals
    breaks = np.zeros(len(df), dtype=int)  # 1 for support break, 2 for resistance break
    wick_breaks = np.zeros(len(df), dtype=int)  # 1 for bull wick, 2 for bear wick
    
    for i in range(1, len(df)):
        curr_close = df['close'].iloc[i]
        prev_close = df['close'].iloc[i-1]
        curr_open = df['open'].iloc[i]
        curr_high = df['high'].iloc[i]
        curr_low = df['low'].iloc[i]
        
        # Check for breaks with volume
        if low_pivot[i] != 0:  # Only check valid pivot points
            if (prev_close >= low_pivot[i] and curr_close < low_pivot[i] and 
                not (curr_open - curr_close < curr_high - curr_open) and 
                osc[i] > volume_threshold):
                breaks[i] = 1  # Support break
                
        if high_pivot[i] != 0:  # Only check valid pivot points
            if (prev_close <= high_pivot[i] and curr_close > high_pivot[i] and 
                not (curr_open - curr_low > curr_close - curr_open) and 
                osc[i] > volume_threshold):
                breaks[i] = 2  # Resistance break
            
        # Check for bull/bear wicks
        if high_pivot[i] != 0:
            if (prev_close <= high_pivot[i] and curr_close > high_pivot[i] and 
                curr_open - curr_low > curr_close - curr_open):
                wick_breaks[i] = 1  # Bull wick
                
        if low_pivot[i] != 0:
            if (prev_close >= low_pivot[i] and curr_close < low_pivot[i] and 
                curr_open - curr_close < curr_high - curr_open):
                wick_breaks[i] = 2  # Bear wick
    
    # Create result DataFrame
    # result = pd.DataFrame({
    #     'support': low_pivot,
    #     'resistance': high_pivot,
    #     'break_signal': breaks,
    #     'wick_signal': wick_breaks,
    #     'volume_oscillator': osc
    # }, index=df.index)
    
    # Print some statistics to verify pivot points are being found
    print(f"Number of support levels found: {np.count_nonzero(low_pivot)}")
    print(f"Number of resistance levels found: {np.count_nonzero(high_pivot)}")

    return low_pivot, high_pivot
    return result
