import pandas as pd



def pivot_high(highs, left_bars=2, right_bars=2):
    if isinstance(highs, list):
        highs = pd.Series(highs)
    
    pivot_highs = [""] * len(highs)  # Initialize the list with empty strings

    for i in range(left_bars, len(highs) - right_bars):
        current_high = highs[i]
        is_pivot = True
        
        # Check left bars
        if any(highs[i - j] >= current_high for j in range(1, left_bars + 1)):
            is_pivot = False
        
        # Check right bars
        if any(highs[i + j] >= current_high for j in range(1, right_bars + 1)):
            is_pivot = False
        
        if is_pivot:
            pivot_highs[i] = current_high  # Mark as pivot high
    
    return pivot_highs

# Example usage
# highs = [10, 12, 14, 16, 15, 13, 11, 17, 18, 16, 14, 12]
# pivot_highs = pivot_high(highs, left_bars=2, right_bars=2)
# print(pivot_highs)





def pivot_low(lows, left_bars=2, right_bars=2):
    if isinstance(lows, list):
        lows = pd.Series(lows)
    pivot_lows = [""] * len(lows)  # Initialize the list with empty strings

    for i in range(left_bars, len(lows) - right_bars):
        current_low = lows[i]
        is_pivot = True
        
        # Check left bars
        if any(lows[i - j] <= current_low for j in range(1, left_bars + 1)):
            is_pivot = False
        
        # Check right bars
        if any(lows[i + j] <= current_low for j in range(1, right_bars + 1)):
            is_pivot = False
        
        if is_pivot:
            pivot_lows[i] = current_low  # Mark as pivot low
    
    return pivot_lows

# Example usage
# lows = [10, 12, 14, 13, 12, 11, 10, 11, 12, 14, 13, 12]
# pivot_lows = pivot_low(lows, left_bars=2, right_bars=2)
# print(pivot_lows)
