import datetime
from typing import List, Dict

class Agent:
    def __init__(self, id: str, skills: List[str]):
        self.id = id
        self.skills = skills
        self.schedule: Dict[datetime.date, List['Meeting']] = {}
        self.last_shift_end: datetime.datetime = None

    def can_work(self, meeting: 'Meeting') -> bool:
        if not self.schedule:
            return True
        
        if self.last_shift_end:
            rest_time = meeting.start - self.last_shift_end
            if rest_time < datetime.timedelta(hours=8):
                return False

        return meeting.required_skill in self.skills or meeting.required_skill == 'Monitoring'

    def add_meeting(self, meeting: 'Meeting'):
        date = meeting.start.date()
        if date not in self.schedule:
            self.schedule[date] = []
        self.schedule[date].append(meeting)
        self.last_shift_end = meeting.end

class Meeting:
    def __init__(self, start: datetime.datetime, end: datetime.datetime, required_skill: str, is_night: bool):
        self.start = start
        self.end = end
        self.required_skill = required_skill
        self.is_night = is_night

    @property
    def duration(self) -> float:
        return (self.end - self.start).total_seconds() / 3600

    def overlaps(self, other: 'Meeting') -> bool:
        return (self.start < other.end) and (other.start < self.end)