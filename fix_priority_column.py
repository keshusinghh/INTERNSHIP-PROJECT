import sqlite3
import os

def migrate_priority():
    """Add priority column to tasks table if it doesn't exist"""
    try:
        # Connect to the SQLite database
        print("Connecting to SQLite database...")
        conn = sqlite3.connect('nexusboard.db')
        cursor = conn.cursor()
        
        # Check if priority column exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'priority' not in column_names:
            print("Adding priority column to tasks table...")
            # Add priority column with default value 'medium'
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")
            conn.commit()
            print("Successfully added priority column to tasks table.")
        else:
            print("Priority column already exists in tasks table.")
            
        cursor.close()
        conn.close()
        return True
    except Exception as error:
        print(f"Error: {error}")
        return False

if __name__ == "__main__":
    migrate_priority()