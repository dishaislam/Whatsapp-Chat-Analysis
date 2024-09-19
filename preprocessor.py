import re
import pandas as pd
from datetime import datetime

def preprocess(data):
    # Pattern to match date, time, and message
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s(0?[1-9]|1[0-2]):([0-5]\d)\s(AM|PM))\s-\s(.*)'

    # Find all matches in the data
    matches = re.findall(pattern, data)

    # Function to convert 12-hour format to 24-hour format
    def convert_to_24_hour(hour, minute, am_pm):
        time_str = f"{hour}:{minute} {am_pm}"
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        return time_obj.strftime('%H:%M')

    # Extract date-time and messages
    dates = []
    messages = []

    for match in matches:
        date_part = match[0]
        hour = match[1]
        minute = match[2]
        am_pm = match[3]
        message_part = match[4]

        # Convert to 24-hour format
        time_24 = convert_to_24_hour(hour, minute, am_pm)
        date_time = f"{date_part.split(',')[0]} {time_24} -"

        dates.append(date_time)
        messages.append(message_part.strip())

    # Create a DataFrame after the loop
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert the 'message_date' column to datetime
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y %H:%M -')

    # Rename 'message_date' to 'date'
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract users and messages
    users = []
    message_texts = []

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # If user name is present
            users.append(entry[1])
            message_texts.append(entry[2])
        else:  # For group notifications
            users.append('group_notification')
            message_texts.append(entry[0])

    # Add 'user' and 'message' columns to the DataFrame
    df['user'] = users
    df['message'] = message_texts

    # Drop the original 'user_message' column
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional date information
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['only_date'] = df['date'].dt.date
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['day_name'] = df['date'].dt.day_name()

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str(00) + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df