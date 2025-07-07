from flask import Flask, Blueprint, request, jsonify
from backend.services.roadmap_service import (
    get_roadmap, add_main_node, add_branch_node,
    update_main_node, update_branch_node, delete_main_node, delete_branch_node
)

roadmap_app = Blueprint('roadmap_app', __name__)

@roadmap_app.route('/roadmap', methods=['GET'])
def api_get_roadmap():
    user_id = request.args.get('user_id')
    target_id = request.args.get('target_id', 'testtarget')
    return jsonify(get_roadmap(user_id, target_id))

@roadmap_app.route('/roadmap/main', methods=['POST'])
def api_add_main_node():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    target_id = data.get('target_id', 'testtarget')
    if not user_id or not title or not target_id:
        return jsonify({'success': False, 'error': 'user_id、技能点标题和目标ID不能为空'})
    add_main_node(user_id, target_id, title)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/branch', methods=['POST'])
def api_add_branch_node():
    data = request.get_json()
    user_id = data.get('user_id')
    main_id = data.get('main_id')
    title = data.get('title')
    target_id = data.get('target_id', 'testtarget')
    if not user_id or not main_id or not title or not target_id:
        return jsonify({'success': False, 'error': 'user_id、分技能点参数不完整'})
    add_branch_node(main_id, target_id, title)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/main/<int:node_id>', methods=['PUT'])
def api_update_main_node(node_id):
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    status = data.get('status')
    remark = data.get('remark', '')
    target_id = data.get('target_id', 'testtarget')
    if not user_id or not title or not status or not target_id:
        return jsonify({'success': False, 'error': 'user_id、参数不完整'})
    update_main_node(node_id, title, status, remark, target_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/branch/<int:node_id>', methods=['PUT'])
def api_update_branch_node(node_id):
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    status = data.get('status')
    remark = data.get('remark', '')
    target_id = data.get('target_id', 'testtarget')
    if not user_id or not title or not status or not target_id:
        return jsonify({'success': False, 'error': 'user_id、参数不完整'})
    update_branch_node(node_id, title, status, remark, target_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/main/<int:node_id>', methods=['DELETE'])
def api_delete_main_node(node_id):
    user_id = request.args.get('user_id')
    target_id = request.args.get('target_id', 'testtarget')
    delete_main_node(node_id, target_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/branch/<int:node_id>', methods=['DELETE'])
def api_delete_branch_node(node_id):
    user_id = request.args.get('user_id')
    target_id = request.args.get('target_id', 'testtarget')
    delete_branch_node(node_id, target_id)
    return jsonify({'success': True}) 