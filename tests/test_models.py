import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.
                             getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import json
from base64 import b64encode
from bucketlist_api.models import User
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

    def tearDown(self):
        User.query.filter_by(id=self.user.id).delete()

    def test_user_model(self):
        self.assertTrue(self.user.id > 0)

    def test_verify_password(self):
        self.assertTrue(self.user.verify_password('wahab'))

    def test_get_user(self):
        user = User.get_user('tester', 'wahab')
        self.assertIsNotNone(user)

    def test_get_user_with_token(self):
        user = User.get_user_with_token(self.token)
        self.assertEqual(user.id, self.user.id)

    def test_user_exist(self):
        self.assertTrue(User.user_exist("tester"))

    def test_bucketlist_model(self):
        pass
