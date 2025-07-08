import sqlite3
from datetime import datetime

def get_conn():
    return sqlite3.connect('database.db')

def init_todo_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_todos(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, text, completed, created_at FROM todos WHERE user_id=? ORDER BY id DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [
        {'id': row[0], 'text': row[1], 'completed': bool(row[2]), 'created_at': row[3]}
        for row in rows
    ]

def add_todo(user_id, text):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO todos (user_id, text, completed, created_at) VALUES (?, ?, 0, ?)', (user_id, text, now))
    conn.commit()
    conn.close()
    return True

def update_todo(todo_id, completed, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE todos SET completed=? WHERE id=? AND user_id=?', (int(completed), todo_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_todo(todo_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id=? AND user_id=?', (todo_id, user_id))
    conn.commit()
    conn.close()
    return True 