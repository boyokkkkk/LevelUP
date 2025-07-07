# app.py 完整修改版本

from flask import Blueprint, render_template, request, jsonify, send_file
import sqlite3
import os
from datetime import datetime
from contextlib import closing
from flask_cors import CORS

md_app = Blueprint('md_app', __name__)
CORS(md_app, supports_credentials=True)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 content TEXT,
                 parent_id INTEGER,
                 is_dir INTEGER DEFAULT 0,
                 tags TEXT DEFAULT '',
                 user_id TEXT DEFAULT '',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# 获取文件树
@md_app.route('/')
def index():
    return render_template('index_md.html')

# API: 获取文件列表
@md_app.route('/api/files', methods=['GET'])
def get_files():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "缺少user_id"}), 400
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, name, parent_id, is_dir, tags FROM files WHERE user_id=? ORDER BY is_dir DESC, name", (user_id,))
        files = [{"id": row[0], "name": row[1], "parent_id": row[2], "is_dir": bool(row[3]), "tags": row[4]} 
                for row in c.fetchall()]
        conn.close()
        return jsonify({"success": True, "data": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# API: 创建保存文件/目录
@md_app.route('/api/files', methods=['POST'])
def save_or_create_file():
    data = request.json
    name = data.get('name')
    content = data.get('content', '')
    tags = data.get('tags', '')
    user_id = data.get('user_id')
    if not name or not user_id:
        return jsonify({"success": False, "error": "文件名和user_id不能为空"}), 400
    if not name.endswith('.md'):
        name += '.md'
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("SELECT id FROM files WHERE name = ? AND user_id = ?", (name, user_id))
        existing_file = c.fetchone()
        if existing_file:
            return jsonify({"success": False, "error": "文件已存在"}), 409
        c.execute("""
            INSERT INTO files (name, content, tags, user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, content, tags, user_id, current_time, current_time))
        file_id = c.lastrowid
        conn.commit()
        c.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        file_data = c.fetchone()
        conn.close()
        return jsonify({
            "success": True,
            "message": "文件创建成功",
            "data": {
                "id": file_data[0],
                "name": file_data[1],
                "content": file_data[2],
                "parent_id": file_data[3],
                "is_dir": bool(file_data[4]),
                "tags": file_data[5],
                "user_id": file_data[6],
                "created_at": file_data[7],
                "updated_at": file_data[8]
            }
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": f"创建文件时出错: {str(e)}"}), 500

# API: 获取文件内容
@md_app.route('/api/files/<int:file_id>', methods=['GET'])
def get_file_content(file_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("""
            SELECT id, name, content, is_dir, parent_id, tags 
            FROM files 
            WHERE id = ?
        """, (file_id,))
        result = c.fetchone()
        conn.close()
        if not result:
            return jsonify({"success": False, "error": "文件不存在"}), 404
        file_id, name, content, is_dir, parent_id, tags = result
        return jsonify({
            "success": True,
            "data": {
                "id": file_id,
                "name": name,
                "content": content or "",
                "is_dir": bool(is_dir),
                "parent_id": parent_id,
                "tags": tags
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"获取文件内容失败: {str(e)}"}), 500

# API: 更新文件内容
@md_app.route('/api/files/<int:file_id>', methods=['PUT'])
def update_file_content(file_id):
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        tags = data.get('tags')
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"success": False, "error": "缺少user_id"}), 400
        if not name and not content and not tags:
            return jsonify({"success": False, "error": "必须提供name、content或tags字段"}), 400
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id FROM files WHERE id = ? AND user_id = ?", (file_id, user_id))
        if not c.fetchone():
            conn.close()
            return jsonify({"success": False, "error": "文件不存在或无权限"}), 404
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updates = []
        params = []
        if name:
            if not name.endswith('.md'):
                name += '.md'
            updates.append("name = ?")
            params.append(name)
        if content:
            updates.append("content = ?")
            params.append(content)
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        updates.append("updated_at = ?")
        params.append(current_time)
        sql = f"UPDATE files SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        params.append(file_id)
        params.append(user_id)
        c.execute(sql, params)
        conn.commit()
        c.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        file_data = c.fetchone()
        conn.close()
        return jsonify({
            "success": True,
            "message": "文件更新成功",
            "data": {
                "id": file_data[0],
                "name": file_data[1],
                "content": file_data[2],
                "parent_id": file_data[3],
                "is_dir": bool(file_data[4]),
                "tags": file_data[5],
                "user_id": file_data[6],
                "created_at": file_data[7],
                "updated_at": file_data[8]
            }
        })
    except Exception as e:
        if 'conn' in locals() and conn is not None:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

# API: 删除文件/目录
@md_app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "缺少user_id"}), 400
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT name FROM files WHERE id = ? AND user_id = ?", (file_id, user_id))
        file_name = c.fetchone()
        file_name = file_name[0] if file_name else "未知文件"
        c.execute("DELETE FROM files WHERE id = ? AND user_id = ?", (file_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({
                "success": True,
                "message": "文件删除成功",
                "data": {
                    "name": file_name
                }
            })
    except Exception as e:
        if 'conn' in locals() and conn is not None:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": f"删除文件失败: {str(e)}"}), 500

# 临时添加测试路由
@md_app.route('/test-db')
def test_db():
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, name, is_dir FROM files")
        files = c.fetchall()
        conn.close()
        return jsonify({"success": True, "data": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500