from app_service.manager_users.service import ManagerUsers
from app_service import request, jsonify, jwt_required, get_jwt_identity, app

manager_users = ManagerUsers()


# user
@app.route('/user', methods=['POST'])
def registration_user():
    user = manager_users.create_user(request.json)
    if user is None:
        return jsonify("Bad request"), 400
    return jsonify(manager_users.user_format_json(user)), 201


# user
@app.route('/user/login', methods=['POST'])
def login_user():
    user_id, token = manager_users.sign_in(request.json)
    if user_id == -2:
        return jsonify("The user does not exist"), 400
    elif user_id == -1:
        return jsonify("Wrong password"), 400
    return jsonify({'token': token, 'id': user_id}), 200


# user
@app.route('/user/<int:user_id>', methods=['GET'])
@jwt_required
def get_info_user(user_id):
    current_user = get_jwt_identity()
    if user_id != current_user[0] and current_user[1] != 'Admin':
        return jsonify("Access denied"), 403
    user_info = manager_users.get_user(user_id)
    if user_info is None:
        return jsonify("The user does not exist"), 403
    user_format_dict = manager_users.user_format_json(user_info)
    user_format_dict['role'] = current_user[1]
    return user_format_dict, 200


# user
@app.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required
def update_info_user(user_id):
    current_user = get_jwt_identity()
    if user_id != current_user[0] and current_user[1] != 'Admin':
        return jsonify("Access denied"), 403
    user = manager_users.get_user(user_id)
    if user is None:
        return jsonify("The user does not exist"), 403
    return manager_users.user_format_json(manager_users.update_user(user_id, request.json, user)), 200


# user
@app.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required
def delete_user(user_id):
    current_user = get_jwt_identity()
    if user_id != current_user[0] and current_user[1] != 'Admin':
        return jsonify("Access denied"), 403
    return {'success': 0 if manager_users.delete_user(user_id) else 1}, 200


# admin
@app.route('/user/<int:user_id>/role', methods=['PUT'])
@jwt_required
def update_role(user_id):
    current_user = get_jwt_identity()
    if current_user[1] != 'Admin':
        return jsonify("Access denied"), 403
    if not(request.json['role'] in ['User', 'Expert', 'Researcher', 'Admin']):
        return jsonify("Error role"), 401
    return {'success': 0 if manager_users.update_role(user_id, request.json['role']) else 1}, 200
