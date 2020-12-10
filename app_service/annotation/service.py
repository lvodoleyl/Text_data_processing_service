from app_service import db
from app_service.annotation.src import create_annotation
from app_service.models import Annotation, Text, AnnotationModel
from app_service.texts.service import ManagerTexts


class ManagerAnnotation(ManagerTexts):
    def annotation_format_json(self, text: Text, result: Annotation) -> dict:
        return {
            'text_id': text.id,
            'request_id': result.id,
            'use_text': text.text,
            'predict_text': result.predict_text,
            'true_text': result.true_text,
            'model_id': result.model_id
        }

    # Возможно, стоит коммитить новые записи и оформлять в очередь для запуска
    def request_for_annotation(self, text_id: int):
        text = self.get_text(text_id)
        annotation_text = create_annotation(text.text)
        new_annotation_text = Annotation(
            text_id=text_id,
            predict_text=annotation_text
        )
        db.session.add(new_annotation_text)
        db.session.commit()

    def get_list_request_for_annotation(self, user_id: int) -> list:
        requests = db.session.query(Text).filter(Text.user_id == user_id, Text.annotate != None).all()
        return requests

    def get_result_annotation(self, request_id: int) -> (Annotation, Text):
        annotation = db.session.query(Annotation).filter(Annotation.id == request_id).first()
        text = db.session.query(Text).filter(Text.id == annotation.use_text).first()
        return annotation, text

    def delete_request_annotation(self, request_id: int) -> int:
        annotation = self.get_result_annotation(request_id)
        db.session.delete(annotation)
        db.session.commit()
        return 0


class ManagerOfModels(ManagerAnnotation):
    def register_text_for_assessment(self, text: str, true_text: str, user_id: int, model_id: int) -> (Text, Annotation):
        text = self.registration_text(text=text, user_id=user_id)
        annot = Annotation(
            model_id=model_id,
            text_id=text.id,
            predict_text=create_annotation(text.text),
            true_text=true_text
        )
        db.session.add(annot)
        db.session.commit()
        return text, annot

    def get_list_texts_for_assessment(self, user_id: int) -> list:
        texts = db.session.query(Text).filter(Text.user_id == user_id, Text.annotate != None).all()
        return texts

    def get_text_for_assessment(self, test_text_id: int) -> Text:
        return db.session.query(Text).filter(Text.id == test_text_id, Text.annotate != None).first()

    def update_text_for_assessment(self, text_json: dict, text: Text) -> (Text, Annotation):
        text = self.update_text(text_json, text)
        text_annotation = db.session.query(Annotation).filter(Annotation.use_text == text.id).first()
        text_annotation.true_text = text_json['true_text']
        text_annotation.model_id = text_json['model_id']
        text_annotation.predict_text = create_annotation(text.text)
        db.session.add(text_annotation)
        db.session.commit()
        return text, text_annotation

    def get_quality(self, model_id: int, user_id: int) -> float:
        texts = self.get_list_texts_for_assessment(user_id=user_id)
        # TODO compute quality
        model = db.session.query(AnnotationModel).filter(AnnotationModel.id == model_id).first()
        return model.quality
