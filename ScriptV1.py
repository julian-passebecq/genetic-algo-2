#ScriptV1.py
import datetime
import os
import pandas as pd
import plotly.express as px

from constants import AGENTS, APPOINTMENT_TYPES
from models import Agent, Meeting
from meeting_generator import generate_meetings
from genetic_algorithm import run_scheduling_algorithm
from visualization import create_schedule_dataframe, plot_schedule, plot_schedule_statistics, analyze_schedule, plot_fitness_history

# Function to set parameters
def set_parameters(num_agents=5, num_days=7, num_clients=5, population_size=50, num_generations=100):
    global PARAMS
    PARAMS = {
        'num_agents': num_agents,
        'num_days': num_days,
        'num_clients': num_clients,
        'population_size': population_size,
        'num_generations': num_generations
    }
    print("Parameters set successfully.")

# Function to generate and display meetings
def generate_and_display_meetings():
    start_date = datetime.date.today()
    global meetings
    meetings = generate_meetings(start_date, num_clients=PARAMS['num_clients'], days=PARAMS['num_days'])
    
    meetings_df = pd.DataFrame([
        {
            'Start': m.start,
            'End': m.end,
            'Type': m.required_skill,
            'Is Night': m.is_night,
            'Duration (hours)': (m.end - m.start).total_seconds() / 3600
        } for m in meetings
    ])
    
    print(f"Generated {len(meetings)} meetings")
    print(meetings_df.to_string(index=False))  # Print all rows to the console
    
    # Create a calendar view of the meetings
    fig = px.timeline(meetings_df, x_start="Start", x_end="End", y="Type", color="Is Night",
                      title="Generated Meetings Calendar")
    fig.update_yaxes(categoryorder="category ascending")
    
    # Add vertical lines for day boundaries
    for day in pd.date_range(meetings_df['Start'].min(), meetings_df['End'].max()):
        fig.add_vline(x=day.replace(hour=5, minute=0), line_dash="dash", line_color="gray")
    
    # Update x-axis to show date on bottom and time on top
    fig.update_xaxes(
        tickformat="%H:%M",
        tickangle=0,
        tickfont=dict(size=10),
        showgrid=True,
        gridcolor='lightgray'
    )
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=False),
            tickformat="%Y-%m-%d"
        ),
        xaxis2=dict(
            overlaying="x",
            side="top",
            tickformat="%H:%M",
            showgrid=False
        )
    )
    
    fig.show()
    
    return meetings_df

# Function to run algorithm
def run_algorithm():
    global agents, meetings, schedule_df, fitness_history
    if 'meetings' not in globals() or meetings is None:
        print("Please generate meetings first.")
        return

    # Create agent objects
    agents = [Agent(f"Agent{i+1}", AGENTS[f"Agent{i+1}"]) for i in range(PARAMS['num_agents'])]

    print(f"Running algorithm with {len(agents)} agents and {len(meetings)} meetings")

    # Run the scheduling algorithm
    final_schedule, fitness_history = run_scheduling_algorithm(agents, meetings, 
                                                               pop_size=PARAMS['population_size'], 
                                                               generations=PARAMS['num_generations'])

    print(f"Scheduled {len(final_schedule)} meetings")
    print(f"Final fitness score: {fitness_history[-1]}")
    
    # Create and display schedule dataframe
    schedule_df = create_schedule_dataframe(final_schedule)
    print(schedule_df.to_string(index=False))  # Print all rows to the console
    
    # Plot fitness history
    fig = plot_fitness_history(fitness_history)
    fig.show()
    
    # Analyze the schedule
    analyze_schedule(schedule_df)
    
    return schedule_df

# Function to visualize results
def visualize_results():
    global schedule_df
    if 'schedule_df' not in globals() or schedule_df is None:
        print("Please run the scheduling algorithm first to generate a schedule.")
        return
    
    # Plot the schedule (calendar view)
    fig = plot_schedule(schedule_df)
    fig.show()

    # Plot additional statistics
    stats_fig = plot_schedule_statistics(schedule_df)
    stats_fig.show()

# Function to analyze results
def analyze_results():
    global schedule_df
    if 'schedule_df' not in globals() or schedule_df is None:
        print("Please run the scheduling algorithm first to generate a schedule.")
        return
    
    analyze_schedule(schedule_df)

# Function to save results to CSV
def save_results(meetings_df, schedule_df):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join("results", timestamp)
    os.makedirs(results_dir, exist_ok=True)
    
    meetings_file = os.path.join(results_dir, "meetings.csv")
    schedule_file = os.path.join(results_dir, "schedule.csv")
    
    meetings_df.to_csv(meetings_file, index=False)
    schedule_df.to_csv(schedule_file, index=False)
    
    print(f"Results saved to {results_dir}")

# Main function to execute all steps
def main():
    set_parameters()
    meetings_df = generate_and_display_meetings()
    schedule_df = run_algorithm()
    visualize_results()
    analyze_results()
    save_results(meetings_df, schedule_df)

if __name__ == "__main__":
    main()
