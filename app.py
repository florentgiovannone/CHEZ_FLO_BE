from flask import Flask, jsonify, request
import logging
from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from config.environment import db_URI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.is_json:
        logger.info(f"Body: {request.get_json()}")


@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status_code}")
    return response


@app.route("/", methods=["GET"])
def root():
    return "Chez Flo API is running!"


@app.route("/hello", methods=["GET"])
def hello():
    return "Hello World!"


@app.errorhandler(404)
def not_found(error):
    logger.error(f"404 error: {error}")
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "Something went wrong"}), 500


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
