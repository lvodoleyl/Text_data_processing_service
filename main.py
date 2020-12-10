from flask import Flask


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:12345@localhost:5432/text_service'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
