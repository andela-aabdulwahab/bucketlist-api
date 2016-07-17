"""Script defined to handle BucketList Item API Calls."""

from flask_restful import Resource, reqparse, marshal_with
from flask import g, request, abort, url_for
from bucketlist_api.models import User, BucketList, BucketListItem
from bucketlist_api.authentication import auth
from bucketlist_api.decorators import get_bucketlist, own_by_user
from bucketlist_api.serializers import bucketlist_serializer


class ItemListAPI(Resource):
    """The API for all Item request.
       requires authentication for access

       Inherits:
           Resource
    """
    decorators = [own_by_user, get_bucketlist, auth.login_required]

    def __init__(self):
        """Initialize the API call and specified the required parameter.

        Makes call Resource constructor
        """
        self.parser = self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, location='json')
        self.parser.add_argument('done', type=int, location='json')
        super(ItemListAPI, self).__init__()

    @marshal_with(bucketlist_serializer)
    def post(self, bucketlist_id):
        data = self.parser.parse_args()
        if not data.get('name'):
            abort(400, 'itemNotCreated: Name not specified for items')
        done = data.get('done', None)
        item = BucketListItem(name=data['name'], done=done)
        g.bucketlist.items.append(item)
        item.save()
        return g.bucketlist

    @marshal_with(bucketlist_serializer)
    def put(self, bucketlist_id, item_id):
        data = self.parser.parse_args()
        item = BucketListItem.query.filter_by(id=item_id,
                              bucketlist_id=bucketlist_id).first_or_404()
        name = data.get('name', item.name)
        done = data.get('done', item.done)
        item.update(name=name, done=done)
        return g.bucketlist

    def delete(self, bucketlist_id, item_id):
        item = BucketListItem.query.filter_by(id=item_id,
                              bucketlist_id=bucketlist_id).first_or_404()
        item.delete()
        return '', 204
