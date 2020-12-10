from app_service import db, create_access_token
from app_service.models import User, Role


class ManagerUsers:
    def user_format_json(self, user: User) -> dict:
        return {
            'id': user.id,
            'login': user.login,
            'email': user.email,
        }

    def get_user(self, user_id: int) -> User:
        user = db.session.query(User).filter(User.id == user_id).first()
        return user

    def delete_user(self, user_id: int) -> int:
        user = self.get_user(user_id)
        db.session.delete(user)
        db.session.commit()
        return 0

    def update_user(self, user_id: int, user_json: dict, user: User) -> User:
        user.email = user_json['email']
        user.login = user_json['login']
        user.password_hash = user_json['password']
        db.session.add(user)
        db.session.commit()
        return user

    def create_user(self, user_json: dict) -> User:
        new_user = User(login=user_json['login'],
                        password=user_json['password'],
                        email=user_json['email'])
        new_user.roles = [db.session.query(Role).filter(Role.name == "User").first()]
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def sign_in(self, user_json: dict) -> (int, str):
        user = db.session.query(User).filter(User.login == user_json['login']).first()
        if user is None:
            return -2, ""
        elif user.check_password(user_json['password']):
            token = create_access_token(identity=(user.id, user.roles[0].name))
            return user.id, token
        else:
            return -1, ""

    def update_role(self, user_id: int, role: str) -> int:
        user = self.get_user(user_id)
        user.roles[0] = [db.session.query(Role).filter(Role.name == role).first()]
        db.session.add(user)
        db.session.commit()
        return 1
