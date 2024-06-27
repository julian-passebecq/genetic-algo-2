import random
import datetime
from constants import APPOINTMENT_TYPES
from models import Meeting

def generate_meeting(date, client, is_night=False):
    if is_night:
        start_hour = 22  # Night shift starts at 22:00
        duration = 5.5  # 3 hours security + 2.5 hours after break
    else:
        start_hour = random.choice([8, 11])  # Day shifts start at 8:00 or 11:00
        duration = random.uniform(1, 3)  # Between 1 and 3 hours

    start_time = datetime.datetime.combine(date, datetime.time(hour=start_hour))
    end_time = start_time + datetime.timedelta(hours=duration)

    meeting_type = "Security" if is_night else random.choice([type for type in APPOINTMENT_TYPES if type != "Security"])

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
        
        # Generate day meetings
        day_meetings = []
        total_day_hours = 0
        while total_day_hours < 35:  # Aim for about 35 hours of day meetings
            client = random.randint(1, num_clients)
            meeting = generate_meeting(current_date, client, is_night=False)
            if total_day_hours + (meeting.end - meeting.start).total_seconds() / 3600 <= 35:
                day_meetings.append(meeting)
                total_day_hours += (meeting.end - meeting.start).total_seconds() / 3600
        
        # Generate one night shift
        night_shift = generate_meeting(current_date, random.randint(1, num_clients), is_night=True)
        
        meetings.extend(day_meetings + [night_shift])

    return meetings