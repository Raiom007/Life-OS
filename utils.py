import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data"

SCHEMAS = {
    "body_gym.csv": ["date", "weight", "workout_type", "workout_completed", "energy_level"],
    "dsa_tracker.csv": ["date", "problem_name", "platform", "topic", "difficulty", "time_taken_mins", "solved_without_help", "revisited"],
    "ai_learning.csv": ["date", "topic_studied", "hours_studied", "implemented_code", "notes_written"],
    "mistake_log.csv": ["date", "problem_name", "topic", "mistake_type", "explanation", "fix_strategy", "resolved"]
}

def init_data_files():
    """Initializes the data directory and creates empty CSVs with schemas if they don't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for filename, columns in SCHEMAS.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            df = pd.DataFrame(columns=columns)
            df.to_csv(filepath, index=False)

def load_data(filename):
    """Loads a CSV file into a Pandas DataFrame."""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        # Read the file and parse dates if the date column exists
        return pd.read_csv(filepath)
    else:
        init_data_files()
        return pd.read_csv(filepath)

def save_data(filename, new_data_dict):
    """Appends a new row (dictionary) to the specified CSV."""
    # Ensure current date is set if not provided
    if "date" not in new_data_dict or not new_data_dict["date"]:
        new_data_dict["date"] = datetime.now().strftime("%Y-%m-%d")
        
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.DataFrame([new_data_dict])
    
    # If file exists, append; otherwise write new
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        df.to_csv(filepath, mode='a', header=False, index=False)
    else:
        df.to_csv(filepath, mode='w', header=True, index=False)
    
    return True
    
def update_data(filename, df):
    """Overwrites the specified CSV entirely with the provided DataFrame. Useful for editing existing records."""
    filepath = os.path.join(DATA_DIR, filename)
    df.to_csv(filepath, index=False)
    return True
