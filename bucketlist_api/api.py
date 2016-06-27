import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.
    getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from werkzeug.http import parse_authorization_header
from flask import Flask, jsonify, request, abort, make_response, url_for
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from bucketlist_api.models import User, BucketList, BucketListItem, save
from datetime import datetime
from custom_error import errors

app = Flask(__name__, static_url_path='')
api = Api(app, errors=errors)
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

    def post(self):
        data = self.parser.parse_args()
        new_user = User(username=data['username'])
        new_user.hash_password(data['password'])
        if User.user_exist(new_user.username):
            abort(409, 'SignUpFailed: A User with the specified username '
                       'already exist')
        save(new_user)
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


    def post(self):
        data = self.parser.parse_args()
        user = User.get_user(data['username'], data['password'])
        if not user:
            abort(401, "Username or password not correct")
        token = user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})



class BucketListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.parser = self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, location='json')
        self.parser.add_argument('is_public', type=bool, location='json')
        self.parser.add_argument('Authorization', location='headers')


    def post(self):
        data = self.parser.parse_args()
        if not data.get('name'):
            abort(400, 'BucketListNotCreated: Name not specified for bucketlist')
        bucketlist = BucketList(name=data['name'], is_public=False)
        bucketlist.date_created = datetime.now()
        bucketlist.date_modified = datetime.now()
        if data.get('is_public'):
            bucketlist.is_public = data['is_public']
        auth_data = request.authorization
        user = User.get_user_with_token(auth_data).id
        bucketlist.user_id = user.id
        save(bucketlist)
        response = jsonify({'bucketlist': url_for('bucketlist',id=bucketlist.id,
                            _external=True)})
        response.status_code = 201
        return response

    def get(self, id=None):
        auth_data = request.authorization
        limit = request.args.get('limit', '20')
        page = request.args.get('page')
        user = User.get_user_with_token(auth_data)
        q = request.args.get('q')
        if id:
            bucketlist = BucketList.get_bucketlist(id=id, user_id=user.id)
        else:
            bucketlist = BucketList.get_bucketlist(user_id=user.id, q=q,
                                                   limit=limit, page=page)
        if len(bucketlist[0]) < 1:
            abort(404, "NotFound: No bucketlist that satisfy the specified"
                       " parameter found")
        return jsonify({'bucketlist': bucketlist})

    def put(self, id):
        auth_data = request.authorization
        data = self.parser.parse_args()
        user = User.get_user_with_token(auth_data)
        bucketlist = (BucketList.query.filter_by(id=id, user_id=user.id)
                                      .first())
        if bucketlist is None:
            abort(404, "UpdateFailed: No bucketlist with the specified id")
        if data.get('name'):
            bucketlist.name = data['name']
        if data.get('is_public'):
            bucketlist.is_public = data['is_public']
        bucketlist.date_modified = datetime.now()
        save(bucketlist)
        response = jsonify({'bucketlist': url_for('bucketlist',id=bucketlist.id,
                            _external=True)})
        response.status_code = 201
        return response

    def delete(self, id):
        auth_data = request.authorization
        data = self.parser.parse_args()
        user = User.get_user_with_token(auth_data)
        bucketlist = (BucketList.query.filter_by(id=id, user_id=user.id)
                                      .delete())
        if not bucketlist:
            abort(404, "DeleteFailed: No bucketlist with the specified id")
        items = (BucketListItem.query.filter_by(bucketlist_id = id).delete())
        save()
        response = jsonify({'message':'bucketlist deleted'})
        response.status_code = 201
        return response



class ItemListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.parser = self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, location='json')
        self.parser.add_argument('done', type=int, location='json')

    def post(self, id):
        data = self.parser.parse_args()
        auth_data = request.authorization
        if not User.bucketlist_own_by_user(auth_data, id):
            abort(401, "NotPermitted: You can't access bucketlist belonging to"
                       " other users")
        item = BucketListItem(name=data['name'], bucketlist_id=id)
        item.date_created = datetime.now()
        item.date_modified = datetime.now()
        save(item)
        response = jsonify({'item':item.id})
        response.status_code = 201
        return response

    def put(self, id, item_id):
        auth_data = request.authorization
        data = self.parser.parse_args()
        if not User.bucketlist_own_by_user(auth_data, id):
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
        item.date_modified = datetime.now()
        save(item)
        BucketList.update_bucketlist(id)
        response = jsonify({'item':item.id})
        response.status_code = 200
        return response

    def delete(self, id, item_id):
        auth_data = request.authorization
        if not User.bucketlist_own_by_user(auth_data, id):
            abort(401, "NotPermitted: You can't access bucketlist belonging to"
                       " other users")
        item = BucketListItem.query.filter_by(id=item_id,
                                           bucketlist_id=item_id).delete()
        if not item:
            abort(404, "DeleteFailed: Item with the specified id not found")
        BucketList.update_bucketlist(id)
        save()
        response = jsonify({'item': item})
        response.status_code = 200
        return response






#build api end point to handle 405 that returns json
api.add_resource(CreateUserAPI, '/auth/register', endpoint='register')
api.add_resource(LoginUserAPI, '/auth/login', endpoint='login')
api.add_resource(BucketListAPI, '/bucketlists', endpoint='bucketlists')
api.add_resource(BucketListAPI, '/bucketlists/<int:id>', endpoint='bucketlist')
api.add_resource(ItemListAPI, '/bucketlists/<int:id>/items',
                 endpoint='items')
api.add_resource(ItemListAPI, '/bucketlists/<int:id>/items/<int:item_id>',
                 endpoint='item')

if __name__ == '__main__':
    app.run(debug=True)
