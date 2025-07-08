import sqlite3
from datetime import datetime

def get_conn():
    return sqlite3.connect('roadmap.db')

def init_roadmap_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        DROP TABLE IF EXISTS roadmap_branch_nodes
    ''')
    c.execute('''
        DROP TABLE IF EXISTS roadmap_main_nodes
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_main_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'todo',
            remark TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_branch_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_id INTEGER NOT NULL,
            target_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'todo',
            remark TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(main_id) REFERENCES roadmap_main_nodes(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_roadmap(user_id, target_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM roadmap_main_nodes WHERE user_id=? AND target_id=?', (user_id, target_id))
    mains = c.fetchall()
    # 如果没有主节点，自动插入一个
    if not mains:
        now = datetime.now().isoformat()
        c.execute('''
            INSERT INTO roadmap_main_nodes (user_id, target_id, title, status, remark, created_at, updated_at)
            VALUES (?, ?, ?, 'todo', '', ?, ?)
        ''', (user_id, target_id, '第一个技能点', now, now))
        conn.commit()
        c.execute('SELECT * FROM roadmap_main_nodes WHERE user_id=? AND target_id=?', (user_id, target_id))
        mains = c.fetchall()
    result = []
    for main in mains:
        main_id = main[0]
        c.execute('SELECT * FROM roadmap_branch_nodes WHERE main_id=? AND target_id=?', (main_id, target_id))
        branches = c.fetchall()
        result.append({
            'id': main[0],
            'title': main[3],
            'status': main[4],
            'remark': main[5],
            'children': [
                {
                    'id': b[0],
                    'title': b[3],
                    'status': b[4],
                    'remark': b[5]
                } for b in branches
            ]
        })
    conn.close()
    return result

def add_main_node(user_id, target_id, title):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        INSERT INTO roadmap_main_nodes (user_id, target_id, title, status, remark, created_at, updated_at)
        VALUES (?, ?, ?, 'todo', '', ?, ?)
    ''', (user_id, target_id, title, now, now))
    conn.commit()
    conn.close()
    return True

def add_branch_node(main_id, target_id, title):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        INSERT INTO roadmap_branch_nodes (main_id, target_id, title, status, remark, created_at, updated_at)
        VALUES (?, ?, ?, 'todo', '', ?, ?)
    ''', (main_id, target_id, title, now, now))
    conn.commit()
    conn.close()
    return True

def update_main_node(node_id, title, status, remark, target_id):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        UPDATE roadmap_main_nodes SET title=?, status=?, remark=?, updated_at=? WHERE id=? AND target_id=?
    ''', (title, status, remark, now, node_id, target_id))
    conn.commit()
    conn.close()
    return True

def update_branch_node(node_id, title, status, remark, target_id):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        UPDATE roadmap_branch_nodes SET title=?, status=?, remark=?, updated_at=? WHERE id=? AND target_id=?
    ''', (title, status, remark, now, node_id, target_id))
    conn.commit()
    conn.close()
    return True

def delete_main_node(node_id, target_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM roadmap_branch_nodes WHERE main_id=? AND target_id=?', (node_id, target_id))
    c.execute('DELETE FROM roadmap_main_nodes WHERE id=? AND target_id=?', (node_id, target_id))
    conn.commit()
    conn.close()
    return True

def delete_branch_node(node_id, target_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM roadmap_branch_nodes WHERE id=? AND target_id=?', (node_id, target_id))
    conn.commit()
    conn.close()
    return True
