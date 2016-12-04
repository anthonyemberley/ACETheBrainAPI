from AceAPI import db
from sqlalchemy.dialects.postgresql import JSON


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True)
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String())

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Response(db.Model):
    __tablename__ = 'response'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    response = db.Column(db.String())
    question = db.Column(db.String())
    response_time = db.Column(db.Integer)
    errors = db.Column(db.Integer)
    pauses = db.Column(db.Integer)

    def __init__(self, user_id, response, response_time, errors, pauses, question):
        self.user_id = user_id
        self.response = response
        self.response_time = response_time
        self.errors = errors
        self.pauses = pauses
        self.question = question


    def __repr__(self):
        return '<id {}>'.format(self.id)