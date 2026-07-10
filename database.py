import sqlite3
import os
from datetime import datetime

DB_FILE = 'life_os.db'

def get_connection():
    """Returns a new connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def init_db():
    """Creates the SQLite database and all required tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dsa_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            problem_name TEXT,
            platform TEXT,
            topic TEXT,
            difficulty TEXT,
            time_taken INTEGER,
            solved_without_help INTEGER,
            revisited INTEGER
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gym_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            workout_type TEXT,
            completed INTEGER,
            energy_level INTEGER,
            weight REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_learning_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            topic TEXT,
            hours REAL,
            code_implemented INTEGER,
            notes_written INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mistake_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            area TEXT,
            topic TEXT,
            mistake_type TEXT,
            explanation TEXT,
            fix_strategy TEXT,
            resolved INTEGER
        )
    ''')

    # --- GAMIFICATION TABLES (v2.0) ---
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            domain_name TEXT,
            metric_name TEXT,
            target_type TEXT,
            target_value REAL,
            weight REAL,
            last_updated TIMESTAMP,
            PRIMARY KEY (domain_name, metric_name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_history (
            date TEXT PRIMARY KEY,
            life_score REAL,
            dsa_score REAL,
            gym_score REAL,
            ai_score REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1), -- Single row enforcement
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_active_date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_challenges (
            week_start TEXT PRIMARY KEY,
            boss_domain TEXT,
            defeated INTEGER DEFAULT 0,
            bonus_xp_awarded INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS target_adjustment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            metric TEXT,
            old_value REAL,
            new_value REAL,
            reason TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            name TEXT PRIMARY KEY,
            description TEXT,
            condition_logic TEXT,
            unlocked INTEGER DEFAULT 0,
            date_unlocked TEXT
        )
    ''')

    # Seed initial data
    _seed_initial_rpg_data(cursor)

    conn.commit()
    conn.close()

def _seed_initial_rpg_data(cursor):
    """Inserts default row for player_profile and default targets if empty."""
    cursor.execute("INSERT OR IGNORE INTO player_profile (id, total_xp, level, current_streak, longest_streak) VALUES (1, 0, 1, 0, 0)")
    
    # Check if targets exist
    cursor.execute("SELECT COUNT(*) FROM targets")
    if cursor.fetchone()[0] == 0:
        now = datetime.now()
        default_targets = [
            ("DSA", "weekly_total", "weekly", 7.0, 1.5, now), # 7 problems a week, High weight
            ("Gym", "completion_pct", "weekly", 100.0, 1.2, now), # Need 100% of 5 days, Med-high weight
            ("AI", "weekly_hours", "weekly", 10.0, 1.0, now) # 10 hours a week, Med weight
        ]
        cursor.executemany("INSERT INTO targets VALUES (?, ?, ?, ?, ?, ?)", default_targets)
        
        default_achievements = [
            ("First Blood", "Log your first entry", "logs_count >= 1", 0, None),
            ("Consistency is Key", "Hit a 7-day streak", "current_streak >= 7", 0, None),
            ("Algorithms Novice", "Solve 10 DSA Problems", "dsa_total >= 10", 0, None),
            ("Level 5 Reached", "Reach Level 5", "level >= 5", 0, None)
        ]
        cursor.executemany("INSERT INTO achievements VALUES (?, ?, ?, ?, ?)", default_achievements)

# --- INSERT FUNCTIONS ---

def _get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def insert_dsa_session(problem_name, platform, topic, difficulty, time_taken, solved_without_help, revisited, date=None):
    if date is None:
        date = _get_current_date()
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dsa_sessions (date, problem_name, platform, topic, difficulty, time_taken, solved_without_help, revisited)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, problem_name, platform, topic, difficulty, time_taken, solved_without_help, revisited))
    conn.commit()
    conn.close()

def insert_gym_log(workout_type, completed, energy_level, weight, date=None):
    if date is None:
        date = _get_current_date()
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO gym_logs (date, workout_type, completed, energy_level, weight)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, workout_type, completed, energy_level, weight))
    conn.commit()
    conn.close()

def insert_ai_log(topic, hours, code_implemented, notes_written, date=None):
    if date is None:
        date = _get_current_date()
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ai_learning_logs (date, topic, hours, code_implemented, notes_written)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, topic, hours, code_implemented, notes_written))
    conn.commit()
    conn.close()

def insert_mistake(area, topic, mistake_type, explanation, fix_strategy, resolved, date=None):
    if date is None:
        date = _get_current_date()
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mistake_logs (date, area, topic, mistake_type, explanation, fix_strategy, resolved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, area, topic, mistake_type, explanation, fix_strategy, resolved))
    conn.commit()
    conn.close()

# --- FETCH & ANALYTICS FUNCTIONS ---

def fetch_all(table_name):
    """Generic fetch for a single table. Returns a list of dictionaries mapping column to value."""
    # List of allowed tables to prevent SQL injection via table name
    allowed = ['dsa_sessions', 'gym_logs', 'ai_learning_logs', 'mistake_logs']
    if table_name not in allowed:
        return []
        
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_weekly_summary(start_date, end_date):
    """
    Returns custom weekly summary dictionary pulling directly via SQL for efficiency:
    - DSA count this week
    - Gym completion %
    - AI hours total
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. DSA Count
    cursor.execute("SELECT COUNT(*) FROM dsa_sessions WHERE date >= ? AND date <= ?", (start_date, end_date))
    dsa_count = cursor.fetchone()[0] or 0
    
    # 2. Gym Completion %
    cursor.execute("SELECT COUNT(*) FROM gym_logs WHERE date >= ? AND date <= ? AND completed = 1", (start_date, end_date))
    gym_completed_days = cursor.fetchone()[0] or 0
    # Assuming 5 is a target for a whole week, adjust as necessary based on logic.
    gym_pct = min(100.0, (gym_completed_days / 5.0) * 100)
    
    # 3. AI Hours
    cursor.execute("SELECT SUM(hours) FROM ai_learning_logs WHERE date >= ? AND date <= ?", (start_date, end_date))
    ai_hours = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        "dsa_count_weekly": dsa_count,
        "gym_completion_pct": gym_pct,
        "ai_hours_weekly": ai_hours
    }

def get_targets():
    """Returns all current targets mapping domain_name to dict of rules."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targets")
    rows = cursor.fetchall()
    conn.close()
    
    targets = {}
    for r in rows:
        d = dict(r)
        if d['domain_name'] not in targets:
            targets[d['domain_name']] = []
        targets[d['domain_name']].append(d)
    return targets

def update_target(domain_name, metric_name, old_value, new_value, reason):
    """Adjusts a target and logs it in the history table."""
    conn = get_connection()
    cursor = conn.cursor()
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Update targets table
    cursor.execute('''
        UPDATE targets 
        SET target_value = ?, last_updated = ?
        WHERE domain_name = ? AND metric_name = ?
    ''', (new_value, date_str, domain_name, metric_name))
    
    # 2. Log history
    cursor.execute('''
        INSERT INTO target_adjustment_history (date, metric, old_value, new_value, reason)
        VALUES (?, ?, ?, ?, ?)
    ''', (date_str, metric_name, old_value, new_value, reason))
    
    conn.commit()
    conn.close()

def get_target_history():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM target_adjustment_history ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_achievements():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM achievements")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
