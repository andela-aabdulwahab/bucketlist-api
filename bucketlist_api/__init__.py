from flask import Flask, Blueprint
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
    api_blueprint = Blueprint("api", __name__, url_prefix='/')
    app.register_blueprint(api_blueprint)
    return app
