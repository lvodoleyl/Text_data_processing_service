from datetime import datetime

from flask_security import RoleMixin, SQLAlchemyUserDatastore, Security
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app_service import db, app

user_role = db.Table('User_Role',
                     db.Column('role_id', db.Integer, db.ForeignKey('Roles.id')),
                     db.Column('user_id', db.Integer, db.ForeignKey('Users.id')))


class User(db.Model, UserMixin):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(1024), nullable=False)
    email = db.Column(db.String(32), nullable=True)
    texts = db.relationship('Text', backref='user', cascade="all, delete")
    systems = db.relationship('SystemOfConclusions', backref='user', cascade="all, delete")
    requests = db.relationship('HistoryOfConclusions', backref='user', cascade="all, delete")
    models = db.relationship('AnnotationModel', backref='user', cascade="all, delete")
    clusters = db.relationship('RequestClustering', backref='user', cascade="all, delete")
    roles = db.relationship('Role', secondary=user_role,
                            backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, login, password, email=""):
        self.login = login
        self.email = email
        self.set_password(password)


class Role(db.Model, RoleMixin):
    __tablename__ = "Roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text, nullable=False)


class Text(db.Model):
    __tablename__ = "Texts"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    annotate = db.relationship('Annotation', backref='text', uselist=False, cascade="all, delete")
    clusters = db.relationship('ClusterAnalysis', backref='text', cascade="all, delete")

    def __init__(self, text, user_id):
        self.text = text
        self.user_id = user_id


class Annotation(db.Model):
    __tablename__ = "Annotation"
    id = db.Column(db.Integer, primary_key=True)
    predict_text = db.Column(db.Text, nullable=False)
    true_text = db.Column(db.Text, nullable=True)
    use_text = db.Column(db.Integer, db.ForeignKey('Texts.id'))
    model_id = db.Column(db.Integer, db.ForeignKey('AnnotationModels.id'))

    def __init__(self, predict_text, text_id, model_id=0, true_text=''):
        self.predict_text = predict_text
        self.true_text = true_text
        self.use_text = text_id
        self.model_id = model_id


class AnnotationModel(db.Model):
    __tablename__ = "AnnotationModels"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    quality = db.Column(db.Float)
    alltexts = db.relationship('Annotation', backref='model')


class RequestClustering(db.Model):
    __tablename__ = "RequestsClustering"
    id = db.Column(db.Integer, primary_key=True)
    count_clusters = db.Column(db.Integer)
    words = db.Column(db.Text)
    topic_modeling = db.Column(db.Text)
    bool_word = db.Column(db.Boolean)
    bool_fcm = db.Column(db.Boolean)
    analysis = db.relationship('ClusterAnalysis', backref='request', cascade="all, delete")
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def __init__(self, count_clusters, user_id, bool_word=True, bool_fcm=True):
        self.count_clusters = count_clusters
        self.user_id = user_id
        self.bool_fcm = bool_fcm
        self.bool_word = bool_word


class ClusterAnalysis(db.Model):
    __tablename__ = "ClusterAnalysis"
    id = db.Column(db.Integer, primary_key=True)
    text_id = db.Column(db.Integer, db.ForeignKey('Texts.id'))
    request_id = db.Column(db.Integer, db.ForeignKey('RequestsClustering.id'))
    num_cluster = db.Column(db.Integer, nullable=False)
    fuzzy_value = db.Column(db.Float)

    def __init__(self, text_id, request_id, num_cluster, fuzzy_value):
        self.text_id = text_id
        self.request_id = request_id
        self.num_cluster = num_cluster
        self.fuzzy_value = fuzzy_value


class Rule(db.Model):
    __tablename__ = "Rules"
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.String(1024), nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey('SystemsOfConclusions.id'))

    def __init__(self, rule, system_id):
        self.rule = rule
        self.system_id = system_id


class SystemOfConclusions(db.Model):
    __tablename__ = "SystemsOfConclusions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    requests = db.relationship('HistoryOfConclusions', backref='SystemOfConclusions', cascade="all, delete")
    rules = db.relationship('Rule', backref='SystemOfConclusions', cascade="all, delete")
    linguistic_vars = db.relationship('LinguisticVariable', backref='SystemOfConclusions', cascade="all, delete")

    def __init__(self, name, description, user_id):
        self.name = name
        self.description = description
        self.user_id = user_id


class LinguisticVariable(db.Model):
    __tablename__ = "LinguisticVariable"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))
    lower = db.Column(db.Float, nullable=False)
    upper = db.Column(db.Float, nullable=False)
    type_output = db.Column(db.Boolean)
    system_id = db.Column(db.Integer, db.ForeignKey('SystemsOfConclusions.id'))
    terms = db.relationship('Term', backref='LinguisticVariable', cascade="all, delete")
    input_output = db.relationship('HistoryInputOutput', backref='LinguisticVariable', cascade="all, delete")

    def __init__(self, name, lower, upper, system_id, type_output=False):
        self.name = name
        self.lower = lower
        self.upper = upper
        self.system_id = system_id
        self.type_output = type_output


class Term(db.Model):
    __tablename__ = "Terms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))
    linguistic_id = db.Column(db.Integer, db.ForeignKey('LinguisticVariable.id'))
    type_membership_function = db.Column(db.String(32), nullable=False)
    points = db.Column(db.String(32), nullable=False)

    def __init__(self, name, linguistic_id, type_membership_function, points):
        self.name = name
        self.linguistic_id = linguistic_id
        self.type_membership_function = type_membership_function
        self.points = points


class HistoryInputOutput(db.Model):
    __tablename__ = "HistoryInputOutput"
    id = db.Column(db.Integer, primary_key=True)
    type_output = db.Column(db.Boolean)
    value = db.Column(db.Float)
    id_request = db.Column(db.Integer, db.ForeignKey('HistoryOfConclusions.id'))
    id_variable = db.Column(db.Integer, db.ForeignKey('LinguisticVariable.id'))

    def __init__(self, type_output, value, id_request, id_variable):
        self.type_output = type_output
        self.value = value
        self.id_request = id_request
        self.id_variable = id_variable



class HistoryOfConclusions(db.Model):
    __tablename__ = "HistoryOfConclusions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    system_id = db.Column(db.Integer, db.ForeignKey('SystemsOfConclusions.id'))
    date = db.Column(db.DateTime)
    input_output = db.relationship('HistoryInputOutput', backref='HistoryOfConclusions', cascade="all, delete")

    def __init__(self, user_id, system_id):
        self.user_id = user_id
        self.system_id = system_id
        self.date = datetime.utcnow()


db.create_all()
