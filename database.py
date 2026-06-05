import sqlite3
from datetime import datetime

DB_NAME = "interview.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            technology TEXT,
            difficulty TEXT,
            score INTEGER,
            strengths TEXT,
            weaknesses TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_interview(technology, difficulty, score, strengths, weaknesses):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO interviews (date, technology, difficulty, score, strengths, weaknesses)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date_str, technology, difficulty, score, strengths, weaknesses))
    conn.commit()
    conn.close()

def get_all_interviews():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interviews ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
