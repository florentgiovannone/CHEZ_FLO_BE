"""Main application module for the Flask application."""

import logging
import os
from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

from config.environment import db_URI
from controllers import users_controller
from controllers import content_controller
from controllers import carousels_controller
from controllers import menus_controller
from controllers import grid_controller

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.before_request
def log_request_info():
    """Log request information."""
    logger.info("Request: %s %s", request.method, request.url)
    safe_headers = {
        k: v for k, v in request.headers if k.lower() not in ("authorization", "cookie")
    }
    logger.info("Headers: %s", safe_headers)


@app.after_request
def log_response_info(response):
    """Log response information."""
    logger.info("Response: %s", response.status_code)
    return response


@app.route("/", methods=["GET"])
def root():
    """Root route."""
    return "Chez Flo API is running!"


@app.route("/hello", methods=["GET"])
def hello():
    """Hello route."""
    return "Hello World!"


@app.errorhandler(404)
def not_found(error):
    """Log 404 error."""
    logger.error("404 error: %s", error)
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Log 500 error."""
    logger.error("500 error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Log unhandled exception."""
    logger.error("Unhandled exception: %s", e)
    return jsonify({"error": "Something went wrong"}), 500


app.config["SQLALCHEMY_DATABASE_URI"] = db_URI
CORS(app, origins=["https://chezflodemo.netlify.app/", "https://chezflo.vercel.app"])
db = SQLAlchemy(app)
marshy = Marshmallow(app)
bcrypt = Bcrypt(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Mail configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
if not app.config["MAIL_USERNAME"]:
    raise ValueError("MAIL_USERNAME environment variable must be set")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)
Talisman(
    app,
    force_https=not app.debug,  # Force HTTPS in production, skip locally
    content_security_policy=None,  # Set to None since you're an API, not serving HTML
    session_cookie_secure=True,
    session_cookie_httponly=True,
)

app.register_blueprint(users_controller.router, url_prefix="/api")
app.register_blueprint(content_controller.router, url_prefix="/api")
app.register_blueprint(carousels_controller.router, url_prefix="/api")
app.register_blueprint(menus_controller.router, url_prefix="/api")
app.register_blueprint(grid_controller.router, url_prefix="/api")
