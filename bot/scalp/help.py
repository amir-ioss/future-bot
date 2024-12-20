from datetime import datetime
import config
import logging


logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log(details=""):
    """
    Logs CRUD actions with optional details.
    """
    print(details)
    logging.info(f"{details}")
    return f"Created {details}"



# NOTIFY
from plyer import notification
def trigger_notification(title, message):
    if not config.notify: return
    notification.notify(
        title=title,
        message=message,
        app_name=config.bot_name,  # Optional, for Linux and macOS
        timeout=10                 # Duration in seconds for the notification to appear
    )



def timestamp_to_HHMM(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000
    
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp_s)
    
    # Format the datetime object to HH:MM
    formatted_time = dt_object.strftime('%H:%M')
    
    return formatted_time



def perc_diff(a, b):
    if a == b:
        return 0  # No difference if the numbers are the same
    # return abs(a - b) / ((a + b) / 2) * 100
    return (a - b) / ((a + b) / 2) * 100






import pandas as pd


def pivot_high(highs, left_bars=2, right_bars=2):
    if isinstance(highs, list):
        highs = pd.Series(highs)
    
    pivot_highs = [None] * len(highs)  # Initialize the list with empty strings

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
    pivot_lows = [None] * len(lows)  # Initialize the list with empty strings

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
