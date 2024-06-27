import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_schedule_dataframe(schedule):
    data = []
    for meeting, agent in schedule.items():
        duration = (meeting.end - meeting.start).total_seconds() / 3600
        if meeting.end < meeting.start:  # Meeting crosses midnight
            duration = (meeting.end + datetime.timedelta(days=1) - meeting.start).total_seconds() / 3600
        data.append({
            'Agent': agent.id,
            'Start': meeting.start,
            'End': meeting.end,
            'Type': meeting.required_skill,
            'Is Night': meeting.is_night,
            'Duration': duration
        })
    return pd.DataFrame(data)

def plot_schedule(schedule_df):
    fig = px.timeline(schedule_df, x_start="Start", x_end="End", y="Agent", color="Type",
                      hover_data=["Is Night"],
                      title="Security Company Schedule")
    fig.update_yaxes(categoryorder="category ascending")
    
    # Add vertical lines for day boundaries
    for day in pd.date_range(schedule_df['Start'].min(), schedule_df['End'].max()):
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
    
    return fig

def plot_schedule_statistics(schedule_df):
    # Create a subplot with 1 row and 3 columns
    fig = make_subplots(rows=1, cols=3, subplot_titles=("Meetings per Agent", "Night Shifts per Agent", "Average Working Hours per Agent"))

    # Meetings per agent
    meetings_per_agent = schedule_df['Agent'].value_counts().reset_index()
    meetings_per_agent.columns = ['Agent', 'Number of Meetings']
    fig.add_trace(go.Bar(x=meetings_per_agent['Agent'], y=meetings_per_agent['Number of Meetings'], name='Meetings'), row=1, col=1)

    # Night shifts per agent
    night_shifts = schedule_df[schedule_df['Is Night']]['Agent'].value_counts().reset_index()
    night_shifts.columns = ['Agent', 'Number of Night Shifts']
    fig.add_trace(go.Bar(x=night_shifts['Agent'], y=night_shifts['Number of Night Shifts'], name='Night Shifts'), row=1, col=2)

    # Average working hours per agent
    schedule_df['Duration'] = (schedule_df['End'] - schedule_df['Start']).dt.total_seconds() / 3600
    avg_hours = schedule_df.groupby('Agent')['Duration'].mean().reset_index()
    avg_hours.columns = ['Agent', 'Average Working Hours']
    fig.add_trace(go.Bar(x=avg_hours['Agent'], y=avg_hours['Average Working Hours'], name='Working Hours'), row=1, col=3)

    fig.update_layout(height=400, width=1200, title_text="Schedule Statistics")
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