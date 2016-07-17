from flask_restful import fields


user_serializer = {
    'token': fields.String,
}

item_serializer = {
    'id': fields.Integer,
    'name': fields.String,
    'done': fields.Boolean,
    'date_modified': fields.DateTime,
    'date_created': fields.DateTime,
}

pagination_fields = {
    'page': fields.Integer,
    'number_of_pages': fields.Integer,
    'total': fields.Integer,
    'next': fields.String,
    'previous': fields.String,
}
bucketlist_serializer = {
    'id': fields.Integer,
    'name': fields.String,
    'is_public': fields.Boolean,
    'date_modified': fields.DateTime,
    'date_created': fields.DateTime,
    'created_by': fields.Integer(attribute='user_id'),
    'items': fields.List(fields.Nested(item_serializer)),
}

bucketlist_collection_serializer = {
    'pagination': fields.Nested(pagination_fields),
    'bucketlists': fields.List(fields.Nested(bucketlist_serializer)),
}
