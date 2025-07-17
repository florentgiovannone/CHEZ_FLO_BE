from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from config.environment import db_URI
from flask_cors import CORS
from flask_mail import Mail

app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return "Chez Flo API is running!"


@app.route("/hello", methods=["GET"])
def hello():
    return "Hello World!"


app.config["SQLALCHEMY_DATABASE_URI"] = db_URI

CORS(app)
db = SQLAlchemy(app)
marshy = Marshmallow(app)
bcrypt = Bcrypt(app)

# Mail configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "giovannoneflorent@gmail.com"
app.config["MAIL_PASSWORD"] = "bcnh idnc yebt fady"

mail = Mail(app)

from controllers import users_controller
from controllers import content_controller
from controllers import carousels_controller
from controllers import menus_controller
from controllers import grid_controller

app.register_blueprint(users_controller.router, url_prefix="/api")
app.register_blueprint(content_controller.router, url_prefix="/api")
app.register_blueprint(carousels_controller.router, url_prefix="/api")
app.register_blueprint(menus_controller.router, url_prefix="/api")
app.register_blueprint(grid_controller.router, url_prefix="/api")
