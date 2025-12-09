import sqlite3
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("music_app.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    favorite_mood TEXT,
    joined DATE NOT NULL
)
""")

# Create tracks/history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    mood TEXT NOT NULL,
    duration INTEGER NOT NULL,
    tempo INTEGER NOT NULL,
    instruments TEXT NOT NULL,
    audio_url TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()
