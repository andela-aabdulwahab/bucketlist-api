"""Script defined to handle Register API Call."""

from flask_restful import Resource, reqparse, marshal_with
from flask import abort
from bucketlist_api.models import User
from bucketlist_api.serializers import user_serializer

class CreateUserAPI(Resource):
    """Register User to the app.
       Create an instance of the User Model and save to the database

       Inherits:
           Resource
    """

    def __init__(self):
        """Initialize the API call and specified the required parameter.

        Makes call Resource constructor
        """
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True,
                                 location='json')
        self.parser.add_argument('password', type=str, required=True,
                                 location='json')
        super(CreateUserAPI, self).__init__()

    @marshal_with(user_serializer)
    def post(self):
        """Handles the POST call to the CreateUserAPI."""
        data = self.parser.parse_args()
        username = data.get('username')
        password = data.get('password')
        if User.user_exist(username):
            abort(400, 'SignUpFailed: A User with the specified username '
                       'already exist')
        new_user = User(username=username, password=password)
        new_user.save()
        token = new_user.generate_auth_token()
        return {'token': token.decode('utf-8')}, 201
