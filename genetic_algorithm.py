import random
from typing import List, Dict, Tuple
from models import Agent, Meeting

def initialize_population(pop_size: int, agents: List[Agent], meetings: List[Meeting]) -> List[Dict[Meeting, Agent]]:
    population = []
    for _ in range(pop_size):
        schedule = {}
        for meeting in meetings:
            eligible_agents = [agent for agent in agents if meeting.required_skill in agent.skills or meeting.required_skill == 'Monitoring']
            if eligible_agents:
                schedule[meeting] = random.choice(eligible_agents)
        population.append(schedule)
    return population

def fitness(schedule: Dict[Meeting, Agent], agents: List[Agent]) -> float:
    score = 0
    agent_schedules = {agent: {} for agent in agents}

    for meeting, agent in schedule.items():
        if meeting.required_skill not in agent.skills and meeting.required_skill != 'Monitoring':
            score -= 100

        date = meeting.start.date()
        if date not in agent_schedules[agent]:
            agent_schedules[agent][date] = []
        agent_schedules[agent][date].append(meeting)

        # Check for overlapping meetings
        for other_meeting in agent_schedules[agent][date]:
            if meeting != other_meeting and (meeting.start < other_meeting.end and meeting.end > other_meeting.start):
                score -= 50

    for agent, dates in agent_schedules.items():
        for date, meetings in dates.items():
            work_hours = sum((meeting.end - meeting.start).seconds / 3600 for meeting in meetings)
            if work_hours > 8:
                score -= (work_hours - 8) * 10

            # Check for proper breaks
            sorted_meetings = sorted(meetings, key=lambda m: m.start)
            for i in range(len(sorted_meetings) - 1):
                break_time = (sorted_meetings[i+1].start - sorted_meetings[i].end).seconds / 3600
                if break_time < 0.5:  # Less than 30 minutes break
                    score -= 25

    return score

def crossover(parent1: Dict[Meeting, Agent], parent2: Dict[Meeting, Agent]) -> Tuple[Dict[Meeting, Agent], Dict[Meeting, Agent]]:
    child1, child2 = {}, {}
    crossover_point = random.randint(0, len(parent1))

    items = list(parent1.items())
    child1.update(items[:crossover_point])
    child1.update({k: v for k, v in parent2.items() if k not in child1})

    items = list(parent2.items())
    child2.update(items[:crossover_point])
    child2.update({k: v for k, v in parent1.items() if k not in child2})

    return child1, child2

def mutate(schedule: Dict[Meeting, Agent], agents: List[Agent], mutation_rate: float):
    for meeting in schedule:
        if random.random() < mutation_rate:
            eligible_agents = [agent for agent in agents if meeting.required_skill in agent.skills or meeting.required_skill == 'Monitoring']
            if eligible_agents:
                schedule[meeting] = random.choice(eligible_agents)

def genetic_algorithm(agents: List[Agent], meetings: List[Meeting], pop_size: int, generations: int, mutation_rate: float) -> Dict[Meeting, Agent]:
    population = initialize_population(pop_size, agents, meetings)

    for _ in range(generations):
        population = sorted(population, key=lambda x: fitness(x, agents), reverse=True)
        new_population = population[:2]  # Keep the two best schedules

        while len(new_population) < pop_size:
            parent1, parent2 = random.sample(population[:pop_size // 2], 2)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1, agents, mutation_rate)
            mutate(child2, agents, mutation_rate)
            new_population.extend([child1, child2])

        population = new_population

    return max(population, key=lambda x: fitness(x, agents))

def assign_night_shifts(agents: List[Agent], meetings: List[Meeting]) -> Dict[Meeting, Agent]:
    night_meetings = [m for m in meetings if m.is_night]
    night_agents = [a for a in agents if "Security" in a.skills]
    
    night_schedule = {}
    for meeting in night_meetings:
        available_agents = [a for a in night_agents if meeting.start.date() not in a.schedule]
        if available_agents:
            assigned_agent = random.choice(available_agents)
            night_schedule[meeting] = assigned_agent
            if meeting.start.date() not in assigned_agent.schedule:
                assigned_agent.schedule[meeting.start.date()] = []
            assigned_agent.schedule[meeting.start.date()].append(meeting)
    
    return night_schedule

def run_scheduling_algorithm(agents: List[Agent], meetings: List[Meeting], pop_size: int = 50, generations: int = 100) -> Dict[Meeting, Agent]:
    # First, assign night shifts
    night_schedule = assign_night_shifts(agents, meetings)
    
    # Remove night meetings and update agent availability
    day_meetings = [m for m in meetings if not m.is_night]
    
    # Run genetic algorithm for day meetings
    day_schedule = genetic_algorithm(agents, day_meetings, pop_size=pop_size, generations=generations, mutation_rate=0.1)
    
    # Combine night and day schedules
    final_schedule = {**night_schedule, **day_schedule}
    
    return final_schedule