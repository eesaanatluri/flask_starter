from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()

# creating login manager object
login_manager = LoginManager()

# Load the Config File
def create_app(config_name):
    # initialize the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.loginmessage = "you must be logged in to access this page."
    login_manager.login_view = "auth.login"

    return app
