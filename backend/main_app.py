from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.sign_in_service import init_user_db, add_user, verify_user
from backend.services.target_service import init_target_db, add_target, get_targets, update_target, delete_target, search_targets
from backend.roadmap_app import roadmap_app
from backend.md_app import md_app, init_db

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于session加密

# 配置CORS
CORS(app, supports_credentials=True)

# 修改session配置
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 改为Lax
app.config['SESSION_COOKIE_SECURE'] = False    # 开发环境设为False
app.config['SESSION_COOKIE_HTTPONLY'] = True   # 增加安全性
app.config['SESSION_COOKIE_DOMAIN'] = None     # 允许所有域名

# 初始化数据库
init_user_db()
init_target_db()
init_db()

# 登录验证装饰器
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': '请先登录'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'error': '用户名和密码不能为空'})
    
    success, message = add_user(username, password)
    if success:
        return jsonify({'success': True, 'message': '注册成功'})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'error': '用户名和密码不能为空'})
    
    success, message = verify_user(username, password)
    if success:
        session['user_id'] = username
        return jsonify({
            'success': True, 
            'message': '登录成功',
            'user': {'username': username}
        })
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': '退出成功'})

@app.route('/check_login', methods=['GET'])
def check_login():
    if 'user_id' in session:
        return jsonify({
            'success': True, 
            'user': {'username': session['user_id']}
        })
    return jsonify({'success': False, 'error': '未登录'})

@app.route('/targets', methods=['GET'])
@login_required
def get_user_targets():
    user_id = session['user_id']
    targets = get_targets(user_id)
    return jsonify(targets)

@app.route('/targets', methods=['POST'])
@login_required
def create_target():
    user_id = session['user_id']
    data = request.get_json()
    
    title = data.get('title')
    progress = data.get('progress', 0)
    tags = data.get('tags', [])
    
    if not title:
        return jsonify({'success': False, 'error': '标题不能为空'})
    
    success, message = add_target(title, progress, tags, user_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/targets/<int:target_id>', methods=['PUT'])
@login_required
def update_user_target(target_id):
    user_id = session['user_id']
    data = request.get_json()
    
    title = data.get('title')
    progress = data.get('progress', 0)
    tags = data.get('tags', [])
    
    if not title:
        return jsonify({'success': False, 'error': '标题不能为空'})
    
    success, message = update_target(target_id, title, progress, tags, user_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/targets/<int:target_id>', methods=['DELETE'])
@login_required
def delete_user_target(target_id):
    user_id = session['user_id']
    success, message = delete_target(target_id, user_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/search', methods=['GET'])
@login_required
def search_user_targets():
    user_id = session['user_id']
    query = request.args.get('query', '')
    
    if not query:
        targets = get_targets(user_id)
    else:
        targets = search_targets(query, user_id)
    
    return jsonify(targets)

app.register_blueprint(roadmap_app)
app.register_blueprint(md_app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
