import os
import sys
import inspect
from bucketlist_api.models import User, BucketList, BucketListItem
import unittest
from bucketlist_api import create_app, db
from bucketlist_api.config import TestConfig
import time


class Testmodels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        db.create_all()
        self.user = User(username="tester", password="wahab")
        db.session.add(self.user)
        db.session.commit()
        self.token = self.user.generate_auth_token()

    def test_user_model(self):
        self.assertGreater(self.user.id, 0)

    def test_verify_password(self):
        self.assertTrue(self.user.verify_password("wahab"))

    def test_get_user(self):
        user = User.get_user("tester", "wahab")
        self.assertIsNotNone(user)

    def test_verify_token(self):
        self.assertTrue(User.verify_token(self.token))

    def test_verify_invalid_token(self):
        invalid_token = "this-is-no-way-a-token-nvnfovndsvnsdjn"
        self.assertFalse(User.verify_token(invalid_token))

    def test_expired_token(self):
        token = self.user.generate_auth_token(expiration=1)
        time.sleep(2)
        self.assertFalse(self.user.verify_token(token))

    def test_user_exist(self):
        self.assertTrue(User.user_exist("tester"))


class TestBucketListModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        db.create_all()
        self.bucketlist = BucketList(name="Travel the World")
        self.bucketlist.user_id = 10
        db.session.add(self.bucketlist)
        db.session.commit()

    def test_bucketlist_init(self):
        self.assertGreater(self.bucketlist.id, 0)


class TestBucketListItemModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        db.create_all()
        self.bucketlist = BucketList(name="Travel the world")
        db.session.add(self.bucketlist)
        self.bucketlist_item = BucketListItem(name="See the great wall")
        self.bucketlist_item.bucketlist_id = self.bucketlist.id
        db.session.add(self.bucketlist_item)
        db.session.commit()

    def tearDown(self):
        BucketList.query.filter_by(id=self.bucketlist.id).delete()
        BucketListItem.query.filter_by(id=self.bucketlist_item.id)
        db.session.commit()

    def test_bucketlist_item_init(self):
        self.assertGreater(self.bucketlist_item.id, 0)
