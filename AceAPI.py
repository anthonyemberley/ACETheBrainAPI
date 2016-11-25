from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import os
from flask.ext.sqlalchemy import SQLAlchemy
import psycopg2
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

from models import User

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

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
                db.session.add(newUser)
                db.session.commit()

        except Exception as e:
                return {'error': "Username or email already taken"}
        return {'Email': args['email'], 'Password': args['password'], 'Username': args['password']}

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
	        if user.password == _userPassword:
	            return {"id": user.id, "email": user.email, "username": user.username}
	        else:
	            return {"Email or password do not match our records"}


        except Exception as e:
	            return {'error': str(e)}


api.add_resource(LoginUser, '/api/LoginUser')

if __name__ == '__main__':
    app.run(debug=True)