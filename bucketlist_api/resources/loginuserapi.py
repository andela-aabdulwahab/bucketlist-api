from flask_restful import Resource, reqparse
from flask import jsonify, request, abort, url_for
from bucketlist_api.models import User


class LoginUserAPI(Resource):
    """Login a user, provides an Authentication token.

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
        super(LoginUserAPI, self).__init__()

    def post(self):
        """Handles the post call to the LoginUserAPI.

        Return:
            [Response] containing the token if login is successful

        """
        data = self.parser.parse_args()
        user = User.get_user(data['username'], data['password'])
        if not user:
            abort(401, "Username or password not correct")
        token = user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})
