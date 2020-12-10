from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask import request, jsonify
from main import app

db = SQLAlchemy(app)
jwt = JWTManager(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'


from app_service.manager_users.controller import *
from app_service.texts.controller import *
from app_service.annotation.controller import *
from app_service.clustering.controller import *
from app_service.systems_of_conclusions.controller import *
