AGENTS = {
    "Agent1": ["Fire", "Security"],
    "Agent2": ["Maintenance", "Security"],
    "Agent3": ["Fire"],
    "Agent4": ["Security"],
    "Agent5": []
}

APPOINTMENT_TYPES = ["Monitoring", "Fire", "Security", "Maintenance"]

SHIFTS = {
    "Morning": (7, 15),
    "Afternoon": (14, 22),
    "Night1": (21, 22),
    "Night2": (22, 1),
    "Night3": (2, 4),
    "Night4": (4, 5)
}

SECURITY_AGENTS = [agent for agent, skills in AGENTS.items() if "Security" in skills]