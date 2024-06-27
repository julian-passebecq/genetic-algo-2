import random
import datetime
from constants import APPOINTMENT_TYPES
from models import Meeting

def generate_meeting(date, client, is_night=False):
    if is_night:
        meeting_type = "Security"
        start_hour = random.randint(21, 23)
        duration = random.randint(2, 8)  # Night shifts are longer
    else:
        meeting_type = random.choice([type for type in APPOINTMENT_TYPES if type != "Security"])
        start_hour = random.randint(8, 19)
        duration = random.randint(1, 3)

    start_time = datetime.datetime.combine(date, datetime.time(hour=start_hour))
    end_time = start_time + datetime.timedelta(hours=duration)

    # Ensure night shifts don't end after 5 AM next day
    if is_night and end_time.time() > datetime.time(hour=5):
        end_time = end_time.replace(hour=5, minute=0)

    return Meeting(
        start=start_time,
        end=end_time,
        required_skill=meeting_type,
        is_night=is_night
    )

def generate_meetings(start_date, num_clients=5, days=7):
    meetings = []
    for day in range(days):
        current_date = start_date + datetime.timedelta(days=day)
        daily_meetings = []
        night_shift_assigned = False

        # Generate day meetings
        while len(daily_meetings) < 15:  # Limit day meetings
            client = random.randint(1, num_clients)
            meeting = generate_meeting(current_date, client, is_night=False)
            daily_meetings.append(meeting)

        # Generate one night shift
        night_shift = generate_meeting(current_date, random.randint(1, num_clients), is_night=True)
        daily_meetings.append(night_shift)

        meetings.extend(daily_meetings)

    return meetings