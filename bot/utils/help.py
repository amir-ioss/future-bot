from datetime import datetime, timezone, timedelta

def percentage_difference(number1, number2):
    # difference = abs(number1 - number2)
    difference = number2 - number1 
    percentage_diff = (difference / number1) * 100
    return percentage_diff


def is_between_saturday_sunday_noon(timestamp_ms):
    # Convert timestamp_ms to datetime object
    dt = datetime.fromtimestamp(timestamp_ms/1000, timezone.utc)  # Assuming the timestamp is in UTC

    # Get the day of the week (0=Monday, 6=Sunday)
    day_of_week = dt.weekday()

    # Get the time of the day
    time_of_day = dt.time()

    # Define Saturday 00:00 and Sunday 12:00
    saturday_start = dt.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=(day_of_week + 1) % 7)
    sunday_noon = dt.replace(hour=12, minute=0, second=0, microsecond=0) - timedelta(days=(day_of_week + 1) % 7 - 1)

    # Check if the timestamp is between Saturday 00:00 and Sunday 12:00
    if saturday_start <= dt < sunday_noon:
        return True
    else:
        return False
    

def is_saturday(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp = timestamp_ms / 1000

    # Convert timestamp to datetime object in UTC
    dt = datetime.fromtimestamp(timestamp, timezone.utc)

    # Get the day of the week (0=Monday, 6=Sunday)
    day_of_week = dt.weekday()

    # Check if it's Saturday (5)
    if day_of_week == 5:
        return True
    else:
        return False



