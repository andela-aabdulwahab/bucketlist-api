import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.
                             getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import json
from base64 import b64encode
from bucketlist_api.models import User, BucketList, BucketListItem
import unittest
from flask import url_for
from bucketlist_api import create_app, db
from bucketlist_api.config import TestConfig


class Testmodels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        db.create_all()
        self.user = User(username="tester")
        self.user.hash_password("wahab")
        db.session.add(self.user)
        db.session.commit()
        self.token = self.user.generate_auth_token()

    def test_user_model(self):
        self.assertTrue(self.user.id > 0)

    def test_verify_password(self):
        self.assertTrue(self.user.verify_password("wahab"))

    def test_get_user(self):
        user = User.get_user("tester", "wahab")
        self.assertIsNotNone(user)

    def test_get_user_with_token(self):
        user = User.get_user_with_token(self.token)
        self.assertEqual(user.id, self.user.id)

    def test_user_exist(self):
        self.assertTrue(User.user_exist("tester"))


class TestBucketListModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        db.create_all()
        self.bucketlist = BucketList(name="Travel the World")
        self.bucketlist.created_by = 1
        db.session.add(self.bucketlist)
        db.session.commit()

    def test_bucketlist_init(self):
        self.assertTrue(self.bucketlist.id > 0)

    def test_build_bucketlist(self):
        bucketlist_dict = BucketList.build_bucketlist([self.bucketlist])
        bucketlist_name = bucketlist_dict[self.bucketlist.id]["name"]
        self.assertTrue(type(bucketlist_dict) is dict)
        self.assertTrue(len(bucketlist_dict) > 0)
        self.assertEqual(bucketlist_name, "Travel the World")

    def test_get_bucketlist_id(self):
        bucketlists = BucketList.get_bucketlist(id=self.bucketlist.id)
        self.assertTrue(type(bucketlists) is list)
        self.assertEqual(len(bucketlists), 2)
        self.assertIsNone(bucketlists[1])
        self.assertTrue(type(bucketlists[0]) is dict)

    def test_update_bucketlist(self):
        prev_date_modified = self.bucketlist.date_modified
        BucketList.update_bucketlist(self.bucketlist.id)
        self.assertNotEqual(prev_date_modified, self.bucketlist.date_created)
