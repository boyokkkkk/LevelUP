import sqlite3
import os
from datetime import datetime

def init_target_db():
    """初始化学习目标数据库"""
    conn = sqlite3.connect('targets.db')
    c = conn.cursor()
    
    # 创建学习目标表
    c.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            progress REAL DEFAULT 0,
            tags TEXT,
            update_time TEXT,
            user_id TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_target(title, progress, tags, user_id):
    """添加新的学习目标"""
    try:
        conn = sqlite3.connect('targets.db')
        c = conn.cursor()
        
        # 将标签列表转换为字符串存储
        tags_str = ','.join(tags)
        update_time = datetime.now().strftime('%Y-%m-%d')
        
        c.execute('''
            INSERT INTO targets (title, progress, tags, update_time, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, progress, tags_str, update_time, user_id))
        
        conn.commit()
        conn.close()
        return True, "添加成功"
    except Exception as e:
        return False, f"添加失败: {str(e)}"

def get_targets(user_id):
    """获取指定用户的所有学习目标"""
    try:
        conn = sqlite3.connect('targets.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM targets WHERE user_id = ?', (user_id,))
        targets = c.fetchall()
        
        # 将数据库结果转换为字典列表
        result = []
        for target in targets:
            result.append({
                'id': target[0],
                'title': target[1],
                'progress': target[2],
                'tags': target[3].split(',') if target[3] else [],
                'update': target[4],
                'user_id': target[5]
            })
        
        conn.close()
        return result
    except Exception as e:
        print(f"获取学习目标失败: {str(e)}")
        return []

def update_target(target_id, title, progress, tags, user_id):
    """更新学习目标"""
    try:
        conn = sqlite3.connect('targets.db')
        c = conn.cursor()
        
        # 确保只能更新自己的学习目标
        c.execute('SELECT user_id FROM targets WHERE id = ?', (target_id,))
        result = c.fetchone()
        if not result or result[0] != user_id:
            return False, "无权更新此学习目标"
        
        tags_str = ','.join(tags)
        update_time = datetime.now().strftime('%Y-%m-%d')
        
        c.execute('''
            UPDATE targets 
            SET title = ?, progress = ?, tags = ?, update_time = ?
            WHERE id = ? AND user_id = ?
        ''', (title, progress, tags_str, update_time, target_id, user_id))
        
        conn.commit()
        conn.close()
        return True, "更新成功"
    except Exception as e:
        return False, f"更新失败: {str(e)}"

def delete_target(target_id, user_id):
    """删除学习目标"""
    try:
        conn = sqlite3.connect('targets.db')
        c = conn.cursor()
        
        # 确保只能删除自己的学习目标
        c.execute('SELECT user_id FROM targets WHERE id = ?', (target_id,))
        result = c.fetchone()
        if not result or result[0] != user_id:
            return False, "无权删除此学习目标"
        
        c.execute('DELETE FROM targets WHERE id = ? AND user_id = ?', (target_id, user_id))
        
        conn.commit()
        conn.close()
        return True, "删除成功"
    except Exception as e:
        return False, f"删除失败: {str(e)}"

def search_targets(query, user_id):
    """搜索学习目标"""
    try:
        conn = sqlite3.connect('targets.db')
        c = conn.cursor()
        
        # 在标题和标签中搜索
        search_pattern = f'%{query}%'
        c.execute('''
            SELECT * FROM targets 
            WHERE user_id = ? AND (title LIKE ? OR tags LIKE ?)
        ''', (user_id, search_pattern, search_pattern))
        
        targets = c.fetchall()
        
        # 将数据库结果转换为字典列表
        result = []
        for target in targets:
            result.append({
                'id': target[0],
                'title': target[1],
                'progress': target[2],
                'tags': target[3].split(',') if target[3] else [],
                'update': target[4],
                'user_id': target[5]
            })
        
        conn.close()
        return result
    except Exception as e:
        print(f"搜索学习目标失败: {str(e)}")
        return [] 