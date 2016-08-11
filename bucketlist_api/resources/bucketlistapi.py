"""Script defined to handle bucketlist API Calls."""

from flask_restful import Resource, reqparse, marshal_with
from flask import g, jsonify, request, abort, url_for
from flask_api import status
from bucketlist_api.models import User, BucketList, BucketListItem
from bucketlist_api.authentication import auth
from bucketlist_api.decorators import paginate
from bucketlist_api.serializers import bucketlist_serializer, \
                                       bucketlist_collection_serializer


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

    @marshal_with(bucketlist_serializer)
    def post(self):
        data = self.parser.parse_args()
        if not data.get('name'):
            abort(400, 'BucketListNotCreated: Name not specified'
                       'for bucketlist')
        is_public = data.get('is_public', False)
        bucketlist = BucketList(name=data['name'], is_public=is_public)
        g.user.bucketlists.append(bucketlist)
        bucketlist.save()
        return bucketlist, 201

    @marshal_with(bucketlist_collection_serializer)
    @paginate
    def get(self, id=None):
        if id:
            return g.user.bucketlists.filter_by(id=id)
        q = request.args.get('q')
        if q:
            return g.user.bucketlists.filter(BucketList.name.contains(q))
        return g.user.bucketlists

    @marshal_with(bucketlist_serializer)
    def put(self, id):
        data = self.parser.parse_args()
        bucketlist = g.user.bucketlists.filter_by(id=id).first_or_404()
        name = data.get('name', bucketlist.name)
        is_public = data.get('is_public', bucketlist.is_public)
        bucketlist.update(name=name, is_public=is_public)
        return bucketlist

    def delete(self, id):
        bucketlist = g.user.bucketlists.filter_by(id=id).first_or_404()
        bucketlist.delete()
        return '', status.HTTP_204_NO_CONTENT
