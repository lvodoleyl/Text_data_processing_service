from app_service import db
from app_service.models import Text


class ManagerTexts:
    def text_format_json(self, text: Text) -> dict:
        return {
            'id': text.id,
            'text': text.text
        }

    def get_list_of_texts(self, user_id: int) -> list:
        texts = db.session.query(Text).filter(Text.user_id == user_id).all()
        return texts

    def get_text(self, text_id: int) -> Text:
        text = db.session.query(Text).filter(Text.id == text_id).first()
        return text

    def get_list_all_texts(self):
        return db.session.query(Text).all()

    def registration_text(self, text: str, user_id: int) -> Text:
        new_text = Text(text=text, user_id=user_id)
        db.session.add(new_text)
        db.session.commit()
        return new_text

    def update_text(self, text_json: dict, text: Text) -> Text:
        text.text = text_json['text']
        db.session.add(text)
        db.session.commit()
        return text

    def delete_text(self, text: Text) -> int:
        db.session.delete(text)
        db.session.commit()
        return 0
