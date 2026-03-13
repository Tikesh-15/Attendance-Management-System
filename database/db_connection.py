import sqlite3
import os

def get_connection():
    
    # Project root folder path
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Database file path
    db_path = os.path.join(base_path, "database.db")

    # Connect database
    conn = sqlite3.connect(db_path)

    # Enable foreign key
    conn.execute("PRAGMA foreign_keys = ON")

    return conn