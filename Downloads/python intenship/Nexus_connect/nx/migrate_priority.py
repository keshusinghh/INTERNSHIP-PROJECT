import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_params = {
    'dbname': os.getenv('DB_NAME', 'nexusboard'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def migrate_priority():
    """Add priority column to tasks table if it doesn't exist"""
    conn = None
    try:
        # Connect to the database
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Check if priority column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='tasks' AND column_name='priority';
        """)
        
        if cur.fetchone() is None:
            print("Adding priority column to tasks table...")
            # Add priority column with default value 'medium'
            cur.execute("""
                ALTER TABLE tasks 
                ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium';
            """)
            conn.commit()
            print("Successfully added priority column to tasks table.")
        else:
            print("Priority column already exists in tasks table.")
            
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    migrate_priority()