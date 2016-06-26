import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.
    getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from werkzeug.http import parse_authorization_header
from flask import Flask, jsonify, request, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from bucketlist_api.models import User, BucketList, BucketListItem, get_db
from datetime import datetime

app = Flask(__name__, static_url_path='')
api = Api(app)
auth = HTTPBasicAuth()


@auth.verify_password
def authenticate_token(token, password):
    if User.verify_token(token):
        return True
    return False


class CreateUserAPI(Resource):
    """Register User to the app.

    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True)
        self.parser.add_argument('password', type=str, required=True)
        super(CreateUserAPI, self).__init__()

    def user_exist(self, username):
        if User.query.filter_by(username=username).first():
            return True
        return False

    def post(self):
        data = self.parser.parse_args()
        new_user = User(username=data['username'])
        new_user.hash_password(data['password'])
        db = get_db()
        if self.user_exist(new_user.username):
            abort(400)
        db.session.add(new_user)
        db.session.commit()
        token = new_user.generate_auth_token()
        response = jsonify({'token': token.decode('ascii')})
        response.status_code = 201
        return response




class LoginUserAPI(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True,
                                    location='json')
        self.parser.add_argument('password', type=str, required=True,
                                    location='json')
        super(LoginUserAPI, self).__init__()

    def get_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user is None or not user.verify_password(password):
            return None
        return user

    def post(self):
        data = self.parser.parse_args()
        user = self.get_user(data['username'], data['password'])
        if not user:
            abort(401)
        token = user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})


#build api end point to handle 405 that returns json
api.add_resource(CreateUserAPI, '/auth/register', endpoint='register')
api.add_resource(LoginUserAPI, '/auth/login', endpoint='login')

if __name__ == '__main__':
    app.run(debug=True)
