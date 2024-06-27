from typing import List
import datetime

class Agent:
    def __init__(self, id: str, skills: List[str]):
        self.id = id
        self.skills = skills
        self.schedule = {}  # {date: [meetings]}

class Meeting:
    def __init__(self, start: datetime.datetime, end: datetime.datetime, required_skill: str, is_night: bool):
        self.start = start
        self.end = end
        self.required_skill = required_skill
        self.is_night = is_night