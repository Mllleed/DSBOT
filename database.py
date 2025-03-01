import sqlite3

def create_connection():
    conn = sqlite3.connect('server_logs.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_action(user_id, username, action):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (user_id, username, action)
        VALUES (?, ?, ?)
    ''', (user_id, username, action))
    conn.commit()
    conn.close()

# Создаем таблицу при первом запуске

