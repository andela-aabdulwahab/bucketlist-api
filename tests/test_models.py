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
        self.user.save()
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
        invalid_token = "this-is-no-way-a-token"
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
        self.bucketlist.save()

    def test_bucketlist_init(self):
        self.assertGreater(self.bucketlist.id, 0)

    def test_bucketlist_update(self):
        self.bucketlist.update(is_public=True)
        self.assertTrue(self.bucketlist.is_public)


class TestBucketListItemModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        db.create_all()
        self.bucketlist = BucketList(name="Travel the world")
        db.session.add(self.bucketlist)
        self.bucketlist_item = BucketListItem(name="See the great wall")
        self.bucketlist.items.append(self.bucketlist_item)
        self.bucketlist_item.save()

    def tearDown(self):
        self.bucketlist.delete()
        self.bucketlist_item.delete()

    def test_bucketlist_item_init(self):
        self.assertGreater(self.bucketlist_item.id, 0)
