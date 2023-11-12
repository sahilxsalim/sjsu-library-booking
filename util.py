from datetime import datetime, timedelta
from datetime import datetime
import pytz

def increment_date(date_string, days=1):
    """
    Increment the given date string by a specified number of days.

    Parameters:
    - date_string (str): Date in the format '%Y-%m-%d'.
    - days (int): Number of days to increment (default is 1).

    Returns:
    - str: Updated date string.
    """
    # Convert the string to a datetime object
    date_object = datetime.strptime(date_string, '%Y-%m-%d')

    # Increment the day by the specified number of days
    new_date = date_object + timedelta(days=days)

    # Convert the result back to a string
    new_date_string = new_date.strftime('%Y-%m-%d')

    return new_date_string

def get_today_date():
    """
    Get today's date in the format '%Y-%m-%d'.

    Returns:
    - str: Today's date.
    """
    return datetime.today().strftime('%Y-%m-%d')


def get_time():
    """
    Get the current time in the Pacific timezone in the format '%H:%M:%S'.

    Returns:
    - str: Current time in the Pacific timezone.
    """
    pacific_tz = pytz.timezone('US/Pacific')
    pacific_time = datetime.now(pacific_tz).strftime('%H:%M:%S')
    return pacific_time

def create_titles(slots, room_number = 864):
    """
    Form a list of titles for each slot.

    Parameters:
    - slots (list): List of slots.

    Returns:
    - list: List of titles.
    """
    titles = []
    for slot in slots:

        # Convert the input string to a datetime object
        input_time = datetime.strptime(slot.get("start"), "%Y-%m-%d %H:%M:%S")
        # Format the datetime object according to the desired output
        formatted_time = input_time.strftime("%-I:%M%p %A, %B %d, %Y").replace("AM", "am").replace("PM", "pm")
        # Get the title with the additional information
        title = f"{formatted_time} - {room_number} - Available"

        titles.append(title)
    
    return titles
