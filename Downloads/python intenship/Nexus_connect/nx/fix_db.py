from app import app, db
from app import User, Task

# Run this script to recreate the database tables
with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    print('Database tables recreated successfully')