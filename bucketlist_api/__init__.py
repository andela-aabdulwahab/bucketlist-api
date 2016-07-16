""" Script handle app factory creation."""

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_api import FlaskAPI
from bucketlist_api.custom_error import errors

db = SQLAlchemy()
api_blueprint = Blueprint("api", __name__, url_prefix='/v1')
api = Api(api_blueprint, errors=errors)


def create_app(ConfigObj):
    """Create an instance of Flask with the right
    configuration.

    Arguments:
        env:String specifying the development enviroment
    Return:
        Flask App instance
    """
    app = FlaskAPI(__name__)
    app.config.from_object(ConfigObj)
    db.init_app(app)
    app.register_blueprint(api_blueprint)
    return app
