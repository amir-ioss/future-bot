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
