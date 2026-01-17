import sqlite3
import os

db_path = 'sql_app.db'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found in {os.getcwd()}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check prompt table
    cursor.execute("PRAGMA table_info(prompt)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Prompt columns: {columns}")
    
    if 'active_version_id' not in columns:
        print("Adding active_version_id to prompt...")
        cursor.execute("ALTER TABLE prompt ADD COLUMN active_version_id INTEGER")
    else:
        print("active_version_id already exists in prompt.")
        
    # Check promptversion table
    cursor.execute("PRAGMA table_info(promptversion)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"PromptVersion columns: {columns}")
    
    if 'commit_message' not in columns:
        print("Adding commit_message to promptversion...")
        cursor.execute("ALTER TABLE promptversion ADD COLUMN commit_message TEXT")
    else:
        print("commit_message already exists in promptversion.")
        
    conn.commit()
    conn.close()
    print("Database check complete.")
