import os
import psycopg2
from psycopg2 import sql

def migrate_tasks_table():
    """Add created_at and updated_at columns to tasks table if they don't exist"""
    # Get the database connection string from the environment or use the default
    db_uri = os.environ.get('DATABASE_URL', 'postgresql://postgres:root%40123@localhost/vijay')
    
    # Replace postgres:// with postgresql:// if needed
    if db_uri.startswith('postgres://'):
        db_uri = db_uri.replace('postgres://', 'postgresql://', 1)
    
    # Parse the connection string
    if db_uri.startswith('postgresql://'):
        # Extract connection parameters from URI
        # Format: postgresql://username:password@host:port/dbname
        uri_parts = db_uri.replace('postgresql://', '').split('@')
        credentials = uri_parts[0].split(':')
        host_db = uri_parts[1].split('/')
        
        username = credentials[0]
        password = credentials[1] if len(credentials) > 1 else ''
        
        host_port = host_db[0].split(':')
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'
        
        dbname = host_db[1]
        
        print(f"Connecting to PostgreSQL database: {host}/{dbname}")
        
        # Connect to the database
        conn = psycopg2.connect(
            dbname=dbname,
            user=username,
            password=password,
            host=host,
            port=port
        )
    else:
        print(f"Unsupported database URI: {db_uri}")
        return
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Check if created_at column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tasks' AND column_name = 'created_at'
        """)
        created_at_exists = cursor.fetchone() is not None
        
        # Check if updated_at column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tasks' AND column_name = 'updated_at'
        """)
        updated_at_exists = cursor.fetchone() is not None
        
        # Add created_at column if it doesn't exist
        if not created_at_exists:
            print("Adding created_at column to tasks table...")
            cursor.execute("ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("Migration successful: created_at column added to tasks table")
        else:
            print("created_at column already exists in tasks table")
        
        # Add updated_at column if it doesn't exist
        if not updated_at_exists:
            print("Adding updated_at column to tasks table...")
            cursor.execute("ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("Migration successful: updated_at column added to tasks table")
        else:
            print("updated_at column already exists in tasks table")
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        # Close the connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_tasks_table()