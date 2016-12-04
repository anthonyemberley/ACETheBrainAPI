from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import os
import random
from flask.ext.sqlalchemy import SQLAlchemy
import psycopg2
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

from models import User, Response

class CreateUser(Resource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Email required to create user', required=True)
        parser.add_argument('password', type=str, help='Password required to create user', required=True)
        parser.add_argument('username', type=str, help='Username required to create user', required=True)
        args = parser.parse_args()

        _userEmail = args['email']
        _userPassword = args['password']
        _userUsername = args['username']

        try:
                newUser = User(
                    username=_userUsername,
                    password=_userPassword,
                    email=_userEmail
                )
                userExists = User.query.filter_by(email=_userEmail).first()
                if userExists == None:
                    db.session.add(newUser)
                    db.session.commit()
                    user = User.query.filter_by(email=_userEmail).first()
                    return {"id": user.id, 'Email': args['email'], 'Password': args['password'], 'Username': args['password']}, 200


        except Exception as e:
                return {'error': "Username or email already taken"}, 409

        return {'error': "Username or email already taken"}, 409

api.add_resource(CreateUser, '/api/CreateUser')


class LoginUser(Resource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='Email required to create user', required=True)
        parser.add_argument('password', type=str, help='Password required to create user', required=True)
        args = parser.parse_args()

        _userEmail = args['email']
        _userPassword = args['password']

        try:

            user = User.query.filter_by(email=_userEmail).first()
            if user != None:
                if user.password == _userPassword:
                    return {"id": user.id, "email": user.email, "username": user.username}, 200

            return {"error": "Email or password do not match our records"}, 404


        except Exception as e:
                return {'error': str(e)}


api.add_resource(LoginUser, '/api/LoginUser')

class NewQuestionResponse(Resource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=str, help='User ID is required', required=True)
        parser.add_argument('question', type=str, help='Question is required', required=True)
        parser.add_argument('response', type=str, help='Response is required', required=True)
        parser.add_argument('response_time', type=str, help='Response Time is required', required=True)
        parser.add_argument('errors', type=str, help='Errors are required', required=True)
        parser.add_argument('pauses', type=str, help='Pauses are required', required=True)
        args = parser.parse_args()

        _userID = args['user_id']
        _question = args['question']
        _response = args['response']
        _responseTime = args['response_time']
        _errors = args['errors']
        _pauses = args['pauses']


        try:
                newResponse = Response(
                    user_id = _userID,
                    response = _response,
                    response_time = _responseTime,
                    errors = _errors,
                    pauses = _pauses,
                    question = _question
                )
                db.session.add(newResponse)
                db.session.commit()

        except Exception as e:
                return {'error': "Error inserting into db"}, 400
        return {'user_id': args['user_id'], 'question': args['question'], 'response': args['response'], 'response_time': args['response_time'], 'errors': args['errors'], 'pauses': args['pauses']}, 200

api.add_resource(NewQuestionResponse, '/api/NewResponse')


class NewQuestion(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('questions_asked', type=str, action='append', help='Please provide questions already asked', required=True)
        args = parser.parse_args()


        _questionsAsked = args["questions_asked"]
        possible_questions = ["What did you do today?", "How are you feeling?", "What did you eat for lunch yesterday?", "What is your plan for today?"]
        for question in _questionsAsked:
            print(question)
        if len(_questionsAsked) == len(possible_questions):
            random_question = "Thank you, that is all the questions for today"
        else:
            random_question = random.choice(possible_questions)
            while (random_question in _questionsAsked):
                random_question = random.choice(possible_questions)


        return {'question': random_question}, 200

api.add_resource(NewQuestion, '/api/NewQuestion')

if __name__ == '__main__':
    app.run(debug=True)