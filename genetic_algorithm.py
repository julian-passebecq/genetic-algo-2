import random
import logging
from typing import List, Dict, Tuple
import datetime
from constants import AGENTS, MAX_DAILY_HOURS, MIN_DAILY_HOURS, IDEAL_DAILY_HOURS, MIN_BREAK_TIME, TRAVEL_TIME, MAX_CONSECUTIVE_DAYS, MAX_WEEKLY_HOURS, PENALTY_WEIGHT

logging.basicConfig(filename='genetic_algorithm.log', level=logging.DEBUG)

def fitness(schedule: Dict[int, str], meetings: List[Dict]) -> Tuple[float, Dict]:
    score = 0
    breakdown = {
        "scheduled_meetings": 0,
        "skill_mismatches": 0,
        "overwork": 0,
        "underwork": 0,
        "uneven_distribution": 0,
        "break_violations": 0,
        "uneven_night_shifts": 0
    }
    agent_schedules = {agent: {} for agent in AGENTS}
    night_shift_counts = {agent: 0 for agent in AGENTS}

    for i, agent in schedule.items():
        meeting = meetings[i]
        date = meeting['start'].date()
        if date not in agent_schedules[agent]:
            agent_schedules[agent][date] = []
        agent_schedules[agent][date].append(meeting)

        if meeting['required_skill'] not in AGENTS[agent] and meeting['required_skill'] != 'Monitoring':
            score -= PENALTY_WEIGHT['skill_mismatch']
            breakdown["skill_mismatches"] += 1

    for agent, dates in agent_schedules.items():
        weekly_hours = 0
        consecutive_days = 0
        prev_date = None
        for date, day_meetings in sorted(dates.items()):
            day_meetings.sort(key=lambda x: x['start'])
            daily_hours = sum((m['end'] - m['start']).total_seconds() / 3600 for m in day_meetings)
            weekly_hours += daily_hours

            if daily_hours > MAX_DAILY_HOURS:
                score -= PENALTY_WEIGHT['overwork'] * (daily_hours - MAX_DAILY_HOURS)
                breakdown["overwork"] += daily_hours - MAX_DAILY_HOURS
            elif daily_hours < MIN_DAILY_HOURS:
                score -= PENALTY_WEIGHT['underwork'] * (MIN_DAILY_HOURS - daily_hours)
                breakdown["underwork"] += MIN_DAILY_HOURS - daily_hours

            for i in range(len(day_meetings) - 1):
                break_time = (day_meetings[i+1]['start'] - day_meetings[i]['end']).total_seconds() / 3600
                if break_time < MIN_BREAK_TIME + TRAVEL_TIME:
                    score -= PENALTY_WEIGHT['break_violation']
                    breakdown["break_violations"] += 1

            night_shifts = sum(1 for m in day_meetings if m['is_night'])
            night_shift_counts[agent] += night_shifts

    workloads = [len(dates) for dates in agent_schedules.values()]
    avg_workload = sum(workloads) / len(workloads)
    uneven_distribution = sum(abs(w - avg_workload) for w in workloads)
    score -= PENALTY_WEIGHT['uneven_distribution'] * uneven_distribution
    breakdown["uneven_distribution"] = uneven_distribution

    avg_night_shifts = sum(night_shift_counts.values()) / len(night_shift_counts)
    uneven_night_shifts = sum(abs(n - avg_night_shifts) for n in night_shift_counts.values())
    score -= PENALTY_WEIGHT['uneven_night_shifts'] * uneven_night_shifts
    breakdown["uneven_night_shifts"] = uneven_night_shifts

    scheduled_meetings = len(schedule)
    score += scheduled_meetings * PENALTY_WEIGHT['scheduled_meeting']
    breakdown["scheduled_meetings"] = scheduled_meetings

    return score, breakdown

def initialize_population(pop_size: int, meetings: List[Dict]) -> List[Dict[int, str]]:
    population = []
    for _ in range(pop_size):
        schedule = {}
        for i, meeting in enumerate(meetings):
            if random.random() < 0.8:  # 80% chance to schedule a meeting
                schedule[i] = random.choice(list(AGENTS.keys()))
        population.append(schedule)
    return population

def crossover(parent1: Dict[int, str], parent2: Dict[int, str]) -> Tuple[Dict[int, str], Dict[int, str]]:
    child1, child2 = {}, {}
    for key in set(parent1.keys()) | set(parent2.keys()):
        if random.random() < 0.5:
            if key in parent1:
                child1[key] = parent1[key]
            if key in parent2:
                child2[key] = parent2[key]
        else:
            if key in parent2:
                child1[key] = parent2[key]
            if key in parent1:
                child2[key] = parent1[key]
    return child1, child2

def mutate(schedule: Dict[int, str], meetings: List[Dict], mutation_rate: float):
    for i in range(len(meetings)):
        if random.random() < mutation_rate:
            if i in schedule:
                if random.random() < 0.5:
                    del schedule[i]
                else:
                    schedule[i] = random.choice(list(AGENTS.keys()))
            else:
                schedule[i] = random.choice(list(AGENTS.keys()))

def repair_schedule(schedule: Dict[int, str], meetings: List[Dict]) -> Dict[int, str]:
    agent_schedules = {agent: [] for agent in AGENTS}
    for i, agent in schedule.items():
        agent_schedules[agent].append(meetings[i])
    
    for agent, agent_meetings in agent_schedules.items():
        agent_meetings.sort(key=lambda x: x['start'])
        for i in range(len(agent_meetings) - 1):
            if agent_meetings[i]['end'] > agent_meetings[i+1]['start']:
                del schedule[meetings.index(agent_meetings[i+1])]
    
    return schedule

def genetic_algorithm(meetings: List[Dict], pop_size: int, generations: int, mutation_rate: float) -> Tuple[Dict[int, str], List[float], List[Dict[int, str]]]:
    population = initialize_population(pop_size, meetings)
    best_fitness_history = []
    top_3_schedules = []

    for gen in range(generations):
        population = sorted(population, key=lambda x: fitness(x, meetings)[0], reverse=True)
        best_fitness, breakdown = fitness(population[0], meetings)
        best_fitness_history.append(best_fitness)
        
        logging.info(f"Generation {gen}: Best fitness = {best_fitness}")
        logging.info(f"Fitness breakdown: {breakdown}")

        if gen % 100 == 0:
            print(f"Generation {gen}: Best fitness = {best_fitness}")
            print("Fitness breakdown:", breakdown)

        top_3_schedules = population[:3]

        new_population = population[:2]

        while len(new_population) < pop_size:
            parent1, parent2 = random.sample(population[:pop_size // 2], 2)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1, meetings, mutation_rate)
            mutate(child2, meetings, mutation_rate)
            child1 = repair_schedule(child1, meetings)
            child2 = repair_schedule(child2, meetings)
            new_population.extend([child1, child2])

        population = new_population

    best_schedule = max(population, key=lambda x: fitness(x, meetings)[0])
    return best_schedule, best_fitness_history, top_3_schedules

def run_scheduling_algorithm(meetings: List[Dict], pop_size: int = 300, generations: int = 2000) -> Tuple[Dict[int, str], List[float], List[Dict[int, str]]]:
    return genetic_algorithm(meetings, pop_size=pop_size, generations=generations, mutation_rate=0.1)