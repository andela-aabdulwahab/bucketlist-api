import os, sys, inspect

# Append Curent path to the system path to allow model visibility
currentdir = os.path.dirname(os.path.abspath(inspect.
                             getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from flask import jsonify, request, abort, make_response, url_for
from flask_httpauth import HTTPBasicAuth
from bucketlist_api import create_app, api
from bucketlist_api.config import DevConfig
from bucketlist_api.resources.bucketlistapi import BucketListAPI
from bucketlist_api.resources.itemlistapi import ItemListAPI
from bucketlist_api.resources.createuserapi import CreateUserAPI
from bucketlist_api.resources.loginuserapi import LoginUserAPI
from bucketlist_api.resources.helpapi import HelpAPI

# initialization
app = create_app(DevConfig)

api.add_resource(HelpAPI, '/help', endpoint='help')
api.add_resource(CreateUserAPI, '/auth/register', endpoint='register')
api.add_resource(LoginUserAPI, '/auth/login', endpoint='login')
api.add_resource(BucketListAPI, '/bucketlists', '/bucketlists/<int:id>',
                 endpoint='bucketlists')
api.add_resource(ItemListAPI, '/bucketlists/<int:id>/items',
                 '/bucketlists/<int:id>/items/<int:item_id>', endpoint='items')
