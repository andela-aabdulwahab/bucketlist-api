from flask_restful import Resource, reqparse
from flask import jsonify, request, abort, url_for
from bucketlist_api.models import User, BucketList, BucketListItem
from bucketlist_api.authentication import auth


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
