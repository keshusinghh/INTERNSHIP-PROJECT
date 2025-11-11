import psycopg2
import os
from config import Config

def main():
    # Parse the PostgreSQL connection string
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_parts = db_uri.replace('postgresql://', '').split('/')
    db_credentials = db_parts[0].split('@')
    db_user_pass = db_credentials[0].split(':')
    db_host = db_credentials[1]
    db_name = db_parts[1]
    
    username = db_user_pass[0]
    password = db_user_pass[1]
    host = db_host
    database = db_name
    
    print(f"Connecting to PostgreSQL database: {host}/{database}")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=username,
        password=password
    )
    
    # Create a cursor
    cur = conn.cursor()
    
    # Check if team_visible column exists
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='tasks' AND column_name='team_visible';
    """)
    
    if cur.fetchone() is None:
        print("Adding team_visible column to tasks table...")
        # Add the team_visible column
        cur.execute("""
            ALTER TABLE tasks 
            ADD COLUMN team_visible BOOLEAN DEFAULT TRUE;
        """)
        conn.commit()
        print("Migration successful: team_visible column added to tasks table")
    else:
        print("team_visible column already exists in tasks table")
    
    # Close the connection
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()