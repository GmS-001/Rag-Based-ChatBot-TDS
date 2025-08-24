# database_utils.py

import sqlite3
import bcrypt

DB_NAME = 'chatbot.db'

def get_db_connection():
    """Establishes a connection to the database."""
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    """Creates the users and threads tables if they don't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, password):
    """Hashes a password and adds a new user to the database."""
    if not username or not password:
        return False, "Username and password are required."
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password.decode('utf-8')))
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def verify_user(username, password):
    """Verifies a user's credentials against the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    user_record = cursor.fetchone()
    conn.close()
    
    if user_record:
        hashed_password = user_record[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
    return False

def add_thread_for_user(thread_id, username):
    """Links a new chat thread_id to a username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO threads (thread_id, username) VALUES (?, ?)", (thread_id, username))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
        
def retrieve_user_threads(username):
    """Retrieves all chat thread_ids for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT thread_id FROM threads WHERE username = ?", (username,))
    threads = [row[0] for row in cursor.fetchall()]
    conn.close()
    return threads