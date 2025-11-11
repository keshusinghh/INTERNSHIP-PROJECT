import os
import psycopg2
from psycopg2 import sql

def migrate_database():
    """Add is_admin column to users table if it doesn't exist"""
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
        # Check if is_admin column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_admin'
        """)
        column_exists = cursor.fetchone() is not None
        
        if not column_exists:
            print("Adding is_admin column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            print("Migration successful: is_admin column added to users table")
        else:
            print("is_admin column already exists in users table")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        # Close the connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_database()