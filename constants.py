import random

SKILLS = ["Fire", "Security", "Maintenance"]

def generate_agent_skills():
    num_skills = random.choices([0, 1, 2], weights=[3, 5, 2])[0]
    return random.sample(SKILLS, num_skills)

AGENTS = {f"Agent{i+1}": generate_agent_skills() for i in range(12)}

APPOINTMENT_TYPES = ["Monitoring", "Fire", "Security", "Maintenance"]

SHIFTS = {
    "Morning": (7, 15),
    "Afternoon": (15, 23),
    "Night": (23, 7)
}

MAX_DAILY_HOURS = 10
MIN_DAILY_HOURS = 6
IDEAL_DAILY_HOURS = 8
MIN_BREAK_TIME = 0.5
LUNCH_BREAK_TIME = 1
MIN_REST_BETWEEN_SHIFTS = 11
TRAVEL_TIME = 0.5
MAX_CONSECUTIVE_DAYS = 5
MAX_WEEKLY_HOURS = 48
SECURITY_SHIFT_DURATION = 3
MONITORING_NIGHT_SHIFT_DURATION = 2
PENALTY_WEIGHT = {
    "skill_mismatch": 1000,
    "overwork": 500,
    "underwork": 200,
    "uneven_distribution": 300,
    "break_violation": 400,
    "consecutive_days": 600,
    "unfilled_meeting": 50,
    "uneven_night_shifts": 400,
    "scheduled_meeting": 100
}