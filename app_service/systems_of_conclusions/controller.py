from app_service import request, app, jwt_required, get_jwt_identity, jsonify
from app_service.systems_of_conclusions.service import ManagerSystemsOfConclusions

manager = ManagerSystemsOfConclusions()


# expert
@app.route('/conclusion', methods=['POST'])
@jwt_required
def registration_system():
    current_user = get_jwt_identity()
    if current_user[1] != 'Expert':
        return jsonify("Access denied"), 403
    system = manager.create_system_of_conclusions(request.json, current_user[0])
    return jsonify(manager.system_format_json_expert(system)), 200


# user
@app.route('/conclusion', methods=['GET'])
def get_systems():
    list_systems = manager.get_systems_overview()
    return jsonify([manager.system_format_json_user(system)
                    for system in list_systems]), 200


# expert
@app.route('/conclusion/<int:system_id>', methods=['GET'])
@jwt_required
def get_system(system_id):
    current_user = get_jwt_identity()
    if current_user[1] != 'Expert':
        return jsonify("Access denied"), 403
    system = manager.get_system(system_id)
    if system is None:
        return jsonify("Access denied"), 403
    if system.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return jsonify(manager.system_format_json_expert(system)), 200


# expert
@app.route('/conclusion/<int:system_id>', methods=['PUT'])
@jwt_required
def update_system(system_id):
    current_user = get_jwt_identity()
    if current_user[1] != 'Expert':
        return jsonify("Access denied"), 403
    system = manager.get_system(system_id)
    if system is None:
        return jsonify("Access denied"), 403
    if system.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return jsonify(manager.system_format_json_expert(
        manager.update_system_of_conclusions(system, request.json)
    )), 200


# user
@app.route('/conclusion/<int:system_id>', methods=['POST'])
@jwt_required
def get_conclusion(system_id):
    current_user = get_jwt_identity()
    recommendation = manager.make_fuzzy_conclusion(current_user[0], system_id, request.json['input'])
    return jsonify({'recommendation': recommendation}), 200


# expert
@app.route('/conclusion/<int:system_id>', methods=['DELETE'])
@jwt_required
def delete_system(system_id):
    current_user = get_jwt_identity()
    if current_user[1] != 'Expert':
        return jsonify("Access denied"), 403
    system = manager.get_system(system_id)
    if system.user_id != current_user[0] or system is None:
        return jsonify("Access denied"), 403
    return jsonify({'success': 1 if manager.delete_system(system) else 0}), 200


# user
@app.route('/conclusion/<int:system_id>/history', methods=['GET'])
@jwt_required
def get_history_conclusion_for_system(system_id):
    current_user = get_jwt_identity()
    history = manager.get_history_request_system_of_conclusions(current_user[0], system_id)
    return jsonify([manager.history_format_json(history_num) for history_num in history]), 200
