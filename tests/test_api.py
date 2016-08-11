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
from bucketlist_api import create_app, db
from bucketlist_api.api import api
from bucketlist_api.config import TestConfig
from bucketlist_api.resources.bucketlistapi import BucketListAPI
from bucketlist_api.resources.itemlistapi import ItemListAPI
from bucketlist_api.resources.createuserapi import CreateUserAPI
from bucketlist_api.resources.loginuserapi import LoginUserAPI
from bucketlist_api.resources.helpapi import HelpAPI


def send_post(test_client, url, body, headers=None):
    response = test_client.post(url, data=json.dumps(body), headers=headers,
                                content_type="application/json")
    return response


def register_a_user(test_client, username):
    body = {
        "username": username,
        "password": "malik123",
      }
    response = send_post(test_client, '/v1/auth/register', body)
    response_json = json.loads(response.data.decode('utf-8'))
    return response_json['token']


def post_a_bucketlist(test_client, token):
    headers = authorization_header(token)
    body = {
        "name": "Travel the world",
      }
    response = send_post(test_client, '/v1/bucketlists', body, headers)
    return response


def authorization_header(token):
    headers = {
        'Authorization': 'Basic ' + (b64encode((token+':unused')
                                               .encode('utf-8'))
                                     .decode('utf-8'))
      }
    return headers


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
        self.response = send_post(self.test_client, '/v1/auth/register',
                                  self.body)

    def test_create_user(self):
        response_json = json.loads(self.response.data.decode('utf-8'))
        self.assertEqual(self.response.status_code, 201)
        self.assertIn('token', response_json)

    def test_create_user_username_required(self):
        response_json = json.loads(self.response.data.decode('utf-8'))
        self.assertEqual(self.response.status_code, 400)
        self.assertIn('message', response_json)

    def test_user_exist(self):
        second_response = send_post(self.test_client, '/v1/auth/register', self.body)
        response_json = json.loads(second_response.data.decode('utf-8'))
        self.assertEqual(second_response.status_code, 400)

    def test_login(self):
        response = send_post(self.test_client, '/v1/auth/login', self.body)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response_json)

    def test_login_fail(self):
        body = {
            "username": "malik",
            "password": "invalid"
          }
        response = send_post(self.test_client, '/v1/auth/login', body)
        self.assertEqual(response.status_code, 400)


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
        self.token = register_a_user(self.test_client, "wahabmalik")
        self.response = post_a_bucketlist(self.test_client, self.token)

    def tearDown(self):
        User.query.filter_by(username='wahabmalik').delete()
        BucketList.query.filter_by(id=1).delete()
        db.session.commit()

    def get_bucketlists(self, id=None):
        headers = authorization_header(self.token)
        if id:
            response = response = self.test_client.get('/v1/bucketlists/'+id,
                                                       headers=headers)
        else:
            response = self.test_client.get('/v1/bucketlists', headers=headers)
        response_json = json.loads(response.data.decode('utf-8'))
        return response, response_json

    def test_create_bucketlist(self):
        self.assertEqual(self.response.status_code, 201)

    def test_unauthorize_access(self):
        response = self.test_client.post('/v1/bucketlists')
        error = ('"{\\n  \\"Error\\": \\"Invalid token Supplied or token has '
                 'expired, Login again to get access token\\"\\n}\\n"')
        response_json = json.dumps(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(error, response_json)

    def test_create_bucketlist_name_required(self):
        headers = authorization_header(self.token)
        response = self.test_client.post('/v1/bucketlists', headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_get_bucketlists(self):
        response, response_json = self.get_bucketlists()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response_json), 0)

    def test_get_bucketlists_pagination(self):
        body = {"name": "For Work"}
        body2 = {"name": "For Relationship"}
        headers = authorization_header(self.token)
        bucketlist1 = send_post(self.test_client, '/v1/bucketlists', body,
                                headers=headers)
        bucketlist = send_post(self.test_client, '/v1/bucketlists', body2,
                               headers=headers)
        response = self.test_client.get('/v1/bucketlists?limit=1&page=2',
                                        headers=headers)
        response_json = json.dumps(response.data.decode('utf-8'))
        BucketList.query.filter_by(id=2).delete()
        BucketList.query.filter_by(id=3).delete()
        self.assertIn('next', response_json)
        self.assertIn('previous', response_json)

    def test_get_bucketlists_search(self):
        headers = authorization_header(self.token)
        response = self.test_client.get('/v1/bucketlists?q=travel&limit=200',
                                        headers=headers)
        response_json = json.dumps(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('bucketlist', response_json)

    def test_get_single_bucketlist(self):
        response, response_json = self.get_bucketlists("1")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response_json), 0)

    def test_get_invalid_bucketlist(self):
        response, response_json = self.get_bucketlists("20")
        self.assertEqual(response.status_code, 404)

    def test_update_bucketlists(self):
        headers = authorization_header(self.token)
        body = {
            "is_public": True,
            "name": "Travel to paris",
          }
        response = self.test_client.put('/v1/bucketlists/1',
                                        data=json.dumps(body), headers=headers)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response_json)

    def test_update_invalid(self):
        headers = authorization_header(self.token)
        response = self.test_client.put('/v1/bucketlists/20', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_bucketlist(self):
        headers = authorization_header(self.token)
        response = self.test_client.delete('/v1/bucketlists/1',
                                           headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_delete_bucketlist_invalid(self):
        headers = authorization_header(self.token)
        response = self.test_client.delete('/v1/bucketlists/10',
                                           headers=headers)
        self.assertEqual(response.status_code, 404)


class TestItemAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        api.add_resource(CreateUserAPI, '/auth/register', endpoint='register')
        api.add_resource(BucketListAPI, '/bucketlists',
                                        '/bucketlists/<int:id>',
                                        endpoint='bucketlists')
        api.add_resource(ItemListAPI, '/bucketlists/<int:bucketlist_id>/items',
                         '/bucketlists/<int:bucketlist_id>/items/'
                         '<int:item_id>', endpoint='items')
        db.create_all()
        self.test_client = self.app.test_client()
        self.token = register_a_user(self.test_client, "adeyimalik")
        post_a_bucketlist(self.test_client, self.token)
        self.response = self.post_an_item()

    def tearDown(self):
        User.query.filter_by(username='adeyimalik').delete()
        BucketList.query.filter_by(id=1).delete()
        db.session.commit()

    def put_item(self, headers, id):
        body = {
            "name": "Climb the Eiffel Tower",
            "done": True
          }
        response = self.test_client.put('/v1/bucketlists/1/items/'+id,
                                        data=json.dumps(body),
                                        content_type="application/json",
                                        headers=headers)
        return response

    def post_an_item(self):
        headers = authorization_header(self.token)
        body = {
            "name": "Visit Brazil",
          }
        return send_post(self.test_client, '/v1/bucketlists/1/items', body,
                         headers=headers)

    def test_post_item(self):
        self.assertEqual(self.response.status_code, 201)
        response_json = json.loads(self.response.data.decode('utf-8'))
        self.assertGreater(len(response_json['items']), 0)

    def test_post_item_invalid(self):
        headers = authorization_header(self.token)
        response = self.test_client.post('/v1/bucketlists/10/items',
                                         headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_post_item_unauthorized(self):
        token = register_a_user(self.test_client, "wahabwahab")
        headers = authorization_header(token)
        response = self.test_client.post('/v1/bucketlists/1/items',
                                         headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_update_item(self):
        headers = authorization_header(self.token)
        response = self.put_item(headers, '1')
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response_json['items']), 0)

    def test_update_item_invalid(self):
        headers = authorization_header(self.token)
        response = self.put_item(headers, '100')
        self.assertEqual(response.status_code, 404)

    def test_update_item_unauthorized(self):
        token = register_a_user(self.test_client, "wahabwahab1")
        headers = authorization_header(token)
        response = self.put_item(headers, '1')
        self.assertEqual(response.status_code, 403)

    def test_delete_bucketlist(self):
        headers = authorization_header(self.token)
        response = self.test_client.delete('/v1/bucketlists/1/items/1',
                                           headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_delete_item_invalid(self):
        headers = authorization_header(self.token)
        response = self.test_client.delete('/v1/bucketlists/1/items/10',
                                           headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_update_item_unauthorized(self):
        token = register_a_user(self.test_client, "wahab")
        headers = authorization_header(token)
        response = self.test_client.delete('/v1/bucketlists/1/items/1',
                                           headers=headers)
        self.assertEqual(response.status_code, 403)


class TestHelpAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.app_context().push()
        api.add_resource(HelpAPI, '/help', endpoint='help')
        self.test_client = self.app.test_client()

    def test_get_help(self):
        response = self.test_client.get('/v1/help')
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response_json)
