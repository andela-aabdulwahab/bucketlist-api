from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from bucketlist_api.custom_error import errors

db = SQLAlchemy()
api_blueprint = Blueprint("api", __name__)
api = Api(api_blueprint, errors=errors)

def create_app(ConfigObj):
    """Create an instance of Flask with the right
    configuration.

    Arguments:
        env:String specifying the development enviroment
    Return:
        Flask App instance
    """
    app = Flask(__name__)
    app.config.from_object(ConfigObj)
    db.init_app(app)
    app.register_blueprint(api_blueprint)
    return app
