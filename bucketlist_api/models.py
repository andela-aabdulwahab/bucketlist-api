import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from bucketlist_api import create_app
from bucketlist_api.config import DevConfig
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# initialization
app = create_app(DevConfig)
# extensions
db = SQLAlchemy(app)


def save(db_model=None):
    if db_model:
        db.session.add(db_model)
    db.session.commit()


class User(db.Model):
    """Provides the database Model for Users.

    Inherits:
        db.Model

    Attributes:
        id: [int] id of the user in the database
        username: [String] username of the user
        password_hash: [String] Hashed version of the user password

    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(70))
    bucketlists = db.relationship('BucketList', backref=db.backref('users',
                                  lazy='joined'), lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=20000):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature:
            return None
        except SignatureExpired:
            return None
        user = User.query.get(data['id'])
        return user

    @staticmethod
    def get_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user is None or not user.verify_password(password):
            return None
        return user

    @classmethod
    def get_user_with_token(cls, token):
        if not token:
            return None
        return cls.verify_token(token)

    @classmethod
    def user_exist(cls, username):
        if cls.query.filter_by(username=username).first():
            return True
        return False

    @staticmethod
    def bucketlist_own_by_user(auth_data, bucketlist_id):
        user = User.get_user_with_token(auth_data)
        bucketlist = BucketList.query.filter_by(id=bucketlist_id).first()
        if not bucketlist or bucketlist.user_id != user.id:
            return False
        return True

class BucketList(db.Model):
    """Provides the database Model for the BucketList.

    Attributes:
        user_id: [int] the user id of the foreign key

    Inherits:
        ItemsModel

    """
    __tablename__ = 'bucketlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.now())
    is_public = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('BucketListItem', backref=db.backref('bucketlist',
                           lazy='joined'), lazy='dynamic')

    @classmethod
    def build_bucketlist(cls, list_bucketlist):
        bucketlist_dict = {}
        for bucketlist in list_bucketlist:
            bucketlist_dict[bucketlist.id] = {
                'id': bucketlist.id,
                'items': cls.get_bucketlist_items(bucketlist.id),
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'is_public': bucketlist.is_public,
                'created_by': bucketlist.user_id
            }
        return bucketlist_dict

    @staticmethod
    def get_bucketlist_items(bucketlist_id):
        items = (BucketListItem.query.filter_by(bucketlist_id = bucketlist_id)
                                     .all())
        if not items:
            return []
        return BucketListItem.build_item_list(items)

    @classmethod
    def id_bucketlist(cls, id, query):
        bucketlist = query.filter_by(id=id).first()
        if bucketlist is None:
            bucketlist = []
        else:
            bucketlist = [bucketlist]
        return [cls.build_bucketlist(bucketlist), None]

    @classmethod
    def paginate_bucketlist(cls, query, page, limit, q):
        page_bucketlist = query.paginate(page=page, per_page=limit)
        bucketlist = page_bucketlist.items
        pagination = {
            'page': page_bucketlist.page,
            'number_of_pages': page_bucketlist.pages,
            'total_number_of_bucketlists': page_bucketlist.total,
        }
        if page_bucketlist.has_next:
            pagination['next'] = url_for(endpoint='bucketlists', limit=limit,
                                         page=page_bucketlist.next_num, q=q,
                                         _method='GET', _external=True)
        if page_bucketlist.has_prev:
            pagination['previous'] = url_for(endpoint='bucketlists',limit=limit,
                                             page=page_bucketlist.prev_num, q=q,
                                             _method='GET', _external=True)
        return [cls.build_bucketlist(bucketlist), pagination]

    @classmethod
    def get_bucketlist(cls, id=None, user_id=None, **kwargs):
        query = (cls.query.filter_by(user_id=user_id)
                        .order_by(cls.date_modified.desc()))
        if id:
            return cls.id_bucketlist(id, query)
        q = kwargs.get('q')
        if q:
            query = query.filter(cls.name.contains(q))
        page = kwargs.get('page')
        limit = kwargs.get('limit')
        if page and page.isdigit():
            page = int(page)
        if limit.isdigit():
            limit = int(limit)
            if limit > 100:
                limit = 100
        return cls.paginate_bucketlist(query, page, limit, q)

    @classmethod
    def update_bucketlist(cls, bucketlist_id):
        bucketlist = cls.query.filter_by(id=bucketlist_id).first()
        cls.date_modified = datetime.now()
        save(bucketlist)


class BucketListItem(db.Model):
    """Provides the database Model for the items on the BucketList Items.

    Inherits:
        ItemModel

    Attributes:
        bucketlist_id: [int] it of the bucktelist it belongs to

    """
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    done = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.now())
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlist.id'))

    @staticmethod
    def build_item_list(items):
        item_list = []
        for item in items:
            item_dict = {
            'id':item.id,
            'name':item.name,
            'date_created':item.date_created,
            'date_modified':item.date_modified,
            'done': item.done
            }
            item_list.append(item_dict)
        return item_list
