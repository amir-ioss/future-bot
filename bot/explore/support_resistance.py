import numpy as np
import pandas as pd
# import talib as ta
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



def support_resistance_levels(ohlcv, window=15, volume_threshold=20):
    """
    Calculate support and resistance levels for each candle using a rolling window
    
    Parameters:
    df : pandas.DataFrame
        Must contain columns: ['high', 'low', 'close', 'volume']
    window : int
        Rolling window size for support/resistance calculation
    volume_threshold : int
        Volume threshold percentage for confirming levels
    
    Returns:
    DataFrame with support and resistance levels for each candle
    """
    df = prepare_data_for_analysis(ohlcv)
    
    # Initialize result arrays
    length = len(df)
    supports = np.zeros((length, 3))  # Will store 3 support levels
    resistances = np.zeros((length, 3))  # Will store 3 resistance levels
    
    # Calculate volume indicators using TA-Lib
    volume = df['volume'].values
    vol_ema5 = talib.EMA(volume, timeperiod=5)
    vol_ema10 = talib.EMA(volume, timeperiod=10)
    vol_osc = 100 * (vol_ema5 - vol_ema10) / vol_ema10
    
    # Calculate various technical indicators for support/resistance identification
    df['ema20'] = talib.EMA(df['close'], timeperiod=20)
    df['ema50'] = talib.EMA(df['close'], timeperiod=50)
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    
    # Upper and lower Bollinger Bands
    upper, middle, lower = talib.BBANDS(df['close'], 
                                      timeperiod=20,
                                      nbdevup=2,
                                      nbdevdn=2,
                                      matype=0)
    
    for i in range(window, length):
        # Get the window slice
        window_data = df.iloc[i-window:i+1]
        
        # Find local minima (supports)
        window_lows = window_data['low'].values
        support_levels = []
        
        # Method 1: Local minima
        for j in range(1, len(window_lows)-1):
            if window_lows[j] < window_lows[j-1] and window_lows[j] < window_lows[j+1]:
                support_levels.append(window_lows[j])
        
        # Method 2: Technical indicators for support
        support_levels.extend([
            lower[i],  # Lower Bollinger Band
            df['ema20'].iloc[i],  # EMA 20
            df['ema50'].iloc[i],  # EMA 50
        ])
        
        # Find local maxima (resistances)
        window_highs = window_data['high'].values
        resistance_levels = []
        
        # Method 1: Local maxima
        for j in range(1, len(window_highs)-1):
            if window_highs[j] > window_highs[j-1] and window_highs[j] > window_highs[j+1]:
                resistance_levels.append(window_highs[j])
        
        # Method 2: Technical indicators for resistance
        resistance_levels.extend([
            upper[i],  # Upper Bollinger Band
            df['ema20'].iloc[i],  # EMA 20
            df['ema50'].iloc[i],  # EMA 50
        ])
        
        # Filter and sort levels
        support_levels = [x for x in support_levels if not np.isnan(x)]
        resistance_levels = [x for x in resistance_levels if not np.isnan(x)]
        
        if support_levels:
            support_levels = sorted(set(support_levels))[-3:]  # Keep top 3 supports
            supports[i, :len(support_levels)] = support_levels
            
        if resistance_levels:
            resistance_levels = sorted(set(resistance_levels))[:3]  # Keep top 3 resistances
            resistances[i, :len(resistance_levels)] = resistance_levels
    
    # Create result DataFrame
    # result = pd.DataFrame({
    #     'support1': supports[:, 0],
    #     'support2': supports[:, 1],
    #     'support3': supports[:, 2],
    #     'resistance1': resistances[:, 0],
    #     'resistance2': resistances[:, 1],
    #     'resistance3': resistances[:, 2],
    # }, index=df.index)

    return supports[:, 0], supports[:, 1], supports[:, 2], resistances[:, 0], resistances[:, 1], resistances[:, 2],
    # return result



def support_resistance(ohlcv, window=15, volume_threshold=20):
    """
    Calculate single support and resistance level for each candle
    
    Parameters:
    df : pandas.DataFrame
        Must contain columns: ['high', 'low', 'close', 'volume']
    window : int
        Rolling window size for support/resistance calculation
    volume_threshold : int
        Volume threshold percentage for confirming levels
    
    Returns:
    DataFrame with single support and resistance level for each candle
    """
    df = prepare_data_for_analysis(ohlcv)
    
    # Initialize arrays with NaN
    length = len(df)
    supports = np.full(length, np.nan)
    resistances = np.full(length, np.nan)
    
    # Calculate volume indicators
    volume = df['volume'].values
    vol_ema5 = talib.EMA(volume, timeperiod=5)
    vol_ema10 = talib.EMA(volume, timeperiod=10)
    vol_osc = 100 * (vol_ema5 - vol_ema10) / vol_ema10
    
    # Pre-calculate some technical indicators
    upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20)
    
    # Calculate levels for each candle
    for i in range(window, length):
        # Get the window slice
        window_slice = df.iloc[i-window:i]
        current_close = df['close'].iloc[i]
        
        # Find the most significant low in the window
        window_min = window_slice['low'].min()
        window_min_idx = window_slice['low'].idxmin()
        
        # Find the most significant high in the window
        window_max = window_slice['high'].max()
        window_max_idx = window_slice['high'].idxmax()
        
        # Set support level
        if current_close > window_min:
            supports[i] = window_min
            
        # Set resistance level    
        if current_close < window_max:
            resistances[i] = window_max
            
        # If no level found, use Bollinger Bands
        if np.isnan(supports[i]):
            supports[i] = lower[i]
        if np.isnan(resistances[i]):
            resistances[i] = upper[i]
    
    # Fill initial NaN values with first calculated value
    first_valid_support = next(x for x in supports if not np.isnan(x))
    first_valid_resistance = next(x for x in resistances if not np.isnan(x))
    supports[:window] = first_valid_support
    resistances[:window] = first_valid_resistance
    
    # Create result DataFrame
    # result = pd.DataFrame({
    #     'support': supports,
    #     'resistance': 
    # }, index=df.index)

    return supports, resistances
    # return result