import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from database import fetch_all

def get_weekly_date_range():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def filter_current_week(df, date_col="date"):
    if df.empty or date_col not in df.columns:
        return df
    df[date_col] = pd.to_datetime(df[date_col])
    start, end = get_weekly_date_range()
    mask = (df[date_col] >= start) & (df[date_col] <= end)
    return df.loc[mask]

def calculate_dsa_stats():
    data = fetch_all("dsa_sessions")
    df = pd.DataFrame(data)
    if df.empty:
        return {"streak": 0, "weekly_total": 0, "weakest_topic": "N/A"}
        
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date', ascending=False)
    
    # Calculate streak (consecutive days)
    unique_dates = df['date'].dt.date.unique()
    streak = 0
    today = datetime.now().date()
    current_check = today
    
    # Check if they solved today or yesterday
    if today in unique_dates or (today - timedelta(days=1)) in unique_dates:
        if today in unique_dates:
            streak = 1
            current_check = today - timedelta(days=1)
        else:
            streak = 1
            current_check = today - timedelta(days=2)
            
        while current_check in unique_dates:
            streak += 1
            current_check -= timedelta(days=1)
            
    # Weekly total
    weekly_df = filter_current_week(df)
    weekly_total = len(weekly_df)
    
    # Weakest topic (based on time taken or not solved without help)
    weakest_topic = "N/A"
    if not df.empty:
        # High time taken or needed help implies weakness
        if 'solved_without_help' in df.columns and 'topic' in df.columns:
            weak_df = df[df['solved_without_help'] == 'No']
            if not weak_df.empty:
                weakest_topic = weak_df['topic'].value_counts().idxmax()
            else:
                weakest_topic = df['topic'].value_counts().idxmax() # default to most practiced
                
    return {"streak": streak, "weekly_total": weekly_total, "weakest_topic": weakest_topic}

def calculate_gym_stats():
    data = fetch_all("gym_logs")
    df = pd.DataFrame(data)
    if df.empty:
        return {"completion_pct": 0, "trend": []}
        
    weekly_df = filter_current_week(df)
    if weekly_df.empty:
        return {"completion_pct": 0, "trend": []}
        
    completed = weekly_df[weekly_df['completed'] == 1].shape[0]
    # Assuming user wants to work out 5 days a week
    pct = min(100, (completed / 5) * 100)
    
    return {"completion_pct": pct}

def calculate_ai_stats():
    data = fetch_all("ai_learning_logs")
    df = pd.DataFrame(data)
    if df.empty:
        return {"weekly_hours": 0}
        
    weekly_df = filter_current_week(df)
    if weekly_df.empty:
        return {"weekly_hours": 0}
        
    hours = pd.to_numeric(weekly_df['hours'], errors='coerce').sum()
    return {"weekly_hours": hours}

def calculate_overall_scores():
    gym = calculate_gym_stats()
    dsa = calculate_dsa_stats()
    ai = calculate_ai_stats()
    
    health_score = gym['completion_pct']
        
    dsa_target = 7
    dsa_score = min(100.0, (dsa['weekly_total'] / dsa_target) * 100)
    
    ai_target = 10
    ai_score = min(100.0, (ai['weekly_hours'] / ai_target) * 100)
    
    weights = {"Health": 0.4, "DSA": 0.4, "AI": 0.2}
    overall = (health_score * weights["Health"] + 
               dsa_score * weights["DSA"] + 
               ai_score * weights["AI"])
               
    return {
        "Health": health_score,
        "DSA": dsa_score,
        "AI": ai_score,
        "Overall": min(100.0, overall)
    }

# --- RPG ENGINE LOGIC (v2.0) ---

def process_daily_xp_and_streak():
    """Calculates Life Score, awards XP, handles streak logic, and levels up player."""
    from database import get_connection
    scores = calculate_overall_scores()
    life_score = scores["Overall"]
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Check if already processed today
    cursor.execute("SELECT date FROM performance_history WHERE date = ?", (today,))
    if cursor.fetchone():
        conn.close()
        return  # Already granted XP today
        
    # 2. Log Performance
    cursor.execute('''
        INSERT INTO performance_history (date, life_score, dsa_score, gym_score, ai_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (today, life_score, scores["DSA"], scores["Health"], scores["AI"]))
    
    # 3. Calculate XP & Streak
    xp_earned = int(life_score * 10)
    
    cursor.execute("SELECT total_xp, level, current_streak, longest_streak FROM player_profile WHERE id = 1")
    profile = cursor.fetchone()
    if profile:
        total_xp, level, current_streak, longest_streak = profile
        
        # Intelligent Streak: only increments if life score >= 70%
        if life_score >= 70:
            current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
        else:
            current_streak = 0
            
        new_total_xp = total_xp + xp_earned
        
        # Level Formula: floor(sqrt(total_xp / 100))
        # Ensure minimum level 1
        import math
        new_level = max(1, math.floor(math.sqrt(new_total_xp / 100)))
        
        cursor.execute('''
            UPDATE player_profile 
            SET total_xp = ?, level = ?, current_streak = ?, longest_streak = ?, last_active_date = ?
            WHERE id = 1
        ''', (new_total_xp, new_level, current_streak, longest_streak, today))
        
    conn.commit()
    conn.close()

def get_player_profile():
    from database import get_connection
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM player_profile WHERE id=1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {"level": 1, "total_xp": 0, "current_streak": 0}

def get_xp_progress(total_xp, level):
    """Calculates exactly how much XP is needed for the NEXT level to build a progress bar."""
    import math
    current_level_base_xp = (level ** 2) * 100
    next_level_base_xp = ((level + 1) ** 2) * 100
    
    xp_into_level = total_xp - current_level_base_xp
    xp_needed_for_level = next_level_base_xp - current_level_base_xp
    
    # percentage 0-100
    if xp_needed_for_level <= 0: return 100
    return min(100, int((xp_into_level / xp_needed_for_level) * 100))

def recalculate_difficulty():
    """Adaptive Target Engine. Evaluates 7-day performance and scales up/down targets."""
    from database import get_targets, update_target
    targets = get_targets()
    scores = calculate_overall_scores()  # Using standard scores conceptually as 7-day average proxy for MVP
    
    adjustments_made = 0
    # DSA Logic
    if "DSA" in targets and len(targets["DSA"]) > 0:
        dsa_t = targets["DSA"][0]
        cur_val = dsa_t["target_value"]
        if scores["DSA"] >= 100: # Overperforming
            update_target("DSA", "weekly_total", cur_val, round(cur_val * 1.05, 1), "Overperforming (+5%)")
            adjustments_made += 1
        elif scores["DSA"] <= 80: # Underperforming
            update_target("DSA", "weekly_total", cur_val, round(cur_val * 0.95, 1), "Underperforming (-5%)")
            adjustments_made += 1
            
    # Gym Logic
    if "Gym" in targets and len(targets["Gym"]) > 0:
        gym_t = targets["Gym"][0]
        cur_val = gym_t["target_value"]
        if scores["Health"] >= 100: 
            update_target("Gym", "completion_pct", cur_val, cur_val, "Maxed Out Gym")
        elif scores["Health"] <= 80:
            update_target("Gym", "completion_pct", cur_val, round(cur_val * 0.95, 1), "Underperforming (-5%)")
            adjustments_made += 1
            
    # AI Logic
    if "AI" in targets and len(targets["AI"]) > 0:
        ai_t = targets["AI"][0]
        cur_val = ai_t["target_value"]
        if scores["AI"] >= 100:
            update_target("AI", "weekly_hours", cur_val, round(cur_val * 1.05, 1), "Overperforming (+5%)")
            adjustments_made += 1
        elif scores["AI"] <= 80:
            update_target("AI", "weekly_hours", cur_val, round(cur_val * 0.95, 1), "Underperforming (-5%)")
            adjustments_made += 1

    return adjustments_made

def get_weekly_boss():
    """Determines the weakest domain and sets it as the boss."""
    from database import get_connection
    scores = calculate_overall_scores()
    
    weakest_domain = min([("Gym / Health", scores["Health"]), 
                          ("DSA / Logic", scores["DSA"]), 
                          ("AI / Knowledge", scores["AI"])], key=lambda x: x[1])
                          
    boss_name = f"{weakest_domain[0]} Mastery Boss"
    
    # Store in DB if it's a new week
    start, _ = get_weekly_date_range()
    week_str = start.strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO weekly_challenges (week_start, boss_domain, defeated) VALUES (?, ?, ?)", 
                  (week_str, boss_name, 0))
    conn.commit()
    conn.close()
    
    return {
        "boss_name": boss_name,
        "domain_score": weakest_domain[1],
        "target": 80.0
    }

def generate_radar_chart():
    scores = calculate_overall_scores()
    
    fig = go.Figure(data=go.Scatterpolar(
        r=[scores["Health"], scores["DSA"], scores["AI"], scores["Health"]], # duplicate first to close loop
        theta=['Health/Gym', 'DSA/LeetCode', 'AI/Learning', 'Health/Gym'],
        fill='toself',
        fillcolor='rgba(107, 165, 255, 0.4)',
        line=dict(color='#6ba5ff', width=2)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color='#a0aec0',
                gridcolor='#2d3748'
            ),
            angularaxis=dict(
                color='#e2e8f0',
                gridcolor='#2d3748'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def generate_insights():
    scores = calculate_overall_scores()
    dsa = calculate_dsa_stats()
    
    insights = []
    
    # Weakness
    weak_cat = min([("Health", scores["Health"]), ("DSA", scores["DSA"]), ("AI", scores["AI"])], key=lambda x: x[1])
    insights.append(f"⚠️ **Weakness Detected:** Your {weak_cat[0]} score is lagging ({weak_cat[1]:.1f}%). Focus on this area next week.")
    
    if dsa["streak"] == 0:
        insights.append(f"🚨 **Consistency Warning:** Your DSA streak broke. Solve a quick Easy problem today to get back on track.")
    elif dsa["streak"] > 3:
        insights.append(f"🔥 **Momentum:** Strong DSA streak ({dsa['streak']} days). Keep the momentum going!")
        
    if dsa["weakest_topic"] != "N/A":
        insights.append(f"🧠 **Skill Gap:** Your weakest DSA topic seems to be '{dsa['weakest_topic']}'. Review fundamental patterns.")
        
    # Improvement suggestion
    if scores["Health"] < 50:
        insights.append("💡 **Actionable Plan:** Schedule your workouts and commit to 15 mins a day to build the habit.")
        
    return insights

def generate_habit_heatmap():
    """Generates a GitHub style heatmap data (mocked for visual for MVP)"""
    # In a real app this would aggregate daily scores for the past 6 months
    # Here we mock 30 days of activity intensity (0 to 4)
    dates = [datetime.now() - timedelta(days=x) for x in range(30)]
    np.random.seed(42) # Consistent mock for now until we have lots of real data
    intensity = np.random.randint(0, 5, 30)
    
    df = pd.DataFrame({"Date": dates, "Intensity": intensity})
    df = df.sort_values(by="Date")
    
    fig = px.density_heatmap(df, x="Date", y="Intensity", color_continuous_scale="Viridis")
    fig.update_layout(coloraxis_showscale=False, yaxis_visible=False)
    # This is a basic plot, a true github heatmap is a 2D grid calendar. We will use a scatter for better visuals.
    
    # Better approach for GitHub like style using Scatter:
    df['Week'] = df['Date'].dt.isocalendar().week
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    
    fig2 = go.Figure(data=go.Scatter(
        x=df['Week'],
        y=df['DayOfWeek'],
        mode='markers',
        marker=dict(
            size=15,
            color=df['Intensity'],
            colorscale=[[0, '#15181d'], [0.25, '#1e3a8a'], [0.5, '#3b82f6'], [0.75, '#60a5fa'], [1, '#93c5fd']],
            showscale=False,
            symbol='square'
        ),
        text=df['Date'].dt.strftime('%b %d') + "<br>Intensity: " + df['Intensity'].astype(str),
        hoverinfo='text'
    ))
    
    fig2.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, tickmode='array', tickvals=[0,1,2,3,4,5,6], ticktext=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=200,
        margin=dict(l=40, r=0, t=0, b=0)
    )
    return fig2
