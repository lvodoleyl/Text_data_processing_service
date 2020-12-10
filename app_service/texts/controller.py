from app_service.texts.service import ManagerTexts
from app_service import request, app, jwt_required, get_jwt_identity, jsonify

manager_texts = ManagerTexts()


# user
@app.route('/texts', methods=['POST'])
@jwt_required
def post_text():
    current_user = get_jwt_identity()
    return manager_texts.text_format_json(
        manager_texts.registration_text(request.json["text"],
                                        current_user[0])
    ), 200


# user
@app.route('/texts', methods=['GET'])
@jwt_required
def get_all_user_texts():
    current_user = get_jwt_identity()
    return jsonify([{"id": text.id, "text": text.text} for text in
                    manager_texts.get_list_of_texts(current_user[0])]), 200


# admin
@app.route('/texts/all', methods=['GET'])
@jwt_required
def get_all_texts():
    current_user = get_jwt_identity()
    if current_user[1] != "Admin":
        return jsonify("Access denied"), 403
    return jsonify([manager_texts.text_format_json(text) for text in
                    manager_texts.get_list_all_texts()]), 200


# user
@app.route('/texts/<int:text_id>', methods=['GET'])
@jwt_required
def get_text(text_id):
    current_user = get_jwt_identity()
    text = manager_texts.get_text(text_id)
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return jsonify(manager_texts.text_format_json(text)), 200


# user
@app.route('/texts/<int:text_id>', methods=['PUT'])
@jwt_required
def update_text(text_id):
    current_user = get_jwt_identity()
    text = manager_texts.get_text(text_id)
    if text is None:
        return jsonify("The text does not exist"), 403
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return manager_texts.text_format_json(
        manager_texts.update_text(request.json, text)
    ), 200


# user
@app.route('/texts/<int:text_id>', methods=['DELETE'])
@jwt_required
def delete_text(text_id):
    current_user = get_jwt_identity()
    text = manager_texts.get_text(text_id)
    if text is None:
        return jsonify("The text does not exist"), 403
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return {'success': 0 if manager_texts.delete_text(text) else 1}, 200
