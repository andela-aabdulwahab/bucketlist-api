from flask_restful import Resource, reqparse
from flask import jsonify, request, abort, url_for
from bucketlist_api.models import User

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
        self.parser.add_argument('username', type=str, required=True)
        self.parser.add_argument('password', type=str, required=True)
        super(CreateUserAPI, self).__init__()

    def post(self):
        """Handles the POST call to the CreateUserAPI."""
        data = self.parser.parse_args()
        username = data.get('username')
        password = data.get('password')
        if User.user_exist(username):
            abort(409, 'SignUpFailed: A User with the specified username '
                       'already exist')
        new_user = User(username=username)
        new_user.hash_password(password)
        new_user.save()
        token = new_user.generate_auth_token()
        response = jsonify({'token': token.decode('ascii')})
        response.status_code = 201
        return response
