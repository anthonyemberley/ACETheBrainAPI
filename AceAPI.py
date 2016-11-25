from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import os
from flask.ext.sqlalchemy import SQLAlchemy

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

        return {'Email': args['email'], 'Password': args['password'], 'Username': args['password']}



api.add_resource(CreateUser, '/CreateUser')

if __name__ == '__main__':
    app.run(debug=True)