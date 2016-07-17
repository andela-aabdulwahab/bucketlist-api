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

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        # Prevent changing ID of object
        kwargs.pop('id', None)
        for attr, value in kwargs.items():
            if value is not None:
                setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


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

    def save(self, commit=True):
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
    bucketlists = db.relationship('BucketList', backref='users',
                                  cascade="all, delete", lazy='dynamic')

    def __init__(self, username, password, **kwargs):
        super(User, self).__init__(username=username, **kwargs)
        self.set_password(password)

    def set_password(self, password):
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
    items = db.relationship('BucketListItem', backref='bucketlist',
                            cascade="all, delete", lazy='dynamic')


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
