import os, sys, inspect

# Append Curent path to the system path to allow model visibility
currentdir = os.path.dirname(os.path.abspath(inspect.
                             getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from flask import jsonify, request, abort, make_response, url_for
from flask_restful import Api, Resource, reqparse, fields
from flask_httpauth import HTTPBasicAuth
from bucketlist_api.models import User, BucketList, BucketListItem
from bucketlist_api import create_app, api
from bucketlist_api.config import DevConfig
from datetime import datetime
from bucketlist_api.authentication import auth

# initialization
app = create_app(DevConfig)


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


class HelpAPI(Resource):
    """Provides a help platform for the user. """

    def get(self):
        """Handles the get call to the HelpAPI."""
        help_message = {
            "message": "Access the app with url provided",
            "register": {
                "methods": "POST",
                "url": "auth/register",
                "PublicAccess": True,
             },
            "login": {
                "methods": "POST",
                "url": "/auth/login",
                "PublicAccess": True,
              },
            "bucketlists": {
                "methods": "GET, POST, PUT, DELETE",
                "url": ["/bucketlists", "/bucketlists/<int:id>"],
                "Public Access": False,
             },
            "items": {
                "methods": "POST, PUT, DELETE",
                "url": ["/bucketlists/<int:id>/items",
                        "/bucketlists/<int:id>/items/<int:item_id>"],
                "PublicAccess": False,
             },
        }
        return jsonify(help_message)


class BucketListAPI(Resource):
    """The API for all bucketlist request.
       requires authentication for access

       Inherits:
           Resource
    """
    decorators = [auth.login_required]

    def __init__(self):
        """Initialize the API call and specified the required parameter.

        Makes call Resource constructor
        """
        self.parser = self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, location='json')
        self.parser.add_argument('is_public', type=bool, location='json')
        self.parser.add_argument('Authorization', location='headers')
        super(BucketListAPI, self).__init__()

    def post(self):
        data = self.parser.parse_args()
        if not data.get('name'):
            abort(400, 'BucketListNotCreated: Name not specified'
                       'for bucketlist')
        bucketlist = BucketList(name=data['name'], is_public=False)
        bucketlist.date_created = datetime.now()
        bucketlist.date_modified = datetime.now()
        if data.get('is_public'):
            bucketlist.is_public = data['is_public']
        auth_data = request.authorization
        user = User.get_user_with_token(auth_data.get('username'))
        bucketlist.user_id = user.id
        bucketlist.save()
        response = jsonify({'bucketlist': url_for('api.bucketlists',
                                                  id=bucketlist.id,
                                                  _external=True)})
        response.status_code = 201
        return response

    def get(self, id=None):
        auth_data = request.authorization
        limit = request.args.get('limit', '20')
        page = request.args.get('page')
        user = User.get_user_with_token(auth_data.get('username'))
        q = request.args.get('q')
        if id:
            bucketlist = BucketList.get_bucketlist(id=id, user_id=user.id)
        else:
            bucketlist = BucketList.get_bucketlist(user_id=user.id, q=q,
                                                   limit=limit, page=page)
        if len(bucketlist[0]) < 1:
            abort(404, "NotFound: No bucketlist that satisfy the specified"
                       " parameter found")
        return jsonify({'bucketlists': bucketlist})

    def put(self, id):
        auth_data = request.authorization
        data = self.parser.parse_args()
        user = User.get_user_with_token(auth_data.get('username'))
        bucketlist = (BucketList.query.filter_by(id=id, user_id=user.id)
                                      .first())
        if bucketlist is None:
            abort(404, "UpdateFailed: No bucketlist with the specified id")
        if data.get('name'):
            bucketlist.name = data['name']
        if data.get('is_public'):
            bucketlist.is_public = data['is_public']
        bucketlist.save()
        response = jsonify({'bucketlist': url_for('api.bucketlists',
                                                  id=bucketlist.id,
                                                  _external=True)})
        response.status_code = 201
        return response

    def delete(self, id):
        auth_data = request.authorization
        user = User.get_user_with_token(auth_data.get('username'))
        bucketlist = (BucketList.query.filter_by(id=id, user_id=user.id)
                                      .delete())
        if not bucketlist:
            abort(404, "DeleteFailed: No bucketlist with the specified id")
        items = (BucketListItem.query.filter_by(bucketlist_id=id).delete())
        BucketList.commit()
        response = jsonify({'message': 'bucketlist deleted'})
        response.status_code = 204
        return response


class ItemListAPI(Resource):
    """The API for all Item request.
       requires authentication for access

       Inherits:
           Resource
    """
    decorators = [auth.login_required]

    def __init__(self):
        """Initialize the API call and specified the required parameter.

        Makes call Resource constructor
        """
        self.parser = self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, location='json')
        self.parser.add_argument('done', type=int, location='json')
        super(ItemListAPI, self).__init__()

    def post(self, id):
        data = self.parser.parse_args()
        token = request.authorization.get('username')
        if not User.bucketlist_own_by_user(token, id):
            abort(401, "NotPermitted: You can't access bucketlist belonging to"
                       " other users")
        if not data.get('name'):
            abort(400, 'itemNotCreated: Name not specified for items')
        item = BucketListItem(name=data['name'], bucketlist_id=id)
        item.date_created = datetime.now()
        item.date_modified = datetime.now()
        item.save()
        response = jsonify({'bucketlist': url_for('api.bucketlists', id=id,
                            _external=True)})
        response.status_code = 201
        return response

    def put(self, id, item_id):
        token = request.authorization.get('username')
        data = self.parser.parse_args()
        if not User.bucketlist_own_by_user(token, id):
            abort(401, "NotPermitted: You can't access bucketlist belonging to"
                       " other users")
        item = (BucketListItem.query.filter_by(id=item_id, bucketlist_id=id)
                .first())
        if not item:
            abort(404, "UpdateFailed: Item with the specified id not found")
        if data.get('name'):
            item.name = data['name']
        if data.get('done'):
            item.done = data['done']
        item.save()
        response = jsonify({'bucketlist': url_for('api.bucketlists', id=id,
                            _external=True)})
        return response

    def delete(self, id, item_id):
        token = request.authorization.get('username')
        if not User.bucketlist_own_by_user(token, id):
            abort(401, "NotPermitted: You can't access bucketlist belonging to"
                       " other users")
        item = BucketListItem.query.filter_by(id=item_id,
                                              bucketlist_id=id).delete()
        if not item:
            abort(404, "DeleteFailed: Item with the specified id not found")
        bucketlist = BucketList.query.filter_by(id=id).first()
        bucketlist.save()
        response = jsonify({'bucketlist': url_for('api.bucketlists', id=id,
                            _external=True)})
        response.status_code = 204
        return response


api.add_resource(HelpAPI, '/help', endpoint='help')
api.add_resource(CreateUserAPI, '/auth/register', endpoint='register')
api.add_resource(LoginUserAPI, '/auth/login', endpoint='login')
api.add_resource(BucketListAPI, '/bucketlists', '/bucketlists/<int:id>',
                 endpoint='bucketlists')
api.add_resource(ItemListAPI, '/bucketlists/<int:id>/items',
                 '/bucketlists/<int:id>/items/<int:item_id>', endpoint='items')
