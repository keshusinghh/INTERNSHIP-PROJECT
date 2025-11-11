import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="postgre%40123"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'nexusdb'")
    exists = cursor.fetchone()
    
    if not exists:
        # Create database
        cursor.execute("CREATE DATABASE nexusdb")
        print("Database 'nexusdb' created successfully")
    else:
        print("Database 'nexusdb' already exists")
    
    # Close connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database initialization completed")