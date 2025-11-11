import sqlite3

def migrate_priority():
    """Add priority column to tasks table if it doesn't exist"""
    try:
        # Connect to SQLite database
        print("Connecting to SQLite database...")
        conn = sqlite3.connect('nexusboard.db')
        cursor = conn.cursor()
        
        # Check if priority column exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'priority' not in columns:
            print("Adding priority column to tasks table...")
            # Add priority column with default value 'medium'
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'")
            conn.commit()
            print("Successfully added priority column to tasks table.")
        else:
            print("Priority column already exists in tasks table.")
            
        cursor.close()
        conn.close()
        print("Database connection closed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate_priority()