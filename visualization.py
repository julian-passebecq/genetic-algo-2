import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_top_3_schedules(top_3_schedules, meetings):
    fig = make_subplots(rows=3, cols=1, subplot_titles=['Best Schedule', '2nd Best Schedule', '3rd Best Schedule'])

    for i, schedule in enumerate(top_3_schedules, start=1):
        schedule_df = create_schedule_dataframe(schedule, meetings)
        for agent in schedule_df['Agent'].unique():
            agent_schedule = schedule_df[schedule_df['Agent'] == agent]
            fig.add_trace(
                go.Bar(x=[agent_schedule['Start'], agent_schedule['End']], 
                       y=[agent] * len(agent_schedule), 
                       orientation='h', 
                       name=agent,
                       text=agent_schedule['Type'],
                       hoverinfo='text'),
                row=i, col=1
            )

    fig.update_layout(height=1200, title_text="Top 3 Schedules")
    return fig

# ... (rest of the visualization.py file)


def create_schedule_dataframe(schedule, meetings):
    df = pd.DataFrame([
        {
            'Agent': agent,
            'Start': meetings[i]['start'],
            'End': meetings[i]['end'],
            'Type': meetings[i]['required_skill'],
            'Is Night': meetings[i]['is_night'],
            'Duration': (meetings[i]['end'] - meetings[i]['start']).total_seconds() / 3600
        }
        for i, agent in schedule.items()
    ])
    return df

def plot_schedule(schedule_df):
    fig = go.Figure()

    for agent in schedule_df['Agent'].unique():
        agent_schedule = schedule_df[schedule_df['Agent'] == agent]
        fig.add_trace(go.Bar(
            x=[agent_schedule['Start'], agent_schedule['End']],
            y=[agent] * len(agent_schedule),
            orientation='h',
            name=agent,
            text=agent_schedule['Type'],
            hoverinfo='text',
            marker=dict(
                color=agent_schedule['Is Night'].map({True: 'rgba(0,0,255,0.5)', False: 'rgba(0,255,0,0.5)'}),
                line=dict(
                    color=agent_schedule['Is Night'].map({True: 'blue', False: 'green'}),
                    width=2
                )
            )
        ))

    # Add vertical lines for day boundaries
    for day in pd.date_range(schedule_df['Start'].min(), schedule_df['End'].max()):
        fig.add_shape(
            type="line",
            x0=day,
            x1=day,
            y0=0,
            y1=len(schedule_df['Agent'].unique()),
            line=dict(color="Gray", width=1, dash="dot")
        )

    # Add vertical lines for night shift boundaries
    night_shifts = schedule_df[schedule_df['Is Night']]
    for _, shift in night_shifts.iterrows():
        fig.add_shape(
            type="line",
            x0=shift['Start'],
            x1=shift['Start'],
            y0=0,
            y1=len(schedule_df['Agent'].unique()),
            line=dict(color="Blue", width=2, dash="solid")
        )
        fig.add_shape(
            type="line",
            x0=shift['End'],
            x1=shift['End'],
            y0=0,
            y1=len(schedule_df['Agent'].unique()),
            line=dict(color="Blue", width=2, dash="solid")
        )

    fig.update_layout(
        title="Security Company Schedule",
        xaxis_title="Date",
        yaxis_title="Agent",
        barmode='overlay',
        height=800,
        width=1200,
        showlegend=False
    )

    return fig

def plot_schedule_statistics(schedule_df):
    # Create a subplot with 2 rows and 2 columns
    fig = make_subplots(rows=2, cols=2, subplot_titles=(
        "Meetings per Agent", "Night Shifts per Agent", 
        "Average Working Hours per Agent", "Daily Working Hours per Agent"
    ))

    # Meetings per agent
    meetings_per_agent = schedule_df['Agent'].value_counts().reset_index()
    meetings_per_agent.columns = ['Agent', 'Number of Meetings']
    fig.add_trace(go.Bar(x=meetings_per_agent['Agent'], y=meetings_per_agent['Number of Meetings'], name='Meetings'), row=1, col=1)

    # Night shifts per agent
    night_shifts = schedule_df[schedule_df['Is Night']]['Agent'].value_counts().reset_index()
    night_shifts.columns = ['Agent', 'Number of Night Shifts']
    fig.add_trace(go.Bar(x=night_shifts['Agent'], y=night_shifts['Number of Night Shifts'], name='Night Shifts'), row=1, col=2)

    # Average working hours per agent
    avg_hours = schedule_df.groupby('Agent')['Duration'].mean().reset_index()
    avg_hours.columns = ['Agent', 'Average Working Hours']
    fig.add_trace(go.Bar(x=avg_hours['Agent'], y=avg_hours['Average Working Hours'], name='Working Hours'), row=2, col=1)

    # Daily working hours per agent
    daily_hours = schedule_df.groupby(['Agent', pd.to_datetime(schedule_df['Start']).dt.date])['Duration'].sum().reset_index()
    fig.add_trace(go.Box(x=daily_hours['Agent'], y=daily_hours['Duration'], name='Daily Hours'), row=2, col=2)

    fig.update_layout(height=800, width=1200, title_text="Schedule Statistics")
    return fig

def analyze_schedule(schedule_df):
    # Total meetings per agent
    meetings_per_agent = schedule_df['Agent'].value_counts().sort_index()
    print("Meetings per agent:")
    print(meetings_per_agent)
    print()

    # Night shifts per agent
    night_shifts = schedule_df[schedule_df['Is Night']]['Agent'].value_counts().sort_index()
    print("Night shifts per agent:")
    print(night_shifts)
    print()

    # Average working hours per agent
    avg_hours = schedule_df.groupby('Agent')['Duration'].mean().sort_index()
    print("Average working hours per agent:")
    print(avg_hours)
    print()

    # Daily working hours per agent
    daily_hours = schedule_df.groupby(['Agent', pd.to_datetime(schedule_df['Start']).dt.date])['Duration'].sum()
    print("Daily working hours per agent:")
    print(daily_hours)
    print()

    # Meeting statistics
    total_meetings = len(schedule_df)
    filled_meetings = schedule_df['Agent'].notna().sum()
    fill_rate = filled_meetings / total_meetings * 100

    print(f"Total meetings planned: {total_meetings}")
    print(f"Meetings filled: {filled_meetings}")
    print(f"Fill rate: {fill_rate:.2f}%")
    print()

    # Average workload per agent
    avg_workload = meetings_per_agent.mean()
    print(f"Average workload (meetings per agent): {avg_workload:.2f}")

def plot_fitness_history(fitness_history):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=fitness_history, mode='lines', name='Best Fitness'))
    fig.update_layout(title='Fitness History', xaxis_title='Generation', yaxis_title='Fitness Score')
    return fig