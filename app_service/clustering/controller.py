from app_service.clustering.service import ManagerClustering
from app_service import request, app, jwt_required, get_jwt_identity, jsonify

clustering_manager = ManagerClustering()


# user ? Проверка каждого текста необходима?
@app.route('/clustering', methods=['POST'])
@jwt_required
def clustering_request():
    current_user = get_jwt_identity()
    res = clustering_manager.request_for_clustering(request.json, current_user[0])
    return clustering_manager.clustering_request_format_json(res, res.analysis), 200


# user
@app.route('/clustering', methods=['GET'])
@jwt_required
def get_clusters():
    current_user = get_jwt_identity()
    return jsonify([clustering_manager.clustering_request_format_json(request_, []) for request_ in
                    clustering_manager.get_all_request_clustering(current_user[0])]), 200


# user
@app.route('/clustering/<int:request_id>', methods=['GET'])
@jwt_required
def get_cluster(request_id):
    current_user = get_jwt_identity()
    request_clustering, analysis = clustering_manager.get_clustering_analysis(request_id)
    if request_clustering.user_id != current_user[0]:
        return jsonify("Access denied"), 403
    return jsonify(clustering_manager.clustering_request_format_json(request_clustering, analysis)), 200


# user
@app.route('/clustering/<int:request_id>', methods=['DELETE'])
@jwt_required
def delete_request_clustering(request_id):
    current_user = get_jwt_identity()
    request_clustering = clustering_manager.get_request_clastering(request_id)
    if request_clustering.id != current_user[0]:
        return jsonify("Access denied"), 403
    return {'success': 0 if clustering_manager.delete_request_clustering(request_clustering) else 1}, 200


# user
@app.route('/clustering/<int:request_id>/topic_modeling', methods=['GET'])
@jwt_required
def get_word_cloud(request_id):
    request_clustering = clustering_manager.request_for_topic_modeling(request_id)
    if request_clustering is None:
        return jsonify("Access denied"), 403
    return clustering_manager.clustering_request_format_json(request_clustering, []), 200
