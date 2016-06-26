import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'For checkpoint two preparation'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bucktelist.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)

def get_db():
    #Return an instance of the database
    db.create_all()
    return db

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
