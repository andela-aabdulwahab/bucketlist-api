"""Script defines models for the application."""

import os
from flask import Flask, request, jsonify, g, url_for
from sqlalchemy import desc
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from bucketlist_api import create_app, db
from bucketlist_api.config import DevConfig
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# initialization
app = create_app(DevConfig)


class BaseModel(db.Model):
    """The base model for implementing features common to all the models.

    Inherits:
        db.Model

    Attributes:
        id: [int] id single model in the database
        date_created: [datetime] date function was created
    """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.now())

    def save(self):
        """Save and commit Model changes to Database."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit():
        """Commits changes made to the database."""
        db.session.commit()


class BucketListModel(BaseModel):
    """Base class for bucketlist item.

    Inherits:
        BaseModel

    Attributes:
        name: [string] the title of the Item
        date_modified: [datetime] The last modified date
    """
    __abstract__ = True

    name = db.Column(db.String(50), nullable=False)
    date_modified = db.Column(db.DateTime, default=db.func.now())

    def save(self):
        self.date_modified = db.func.now()
        super(BucketListModel, self).save()


class User(BaseModel):
    """Provides the database Model for Users.

    Inherits:
        BaseModel

    Attributes:
        username: [String] username of the user
        password_hash: [String] Hashed version of the user password
        bucketlists: [Model Fk] ForeignKey relationship between User and
                     BucketList

    """
    __tablename__ = 'users'
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(70))
    bucketlists = db.relationship('BucketList', backref=db.backref('users',
                                  lazy='joined'), lazy='dynamic')

    def hash_password(self, password):
        """Encrypt the User password.

        Arguments:
            password: [String] string Representing the User password
        """
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verify input password with the Hashed password.

        Arguments:
            password: [String] string Representing the User password

        Return:
            Boolean. Representing the status of the password check
        """
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=20000):
        """Generate Authentication Token.

        Arguments:
            expiration: [Int] The token expiry time in second

        Return:
            Token: [String] The generated token
        """
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_token(token):
        """Verify the State of the Token.
        Check if the token is valid and hasn't exipred

        Arguments:
            token: [String]

        Return:
            user [Model] User Model containing the user information
        """
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user

    @staticmethod
    def get_user(username, password):
        """Get the user with specified username.

        Arguments:
            username: [string] username of the user to get_user
            password: [string] a valid password of that user

        Return:
            user [Model] User Model containing the user information
        """
        user = User.query.filter_by(username=username).first()
        if user is None or not user.verify_password(password):
            return None
        return user

    @staticmethod
    def get_user_with_token(token):
        """Get a user with the token provided.

        Arguments:
            token: [string]

        Return:
            user [Model] User Model containing the user information
        """
        return User.verify_token(token)

    @staticmethod
    def user_exist(username):
        """Verify if a user already exist in the Database.

        Arguments:
            token: [string]

        Return:
            [Boolean] Representing the status of the user existence
        """
        if User.query.filter_by(username=username).first():
            return True
        return False

    @staticmethod
    def bucketlist_own_by_user(token, bucketlist_id):
        """Verify if a given bucketlist is own by user.

        Arguments:
            token: [string] token of the user to check the bucketlist against
            bucketlist_id: [string] The BucketList Id

        Return:
            [Boolean] the status of the check
        """
        user = User.get_user_with_token(token)
        bucketlist = BucketList.query.filter_by(id=bucketlist_id).first()
        if not bucketlist or bucketlist.user_id != user.id:
            return False
        return True


class BucketList(BucketListModel):
    """Provides the database Model for the BucketList.

    Attributes:
        is_public: [Boolean] Is availability to the user
        user_id: [int] the foreign key user id
        item: [Model Fk] The bucketlist-item relationship

    Inherits:
        BucketListModel

    """
    __tablename__ = 'bucketlist'
    is_public = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('BucketListItem', backref=db.backref('bucketlist',
                            lazy='joined'), lazy='dynamic')

    @staticmethod
    def build_bucketlist(list_bucketlist):
        """Covert a list of BucketList model object into python Dictionary
        Object.

        Arguments:
            list_bucketlist: [List] contains object of the BucketList Model

        Return:
            [Dict] bucketlist as dictionary
        """
        bucketlist_dict = {}
        for bucketlist in list_bucketlist:
            bucketlist_dict[bucketlist.id] = {
                'id': bucketlist.id,
                'items': BucketList.get_bucketlist_items(bucketlist.id),
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'is_public': bucketlist.is_public,
                'created_by': bucketlist.user_id
            }
        return bucketlist_dict

    @staticmethod
    def get_bucketlist_items(bucketlist_id):
        """Get the items belonging to the specified bucketlist.

        Argument:
            bucketlist_id: [int] the Id of the bucketlist

        Return:
            [Dict] of items belonging to the user
        """
        items = (BucketListItem.query.filter_by(bucketlist_id=bucketlist_id)
                                     .all())
        if not items:
            return []
        return BucketListItem.build_item_list(items)

    @staticmethod
    def id_bucketlist(id, query):
        """Get bucketlist with a specified id.
        Arguments:
            id: [int] id of the bucketlist to Get
            query: [sqlalchemy query] the query to build on

        Return:
            [list] a list containing the bucketlist and pagination properties,
            none in this case

        """
        bucketlist = query.filter_by(id=id).first()
        if bucketlist is None:
            bucketlist = []
        else:
            bucketlist = [bucketlist]
        return [BucketList.build_bucketlist(bucketlist), None]

    @staticmethod
    def paginate_bucketlist(query, page, limit, q):
        """paginate the bucketlist return from a query.

        Arguments:
            query: [sqlalchemy query] the query to build on
            page: [int] page number
            limit: [int] the number of return to return
            q: [string] the optional search parameter
        """
        page_bucketlist = query.paginate(page=page, per_page=limit)
        bucketlist = page_bucketlist.items
        pagination = {
            'page': page_bucketlist.page,
            'number_of_pages': page_bucketlist.pages,
            'total_number_of_bucketlists': page_bucketlist.total,
        }
        if page_bucketlist.has_next:
            pagination['next'] = url_for(endpoint='api.bucketlists',
                                         limit=limit,
                                         page=page_bucketlist.next_num, q=q,
                                         _method='GET', _external=True)
        if page_bucketlist.has_prev:
            pagination['previous'] = url_for(endpoint='api.bucketlists',
                                             limit=limit, page=page_bucketlist
                                             .prev_num, q=q, _method='GET',
                                             _external=True)
        return [BucketList.build_bucketlist(bucketlist), pagination]

    @staticmethod
    def get_bucketlist(id=None, user_id=None, **kwargs):
        """Get a bucketlist from the database.

        Arguments:
            id: [int]
            user_id: [int] Id of the user making thr request
            **kwargs: keyword arguments consisting of page, limit and q
        Return:
            [list] containing the bucketlist dictionary and pagination ppt
        """
        query = BucketList.query.filter_by(user_id=user_id)
        if id:
            return BucketList.id_bucketlist(id, query)
        query = query.order_by(desc(BucketList.date_modified))
        q = kwargs.get('q')
        if q:
            query = query.filter(BucketList.name.contains(q))
        page = kwargs.get('page')
        limit = kwargs.get('limit')
        if page and page.isdigit():
            page = int(page)
        if limit.isdigit():
            limit = int(limit)
        if limit > 100:
            limit = 100
        return BucketList.paginate_bucketlist(query, page, limit, q)


class BucketListItem(BucketListModel):
    """Provides the database Model for the items on the BucketList Items.

    Inherits:
        BucketListModel

    Attributes:
        bucketlist_id: [int] it of the bucketlist it belongs to
        done: [Boolean]

    """
    __tablename__ = 'items'
    done = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlist.id'))

    @staticmethod
    def build_item_list(items):
        """Build a list of the items dictionary.

        Arguments:
            items: [List] a list of BucketListItem Model

        Return:
            [list] a list of items dictionary

        """
        item_list = []
        for item in items:
            item_dict = {
                'id': item.id,
                'name': item.name,
                'date_created': item.date_created,
                'date_modified': item.date_modified,
                'done': item.done
            }
            item_list.append(item_dict)
        return item_list
