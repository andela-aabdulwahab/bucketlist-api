from flask_httpauth import HTTPBasicAuth
from bucketlist_api.models import User
from flask import jsonify, make_response

# Authentication Object
auth = HTTPBasicAuth()


@auth.verify_password
def authenticate_token(token, password):
    """Autheticate User with the provideded token."""
    if User.verify_token(token):
        return True
    return False


@auth.error_handler
def unauthorize():
    """Handles unauthorize access to the API."""

    return make_response(jsonify({'Error': 'Invalid token Supplied or token '
                                  'has expired, Login again to get access'
                                  ' token'}), 401)
