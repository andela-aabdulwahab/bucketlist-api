import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.
                             getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import json
from base64 import b64encode
from bucketlist_api.models import User, BucketList, BucketListItem, save
import unittest
from flask import url_for
from bucketlist_api import create_app, db, api
from bucketlist_api.config import TestConfig
from bucketlist_api.api import CreateUserAPI, LoginUserAPI, BucketListAPI, ItemListAPI

'''api.add_resource(LoginUserAPI, '/auth/login', endpoint='login')
api.add_resource(BucketListAPI, '/bucketlists',
                                '/bucketlists/<int:id>',
                                endpoint='bucketlists')
api.add_resource(ItemListAPI, '/bucketlists/<int:id>/items',
                 '/bucketlists/<int:id>/items/<int:item_id>',
                 endpoint='items')'''


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        api.add_resource(CreateUserAPI, '/auth/register', endpoint='register')
        api.add_resource(LoginUserAPI, '/auth/login', endpoint='login')
        db.create_all()
        self.body = {
            "username": "malikwahab",
            "password": "malik123",
        }
        self.test_client = self.app.test_client()
        self.response = self.send_post('/auth/register', self.body)

    def send_post(self, url, body):
        response = self.test_client.post(url,
                                         data=json.dumps(body),
                                         content_type="application/json")
        return response

    def test_create_user(self):
        response_json = json.loads(self.response.data.decode('utf-8'))
        self.assertEqual(self.response.status_code, 201)
        self.assertIn('token', response_json)

    def test_create_user_username_required(self):
        response_json = json.loads(self.response.data.decode('utf-8'))
        self.assertEqual(self.response.status_code, 409)
        self.assertIn('message', response_json)

    def test_user_exist(self):
        second_response = self.send_post('/auth/register', self.body)
        response_json = json.loads(second_response.data.decode('utf-8'))
        self.assertEqual(second_response.status_code, 409)

    def test_login(self):
        response = self.send_post('/auth/login', self.body)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response_json)

    def test_login_fail(self):
        body = {
            "username": "malik",
            "password": "invalid"
        }
        response = self.send_post('/auth/login', body)
        self.assertEqual(response.status_code, 401)
