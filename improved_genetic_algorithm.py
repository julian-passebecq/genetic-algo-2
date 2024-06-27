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

def crossover(parent1: Dict[Meeting, Agent], parent2: Dict[Meeting, Agent]) -> Tuple[Dict[Meeting, Agent], Dict[Meeting, Agent]]:
    crossover_point = random.randint(0, len(parent1))
    child1 = dict(list(parent1.items())[:crossover_point] + list(parent2.items())[crossover_point:])
    child2 = dict(list(parent2.items())[:crossover_point] + list(parent1.items())[crossover_point:])
    return child1, child2

def mutate(schedule: Dict[Meeting, Agent], agents: List[Agent], mutation_rate: float):
    for meeting in schedule:
        if random.random() < mutation_rate:
            eligible_agents = [agent for agent in agents if meeting.required_skill in agent.skills or meeting.required_skill == 'Monitoring']
            if eligible_agents:
                schedule[meeting] = random.choice(eligible_agents)

def genetic_algorithm(agents: List[Agent], meetings: List[Meeting], pop_size: int, generations: int, mutation_rate: float) -> Tuple[Dict[Meeting, Agent], List[float]]:
    population = initialize_population(pop_size, agents, meetings)
    best_fitness_history = []

    for gen in range(generations):
        population = sorted(population, key=lambda x: fitness(x, agents), reverse=True)
        best_fitness_history.append(fitness(population[0], agents))
        
        new_population = population[:2]  # Elitism: keep the two best schedules

        while len(new_population) < pop_size:
            parent1, parent2 = random.sample(population[:pop_size // 2], 2)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1, agents, mutation_rate)
            mutate(child2, agents, mutation_rate)
            new_population.extend([child1, child2])

        population = new_population

    best_schedule = max(population, key=lambda x: fitness(x, agents))
    return best_schedule, best_fitness_history

def run_scheduling_algorithm(agents: List[Agent], meetings: List[Meeting], pop_size: int = 100, generations: int = 200) -> Tuple[Dict[Meeting, Agent], List[float]]:
    return genetic_algorithm(agents, meetings, pop_size=pop_size, generations=generations, mutation_rate=0.1)



from typing import List, Dict
from models import Agent, Meeting
import datetime

def fitness(schedule: Dict[Meeting, Agent], agents: List[Agent]) -> float:
    score = 0
    agent_schedules = {agent: {} for agent in agents}
    agent_night_shifts = {agent: 0 for agent in agents}

    for meeting, agent in schedule.items():
        date = meeting.start.date()
        if date not in agent_schedules[agent]:
            agent_schedules[agent][date] = []
        agent_schedules[agent][date].append(meeting)

        if meeting.is_night:
            agent_night_shifts[agent] += 1

        # Check skill matching
        if meeting.required_skill not in agent.skills and meeting.required_skill != 'Monitoring':
            score -= 1000  # Heavy penalty for skill mismatch

    for agent, dates in agent_schedules.items():
        for date, meetings in dates.items():
            sorted_meetings = sorted(meetings, key=lambda m: m.start)
            day_hours = sum((meeting.end - meeting.start).total_seconds() / 3600 for meeting in meetings if not meeting.is_night)
            night_meetings = [m for m in meetings if m.is_night]

            # Check for night shift and day shift conflict
            if night_meetings and len(meetings) > 1:
                score -= 2000  # Heavy penalty for having both night and day shifts

            # Check daily working hours
            if day_hours > 10:
                score -= (day_hours - 10) * 100
            elif day_hours < 6:
                score -= (6 - day_hours) * 50

            # Check for overlapping meetings
            for i in range(len(sorted_meetings) - 1):
                if sorted_meetings[i].end > sorted_meetings[i+1].start:
                    score -= 1000  # Heavy penalty for overlapping meetings

            # Check for proper breaks between meetings
            for i in range(len(sorted_meetings) - 1):
                break_time = (sorted_meetings[i+1].start - sorted_meetings[i].end).total_seconds() / 3600
                if break_time < 0.5:  # Less than 30 minutes break
                    score -= 500

    # Check for 3 night shifts per week
    for agent, night_shifts in agent_night_shifts.items():
        if night_shifts != 3:
            score -= abs(night_shifts - 3) * 200

    return score