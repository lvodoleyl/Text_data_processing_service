from threading import Thread
from app_service.annotation.service import ManagerAnnotation, ManagerOfModels
from app_service import request, app, jwt_required, get_jwt_identity, jsonify

annotation_manager = ManagerAnnotation()
models_manager = ManagerOfModels()


# user
@app.route('/annotation', methods=['GET'])
@jwt_required
def get_annotation_texts():
    current_user = get_jwt_identity()
    result = annotation_manager.get_list_request_for_annotation(current_user[0])
    print(result)
    return jsonify([annotation_manager.annotation_format_json(text, text.annotate)
                    for text in result]), 200


# user TODO queue Threads
@app.route('/annotation', methods=['POST'])
@jwt_required
def registering_request_to_annotation():
    current_user = get_jwt_identity()
    text = annotation_manager.get_text(request.json["text_id"])
    if text is None:
        return jsonify("The text does not exist"), 403
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    del text
    run_create_annotation = Thread(target=annotation_manager.request_for_annotation, args=(request.json["text_id"],))
    run_create_annotation.start()
    return jsonify({'success': 1}), 200


# user
@app.route('/annotation/<int:request_id>', methods=['GET'])
@jwt_required
def get_request_to_annotation(request_id):
    current_user = get_jwt_identity()
    annotated, text = annotation_manager.get_result_annotation(request_id)
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return jsonify(annotation_manager.annotation_format_json(text, annotated)), 200


# user
@app.route('/annotation/<int:request_id>', methods=['DELETE'])
@jwt_required
def delete_request_to_annotation(request_id):
    return jsonify({'success': 0 if annotation_manager.delete_request_annotation(request_id) else 1}), 200


# researcher
@app.route('/annotation/test_model', methods=['GET'])
@jwt_required
def get_testing_texts_all():
    current_user = get_jwt_identity()
    if current_user[1] != 'Researcher':
        return jsonify("Access denied"), 403
    texts = models_manager.get_list_texts_for_assessment(current_user[0])
    return jsonify([annotation_manager.annotation_format_json(text, text.annotate)
                    for text in texts]), 200


# researcher
@app.route('/annotation/test_model', methods=['POST'])
@jwt_required
def registration_testing_texts():
    current_user = get_jwt_identity()
    if current_user[1] != 'Researcher':
        return jsonify("Access denied"), 403
    text, annotation = models_manager.register_text_for_assessment(request.json['text'], request.json['true_text'],
                                                                   current_user[0], 0)
    return jsonify(models_manager.annotation_format_json(text, annotation)), 200


# researcher
@app.route('/annotation/test_model/<int:text_test_id>', methods=['GET'])
@jwt_required
def get_test_text(text_test_id):
    current_user = get_jwt_identity()
    if current_user[1] != 'Researcher':
        return jsonify("Access denied"), 403
    text = models_manager.get_text_for_assessment(text_test_id)
    if text is None:
        return jsonify("The text does not exist"), 403
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return jsonify(models_manager.annotation_format_json(text, text.annotate)), 200


# researcher
@app.route('/annotation/test_model/<int:text_test_id>', methods=['PUT'])
@jwt_required
def update_test_text(text_test_id):
    current_user = get_jwt_identity()
    if current_user[1] != 'Researcher':
        return jsonify("Access denied"), 403
    text = models_manager.get_text_for_assessment(text_test_id)
    if text is None:
        return jsonify("The text does not exist"), 403
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    text_update, annotation = models_manager.update_text_for_assessment(request.json, text)
    return jsonify(models_manager.annotation_format_json(text_update, annotation)), 200


# researcher
@app.route('/annotation/test_model/<int:text_test_id>', methods=['DELETE'])
@jwt_required
def delete_test_text(text_test_id):
    current_user = get_jwt_identity()
    if current_user[1] != 'Researcher':
        return jsonify("Access denied"), 403
    text = models_manager.get_text_for_assessment(text_test_id)
    if text is None:
        return jsonify("The text does not exist"), 403
    if text.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return models_manager.delete_text(text), 200


# researcher
@app.route('/annotation/test_model/quality', methods=['GET'])
@jwt_required
def get_quality_model():
    current_user = get_jwt_identity()
    if current_user[1] != 'Researcher':
        return jsonify("Access denied"), 403
    return jsonify({'quality': models_manager.get_quality(0, current_user[0])}), 200
