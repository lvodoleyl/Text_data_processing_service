from app_service import db
from app_service.clustering.src import run_fcm, get_importance_word, get_importance_word_topic_modeling
from app_service.models import RequestClustering, Text, ClusterAnalysis
from app_service.texts.service import ManagerTexts


class ManagerClustering(ManagerTexts):
    def clustering_request_format_json(self, request: RequestClustering, analysis: list) -> dict:
        return {
            'id': request.id,
            'topic_modeling': request.topic_modeling,
            'words': request.words,
            'bool_fcm': request.bool_fcm,
            'bool_word': request.bool_word,
            'count_clusters': request.count_clusters,
            'analysis': [{'id_text': record.text_id,
                          'num_cluster': record.num_cluster,
                          'fuzzy_value': record.fuzzy_value} for record in analysis]
        }

    def request_for_clustering(self, request_json: dict, user_id: int) -> RequestClustering:
        new_request = RequestClustering(
            count_clusters=request_json['count_clusters'],
            user_id=user_id,
            bool_fcm=request_json['bool_fcm'],
            bool_word=request_json['bool_word']
        )
        db.session.add(new_request)
        db.session.commit()
        if new_request.bool_fcm:
            texts = {}
            for id_text in request_json['texts']:
                text_obj = db.session.query(Text).filter(Text.id == id_text).first()
                if text_obj is not None:
                    texts[id_text] = text_obj.text
            clusters = run_fcm(texts=texts, count_clusters=new_request.count_clusters)
            for text_id in clusters.keys():
                for num_cluster in clusters[text_id]['clusters'].keys():
                    cluster_info = ClusterAnalysis(
                        text_id=text_id,
                        request_id=new_request.id,
                        num_cluster=num_cluster,
                        fuzzy_value=clusters[text_id]['clusters'][num_cluster]
                    )
                    db.session.add(cluster_info)
                    db.session.commit()
            if new_request.bool_word:
                new_request.words = get_importance_word(clusters)
                db.session.add(new_request)
                db.session.commit()
        else:
            for id_text in request_json['texts']:
                clusters_info = ClusterAnalysis(
                    text_id=id_text,
                    request_id=new_request.id,
                    num_cluster=-1,
                    fuzzy_value=-1
                )
                db.session.add(clusters_info)
                db.session.commit()
        return new_request

    def get_all_request_clustering(self, user_id: int) -> list:
        return db.session.query(RequestClustering).filter(RequestClustering.user_id == user_id).all()

    def get_request_clastering(self, request_id: int) -> RequestClustering:
        return db.session.query(RequestClustering).filter(RequestClustering.id == request_id).first()

    def get_clustering_analysis(self, request_id: int) -> (RequestClustering, list):
        request = self.get_request_clastering(request_id)
        info_clustering_analysis = db.session.query(ClusterAnalysis).filter(ClusterAnalysis.request_id == request_id).all()
        return request, info_clustering_analysis

    # TODO cascade delete
    def delete_request_clustering(self, request_clustering: RequestClustering) -> int:
        db.session.delete(request_clustering)
        db.session.commit()
        return 0

    def request_for_topic_modeling(self, request_id: int) -> RequestClustering:
        request, list_for_topic_modeling = self.get_clustering_analysis(request_id)
        if request is not None:
            request.topic_modeling = get_importance_word_topic_modeling(list_for_topic_modeling)
            db.session.add(request)
            db.session.commit()
        return request
