'''


'''
import os
import sqlite3
from sqlite3 import Error
from datetime import datetime

# Database file name
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "server_database.db")

# Create a connection to the SQLite database
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
    except Error as e:
        print(e)

    return conn

# Create the Users table
def create_users_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        is_confirmed BOOL NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# Create the Game History table
def create_game_history_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_type TEXT NOT NULL,
        result TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.commit()
    conn.close()

# Create the Ongoing Games table
def create_ongoing_games_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ongoing_games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_type TEXT NOT NULL,
        game_state TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

def create_chat_db():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        '''
    )

    conn.commit()
    conn.close()

# Add a user to the Users table
def add_user(username, password_hash, email, is_confirmed):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (username, password_hash, email, is_confirmed)
    VALUES (?, ?, ?, ?)
    """, (username, password_hash, email, is_confirmed))
    
    conn.commit()
    conn.close()

# Query user by username
def get_user_by_username(username):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    
    conn.close()
    
    return user

# Query user by email
def get_user_by_email(email):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    
    conn.close()
    
    return user

def store_chat_message(username, content, timestamp):
    conn = create_connection()
    cursor = conn.cursor()

    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Convert the datetime object to a string

    cursor.execute(
        "INSERT INTO messages (username, content, timestamp) VALUES (?, ?, ?)",
        (username, content, timestamp_str)
    )

    conn.commit()
    conn.close()


def get_messages():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username, content, timestamp FROM messages")

    messages = cursor.fetchall()
    conn.close()

    return messages

if __name__ == "__main__":
    # Create tables
    create_users_table()
    create_game_history_table()
    create_ongoing_games_table()
    create_chat_db()