import sqlite3
import os

DB_PATH = "instalkalk.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabulka projektů
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabulka položek v projektu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            shop TEXT,
            url TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')
    
    conn.commit()
    conn.close()

if not os.path.exists(DB_PATH):
    init_db()
