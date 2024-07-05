import random
import datetime
from constants import APPOINTMENT_TYPES, SHIFTS, AGENTS, IDEAL_DAILY_HOURS, TRAVEL_TIME, SECURITY_SHIFT_DURATION, MONITORING_NIGHT_SHIFT_DURATION

def generate_meeting(date, shift_type):
    if shift_type == "Night":
        if random.random() < 0.6:  # 60% chance for monitoring, 40% for security
            meeting_type = "Monitoring"
            duration = MONITORING_NIGHT_SHIFT_DURATION
        else:
            meeting_type = "Security"
            duration = SECURITY_SHIFT_DURATION
        start_hour, _ = SHIFTS["Night"]
        start_time = datetime.datetime.combine(date, datetime.time(hour=start_hour))
        end_time = start_time + datetime.timedelta(hours=duration)
    else:
        meeting_type = random.choice([t for t in APPOINTMENT_TYPES if t != "Security"])
        start_hour, end_hour = SHIFTS[shift_type]
        if meeting_type == "Monitoring":
            duration = random.randint(2, 3)
        else:
            duration = random.randint(1, 3)
        start_time = datetime.datetime.combine(date, datetime.time(hour=random.randint(start_hour, end_hour - duration)))
        end_time = start_time + datetime.timedelta(hours=duration)

    return {
        "start": start_time,
        "end": end_time,
        "required_skill": meeting_type,
        "is_night": (shift_type == "Night")
    }

def generate_meetings(start_date, days=7):
    meetings = []
    for day in range(days):
        current_date = start_date + datetime.timedelta(days=day)
        
        # Day meetings
        day_meetings = [generate_meeting(current_date, "Morning") for _ in range(random.randint(15, 20))]
        day_meetings += [generate_meeting(current_date, "Afternoon") for _ in range(random.randint(15, 20))]
        
        # Night meetings
        night_meetings = [generate_meeting(current_date, "Night") for _ in range(5)]  # 2 monitoring, 1 security, 2 extra
        
        meetings.extend(day_meetings + night_meetings)

    return meetings

def estimate_meeting_capacity(num_agents, days):
    total_agent_hours = num_agents * IDEAL_DAILY_HOURS * days
    average_meeting_duration = 2.5  # Assuming an average meeting duration of 2.5 hours
    estimated_meetings = int(total_agent_hours / (average_meeting_duration + TRAVEL_TIME))
    return estimated_meetings