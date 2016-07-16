"""Script defined to handle bucketlist API Calls."""

from flask_restful import Resource, reqparse
from flask import jsonify, request, abort, url_for
from bucketlist_api.models import User, BucketList, BucketListItem
from bucketlist_api.authentication import auth


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
        is_public = data.get('is_public', False)
        bucketlist = BucketList(name=data['name'], is_public=is_public)
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
