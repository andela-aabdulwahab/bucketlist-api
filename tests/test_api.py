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

class TestBucketListAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        api.add_resource(CreateUserAPI, '/auth/register', endpoint='register')
        api.add_resource(BucketListAPI, '/bucketlists',
                                        '/bucketlists/<int:id>',
                                        endpoint='bucketlists')
        db.create_all()
        self.test_client = self.app.test_client()
        self.token = self.register_a_user()
        self.response = self.post_a_bucketlist()

    def tearDown(self):
        User.query.filter_by(username='wahabmalik').delete()

    def send_post(self, url, body, headers=None):
        response = self.test_client.post(url,
                                         data=json.dumps(body),
                                         content_type="application/json",
                                         headers=headers)
        return response

    def register_a_user(self):
        body = {
            "username": "wahabmalik",
            "password": "malik123",
          }
        response = self.send_post('/auth/register', body)
        response_json = json.loads(response.data.decode('utf-8'))
        return response_json['token']

    def post_a_bucketlist(self):
        headers = self.authorization_header()
        body = {
            "name": "Travel the world",
          }
        response = self.send_post('/bucketlists', body, headers)
        return response

    def authorization_header(self):
        headers = {
            'Authorization': 'Basic ' + (b64encode((self.token+':unused')
                                                   .encode('utf-8'))
                                         .decode('utf-8'))
          }
        return headers

    def get_bucketlists(self, id=None):
        headers = self.authorization_header()
        if id:
            response = response = self.test_client.get('/bucketlists/'+id,
                                                       headers=headers)
        else:
            response = self.test_client.get('/bucketlists', headers=headers)
        response_json = json.loads(response.data.decode('utf-8'))
        return response, response_json

    def test_post_bucketlist(self):
        self.assertEqual(self.response.status_code, 201)

    def test_unauthorize_access(self):
        response = self.test_client.post('/bucketlists')
        self.assertEqual(response.status_code, 401)

    def test_bucketlist_name_required(self):
        headers = self.authorization_header()
        response = self.test_client.post('/bucketlists', headers=headers)

    def test_get_bucketlists(self):
        response, response_json = self.get_bucketlists()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response_json['bucketlists']), 0)

    def test_get_id_bucketlist(self):
        response, response_json = self.get_bucketlists("1")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response_json['bucketlists']), 0)

    def test_get_invalid_bucketlist(self):
        response, response_json = self.get_bucketlists("20")
        self.assertEqual(response.status_code, 404)

    def test_put_bucketlists(self):
        headers = self.authorization_header()
        body = {
            "is_public": True,
            "name": "Travel to paris",
          }
        response = self.test_client.put('/bucketlists/1',
                                        data=json.dumps(body), headers=headers)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('bucketlist', response_json)

    def test_put_invalid(self):
        headers = self.authorization_header()
        response = self.test_client.put('/bucketlists/20', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_bucketlist(self):
        headers = self.authorization_header()
        body = {
            "name": "Run a marathon"
          }
        post_response = self.send_post('/bucketlists', body, headers)
        response = self.test_client.delete('/bucketlists/2', headers=headers)
        self.assertEqual(response.status_code, 204)
