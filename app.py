import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from database import (
    init_db, fetch_all, get_weekly_summary, 
    insert_gym_log, insert_dsa_session, insert_ai_log, insert_mistake
)
from components import render_kpi, render_progress_bar, render_section_header, render_xp_bar, plotly_dark_theme
from analytics import (
    calculate_overall_scores, calculate_dsa_stats, calculate_gym_stats, 
    calculate_ai_stats, generate_radar_chart, 
    generate_insights, generate_habit_heatmap, get_weekly_date_range,
    process_daily_xp_and_streak, get_player_profile, get_xp_progress,
    get_weekly_boss, recalculate_difficulty
)

# Initialize Streamlit config
st.set_page_config(
    page_title="Rai Life OS",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
load_css()
init_db()

def page_dashboard():
    st.markdown("<h1>Command <span style='color: #6ba5ff;'>Center</span></h1>", unsafe_allow_html=True)
    
    # Process core RPG logic silently
    process_daily_xp_and_streak()
    
    # Recalculate Difficulty hook
    col_recalc, _ = st.columns([1, 4])
    with col_recalc:
        if st.button("Recalculate Difficulty", use_container_width=True):
            adj = recalculate_difficulty()
            if adj > 0:
                st.success(f"{adj} targets adjusted based on performance!")
            else:
                st.info("No adjustments needed.")
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # RPG Header
    profile = get_player_profile()
    level = profile.get("level", 1)
    xp = profile.get("total_xp", 0)
    streak = profile.get("current_streak", 0)
    pct_to_next = get_xp_progress(xp, level)
    
    render_xp_bar(level, xp, pct_to_next)
    
    # System Status / Insights
    insights = generate_insights()
    if insights:
        with st.container():
            st.markdown("<div style='background-color: #1a1e24; border-left: 4px solid #6ba5ff; padding: 1rem; border-radius: 4px; margin-bottom: 2rem;'>", unsafe_allow_html=True)
            for insight in insights:
                st.markdown(insight)
            st.markdown("</div>", unsafe_allow_html=True)

    scores = calculate_overall_scores()
    boss_info = get_weekly_boss()
    
    # KPI Row (RPG style)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi("Life Score", f"{scores['Overall']:.1f}", "Current Power")
    with col2:
        render_kpi("Active Streak", f"{streak}", "Days", "positive" if streak > 0 else "negative")
    with col3:
        render_kpi("Longest Streak", f"{profile.get('longest_streak', 0)}", "Record")
    with col4:
        # Boss panel mini
        boss_target = boss_info['target']
        domain_val = boss_info['domain_score']
        status = "Winning" if domain_val >= boss_target else "Losing"
        render_kpi("Active Boss", boss_info['boss_name'], status, "positive" if status == "Winning" else "negative")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        render_section_header("Performance Progress", "Weekly aggregates against targets")
        render_progress_bar("Health & Gym", scores["Health"], "#4ade80")
        render_progress_bar("DSA Prep", scores["DSA"], "#facc15")
        render_progress_bar("AI Learning", scores["AI"], "#6ba5ff")
        render_progress_bar("Discipline Score", scores["Overall"], "#a485ff")
        
    with col_right:
        render_section_header("Habit Heatmap", "Daily completion intensity")
        st.plotly_chart(generate_habit_heatmap(), use_container_width=True)

def page_gym():
    render_section_header("Body & Gym", "Track physical progress")
    
    with st.form("gym_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Daily Weight (kg/lbs)", min_value=0.0, format="%.1f")
            workout_type = st.selectbox("Workout Type", ["Push", "Pull", "Legs", "Cardio", "Rest"])
        with col2:
            completed = st.selectbox("Workout Completed?", ["Yes", "No", "N/A"])
            energy = st.slider("Energy Level", 1, 5, 3)
            
        if st.form_submit_button("Log Gym Data"):
            comp_int = 1 if completed == "Yes" else 0
            insert_gym_log(workout_type, comp_int, energy, weight)
            st.success("Gym data logged!")
            
    data = fetch_all("gym_logs")
    df = pd.DataFrame(data)
    if not df.empty and 'weight' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
        df = df.dropna(subset=['weight']).sort_values('date')
        if len(df) > 1:
            df['rolling_avg'] = df['weight'].rolling(window=7, min_periods=1).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['weight'], mode='markers+lines', name='Daily Weight', line=dict(color='#6ba5ff', width=1)))
            fig.add_trace(go.Scatter(x=df['date'], y=df['rolling_avg'], mode='lines', name='7-Day Avg', line=dict(color='#a485ff', width=3)))
            plotly_dark_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

def page_dsa():
    render_section_header("DSA Tracker", "Grind LeetCode, track patterns")
    
    with st.form("dsa_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Problem Name")
            platform = st.selectbox("Platform", ["LeetCode", "HackerRank", "Codeforces", "Other"])
            topic = st.selectbox("Topic", ["Arrays/Hashing", "Two Pointers", "Sliding Window", "Stack", "Binary Search", "Linked List", "Trees", "Tries", "Heap/PQ", "Backtracking", "Graphs", "Advanced Graphs", "1D DP", "2D DP", "Greedy", "Intervals", "Math & Geometry"])
        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            time_taken = st.number_input("Time Taken (mins)", min_value=1)
            solved_help = st.selectbox("Solved Without Help?", ["Yes", "No"])
            revisit = st.selectbox("Needs Revisit?", ["No", "Yes"])
            
        if st.form_submit_button("Log Problem"):
            help_int = 1 if solved_help == "Yes" else 0
            revisit_int = 1 if revisit == "Yes" else 0
            insert_dsa_session(name, platform, topic, difficulty, time_taken, help_int, revisit_int)
            st.success("DSA problem logged!")
            
    data = fetch_all("dsa_sessions")
    df = pd.DataFrame(data)
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Topic Distribution")
            counts = df['topic'].value_counts().reset_index()
            counts.columns = ['Topic', 'Count']
            fig = px.pie(counts, values='Count', names='Topic', color_discrete_sequence=px.colors.sequential.Purp)
            plotly_dark_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.write("### Difficulty")
            diff = df['difficulty'].value_counts().reset_index()
            diff.columns = ['Difficulty', 'Count']
            fig = px.bar(diff, x='Difficulty', y='Count', color='Difficulty', color_discrete_map={"Easy":"#4ade80", "Medium":"#facc15", "Hard":"#f87171"})
            plotly_dark_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

def page_ai():
    render_section_header("AI Learning", "Track AI/ML study progress")
    
    with st.form("ai_form", clear_on_submit=True):
        topic = st.text_input("Topic Studied (e.g., Transformers, RAG, PyTorch)")
        hours = st.number_input("Hours Studied", min_value=0.5, step=0.5)
        col1, col2 = st.columns(2)
        with col1:
            code = st.selectbox("Implemented Code?", ["Yes", "No"])
        with col2:
            notes = st.selectbox("Notes Written?", ["Yes", "No"])
            
        if st.form_submit_button("Log Study Session"):
            code_int = 1 if code == "Yes" else 0
            notes_int = 1 if notes == "Yes" else 0
            insert_ai_log(topic, hours, code_int, notes_int)
            st.success("Session logged!")
            
    data = fetch_all("ai_learning_logs")
    df = pd.DataFrame(data)
    if not df.empty:
        st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)

def page_mistakes():
    render_section_header("Mistake Log", "Analyze and fix conceptual gaps")
    
    with st.form("mistake_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Problem/Project Name")
            topic = st.text_input("Topic")
            mistake_type = st.selectbox("Mistake Type", ["Logic", "Edge Case", "Optimization", "Conceptual Gap", "Syntax"])
        with col2:
            explanation = st.text_input("Explanation / What went wrong?")
            fix = st.text_input("Fix Strategy / Lesson learned")
            resolved = st.selectbox("Resolved?", ["Yes", "No"])
            
        if st.form_submit_button("Log Mistake"):
            res_int = 1 if resolved == "Yes" else 0
            insert_mistake(name, topic, mistake_type, explanation, fix, res_int)
            st.success("Mistake logged!")

    data = fetch_all("mistake_logs")
    df = pd.DataFrame(data)
    if not df.empty:
        counts = df['mistake_type'].value_counts().reset_index()
        counts.columns = ['Type', 'Count']
        fig = px.bar(counts, x='Type', y='Count', title="Frequency of Mistakes by Type")
        plotly_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

def page_weekly():
    render_section_header("Weekly Analytics", "Deep dive into performance")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("### Balance Radar")
        st.plotly_chart(generate_radar_chart(), use_container_width=True)
    with col2:
        st.write("### Review Your Week")
        
        # Original metrics from memory structures
        scores = calculate_overall_scores()
        st.markdown(f"**Overall Discipline:** {scores['Overall']:.1f}%")
        st.markdown(f"**Health Check:** {scores['Health']:.1f}%")
        st.markdown(f"**DSA Target:** {scores['DSA']:.1f}%")
        st.markdown(f"**AI Target:** {scores['AI']:.1f}%")
        
        st.markdown("---")
        
        # New direct SQL summary feature requested
        start, end = get_weekly_date_range()
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        summary = get_weekly_summary(start_str, end_str)

        st.write("### SQLite Hard Weekly Summary")
        st.markdown(f"- **DSA Solved:** {summary['dsa_count_weekly']}")
        st.markdown(f"- **Gym Completion:** {summary['gym_completion_pct']:.1f}%")
        st.markdown(f"- **AI Total Hours:** {summary['ai_hours_weekly']}")

# Sidebar Navigation
st.sidebar.markdown("## Rai OS Navigation")
pages = {
    "Dashboard": page_dashboard,
    "Body & Gym": page_gym,
    "DSA Tracker": page_dsa,
    "AI Learning": page_ai,
    "Mistake Log": page_mistakes,
    "Weekly Analytics": page_weekly
}

selection = st.sidebar.radio("Go to", list(pages.keys()))

st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 High-Performance Build")

# Render selected page
pages[selection]()
