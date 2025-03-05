
from datetime import datetime, timedelta, date
import pickle

def calculate_week_start(start_date):
    """
    Calculate the starting Sunday of the first week for a participant.

    Args:
        start_date (datetime.date): The participant's start date.

    Returns:
        datetime.date: The starting Sunday of the first week.
    """
    # Calculate the day of the week (0=Monday, 6=Sunday)
    day_of_week = start_date.weekday()

    # Find the first Sunday after the start_date
    first_sunday = start_date + timedelta(days=(6 - day_of_week))

    # Ensure at least 7 days after the start_date for the first week
    if (first_sunday - start_date).days < 7:
        # Move to the next Sunday
        first_sunday += timedelta(days=7)

    return first_sunday

def create_hashmaps(start_date, first_week_start, today):
    """
    Create two hashmaps: one mapping days to weeks and another mapping days to day counters.

    Args:
        start_date (datetime.date): The participant's start date.
        first_week_start (datetime.date): The first Sunday for the participant.
        today (datetime.date): The current date.

    Returns:
        tuple: Two hashmaps (days_to_weeks, days_to_counters).
    """
    days_to_weeks = {}
    days_to_counters = {}
    day_counter = 1  # Start counting from 1
    current_date = start_date

    # Determine the first full week
    if (first_week_start - start_date).days < 7:
        first_week_start += timedelta(days=7)  # Ensure first week starts on the next Sunday

    # Iterate through each day from start_date to today
    while current_date <= today:
        if current_date < first_week_start:
            week = 1
        else:
            week = ((current_date - first_week_start).days // 7) + 2  # Weeks start at 2 after the first

        # Populate hashmaps
        days_to_weeks[current_date] = week
        days_to_counters[current_date] = day_counter

        current_date += timedelta(days=1)
        day_counter += 1

    return days_to_weeks, days_to_counters

# Example Usage


# Print Results



with open("/home/sneupane/relief_study/data/Participants_Pool/participants_details.pickle", "rb") as file:
        participant_hashmap = pickle.load(file)
user_days_week={}


today=date.today()
# print(today)
for user in participant_hashmap:
    print(user)
    study_start_date=participant_hashmap[user][2]
    print(study_start_date)
    if study_start_date !="No Start Date":
        study_start_date = datetime.strptime(study_start_date, "%Y-%m-%d")
        # participant_start_date = study_start_date.date()  # Replace with actual start date
        participant_start_date=study_start_date.date()

    # Calculate the first week's start date
        first_week_start = calculate_week_start(participant_start_date)

    # Generate the week map
        days_to_weeks, days_to_counters = create_hashmaps(participant_start_date, first_week_start, today)
        user_days_week[user]=[days_to_weeks,days_to_counters]


file_path = "/home/sneupane/relief_study/data/Participants_Pool/user_days_week.pickle"
with open(file_path, "wb") as file:
        pickle.dump(user_days_week, file)
# print(user_days_week)
current_datetime = datetime.now()
print(f"Current Date and Time: {current_datetime}")
print("Process Done")
