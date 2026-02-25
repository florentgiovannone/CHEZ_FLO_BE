"""Users controller for managing user authentication, registration, and profile updates."""

import re
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from smtplib import SMTPException
import jwt
from flask import Blueprint, request, jsonify, g
from flask_mail import Message
from marshmallow.exceptions import ValidationError
from application import db, app, mail, limiter
from config.environment import SECRET
from middleware.secure_route import secure_route, role_required
from models.users_model import UserModel
from serializers.users_serializer import UserSerializer

user_serializer = UserSerializer()
router = Blueprint("users", __name__)


# --- Signup section ---
@router.route("/signup", methods=["POST"])
@limiter.limit("3 per hour")
def signup():
    """Handle user registration by validating input and creating a new user."""
    try:
        user_dictionary = request.json
        firstname_to_enter = user_dictionary.get("firstname")
        if not firstname_to_enter:
            return (
                jsonify({"error": "you need to enter an firstname"}),
                HTTPStatus.BAD_REQUEST,
            )
        lastname_to_enter = user_dictionary.get("lastname")
        if not lastname_to_enter:
            return (
                jsonify({"error": "you need to enter an lastname"}),
                HTTPStatus.BAD_REQUEST,
            )

        email_to_enter = user_dictionary.get("email")
        if not email_to_enter:
            return (
                jsonify({"error": "you need to enter an email"}),
                HTTPStatus.BAD_REQUEST,
            )
        email = (
            db.session.query(UserModel)
            .filter_by(email=user_dictionary["email"])
            .first()
        )
        if email:
            return jsonify({"error": "The email already exist"}), HTTPStatus.BAD_REQUEST

        username_to_enter = user_dictionary.get("username")
        if not username_to_enter:
            return (
                jsonify({"error": "you need to enter a username"}),
                HTTPStatus.BAD_REQUEST,
            )
        username = (
            db.session.query(UserModel)
            .filter_by(username=user_dictionary["username"])
            .first()
        )
        if username:
            return (
                jsonify({"error": "The username already exist"}),
                HTTPStatus.BAD_REQUEST,
            )
        if username == "":
            return (
                jsonify({"error": "you need to enter an email"}),
                HTTPStatus.BAD_REQUEST,
            )

        password = user_dictionary.get("password")
        password_confirmation = user_dictionary.get("password_confirmation")
        if password != password_confirmation:
            return jsonify({"error": "Passwords do not match"}), HTTPStatus.BAD_REQUEST
        spec_chart = ["!", "@", "#", "$", "%", "&", "*"]
        if len(password) < 8:
            return (
                jsonify(
                    {"error": "Password needs to be a minimum of 8 characters long"}
                ),
                HTTPStatus.BAD_REQUEST,
            )
        if len(password) > 20:
            return (
                jsonify(
                    {"error": "Password needs to be a maximum of 20 characters long"}
                ),
                HTTPStatus.BAD_REQUEST,
            )
        if not re.search("[a-z]", password):
            return (
                jsonify(
                    {"error": "Password needs to contain at least 1 lowercase letter"}
                ),
                HTTPStatus.BAD_REQUEST,
            )
        if not re.search("[A-Z]", password):
            return (
                jsonify(
                    {"error": "Password needs to contain at least 1 uppercase letter"}
                ),
                HTTPStatus.BAD_REQUEST,
            )
        if not re.search("[0-9]", password):
            return (
                jsonify({"error": "Password needs to contain at least 1 digit"}),
                HTTPStatus.BAD_REQUEST,
            )
        if not any(char in spec_chart for char in password):
            return (
                jsonify(
                    {"error": "Password needs to contain at least 1 special character"}
                ),
                HTTPStatus.BAD_REQUEST,
            )
        else:
            user_model = user_serializer.load(user_dictionary)
            user_model.role = "user"
            db.session.add(user_model)
            db.session.commit()
            return user_serializer.jsonify(user_model)
    except ValidationError as _:
        return (
            jsonify(
                {
                    "error": "Something went wrong",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )
    except SMTPException as _:
        return {"error": "Something went very wrong"}


# --- Login section ---
@router.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Authenticate a user and return a JWT token."""
    try:
        credentials_dictionary = request.json
    except ValidationError as _:
        return {
            "errors": _.messages,
            "message": "Something went wrong",
        }, HTTPStatus.BAD_REQUEST
    except SMTPException as _:
        return {"error": "Something went very wrong"}, HTTPStatus.BAD_REQUEST

    user = (
        db.session.query(UserModel)
        .filter_by(username=credentials_dictionary["username"])
        .first()
    )

    if not user or not user.validate_password(credentials_dictionary["password"]):
        return jsonify({"error": "Login failed. Try again"}), HTTPStatus.UNAUTHORIZED

    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(user.id),
        "role": user.role,
    }
    secret = SECRET

    try:
        token = jwt.encode(payload, secret, algorithm="HS256")
        return jsonify({"message": "Login successful.", "token": token})

    except jwt.PyJWTError as _:
        return (
            jsonify({"error": "Token generation failed"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Get Current User section ---
@router.route("/user", methods=["GET"])
@secure_route
def get_current_user():
    """Get the current user by their ID from the database."""
    try:
        user = db.session.query(UserModel).get(g.current_user.id)
        return user_serializer.jsonify(user)
    except ValidationError as _:
        return {
            "errors": _.messages,
            "message": "Something went wrong",
        }, HTTPStatus.BAD_REQUEST
    except SMTPException as _:
        return {"message": "Something went very wrong"}


# --- Display All Users section ---
@router.route("/users", methods=["GET"])
@role_required("admin", "superadmin")
def get_current_users():
    """Get all users from the database."""
    user = db.session.query(UserModel).all()
    return user_serializer.jsonify(user, many=True)


# --- Display Single User section ---
@router.route("/user/<int:user_id>", methods=["GET"])
@role_required("admin", "superadmin")
def get_single_user(user_id):
    """Get a single user by their ID from the database."""
    post = db.session.query(UserModel).get(user_id)
    if post is None:
        return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)
    return user_serializer.jsonify(post)


# --- Update User section ---
@router.route("/user/<int:user_id>", methods=["PUT"])
@secure_route
def update_user(user_id):
    """Update a user by their ID in the database."""
    try:
        if g.current_user.id != user_id and g.current_user.role not in (
            "admin",
            "superadmin",
        ):
            return {"message": "Forbidden"}, HTTPStatus.FORBIDDEN
        user = db.session.query(UserModel).get(user_id)
        if user is None:
            return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)
        user_data = request.json
        user.firstname = user_data.get("firstname", user.firstname)
        user.lastname = user_data.get("lastname", user.lastname)
        user.username = user_data.get("username", user.username)
        user.email = user_data.get("email", user.email)
        user.image = user_data.get("image", user.image)
        db.session.commit()
        return user_serializer.jsonify(user)

    except ValidationError as _:
        return {
            "errors": _.messages,
            "message": "Something went wrong",
        }, HTTPStatus.BAD_REQUEST

    except SMTPException as _:
        return {"message": "Something went very wrong"}, HTTPStatus.BAD_REQUEST


# --- Delete User section ---
@router.route("/user/<int:user_id>", methods=["DELETE"])
@role_required("admin", "superadmin")
def delete_user(user_id):
    """Delete a user by their ID from the database."""
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)

    user.remove()
    return jsonify({"error": "user deleted"})


# --- Change Password section ---
@router.route("/change-password", methods=["PUT"])
@limiter.limit("5 per hour")
@secure_route
def change_password():
    """Change a user's password by their ID in the database."""
    data = request.json
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    user = db.session.query(UserModel).get(g.current_user.id)

    if not user or not user.validate_password(current_password):
        return jsonify({"error": "Incorrect current password"}), HTTPStatus.UNAUTHORIZED

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), HTTPStatus.BAD_REQUEST

    # Password validation (strength check)
    if len(new_password) < 8:
        return (
            jsonify({"error": "Password must be at least 8 characters long"}),
            HTTPStatus.BAD_REQUEST,
        )
    if not any(c.islower() for c in new_password):
        return (
            jsonify({"error": "Password must contain a lowercase letter"}),
            HTTPStatus.BAD_REQUEST,
        )
    if not any(c.isupper() for c in new_password):
        return (
            jsonify({"error": "Password must contain an uppercase letter"}),
            HTTPStatus.BAD_REQUEST,
        )
    if not any(c.isdigit() for c in new_password):
        return (
            jsonify({"error": "Password must contain a digit"}),
            HTTPStatus.BAD_REQUEST,
        )
    if not any(c in "!@#$%&*" for c in new_password):
        return (
            jsonify({"error": "Password must contain a special character (!@#$%&*)"}),
            HTTPStatus.BAD_REQUEST,
        )

    # ✅ Use the `password` setter, not `set_password`
    user.password = new_password
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), HTTPStatus.OK


@router.route("/send-confirmation", methods=["POST"])
@limiter.limit("3 per hour")
def send_confirmation():
    """Send a confirmation email to a user."""
    data = request.json
    email = data.get("email")
    username = data.get("username")

    # Validate email format
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not email or not re.match(email_pattern, email):
        return jsonify({"error": "Invalid email address"}), 400

    try:
        msg = Message(
            subject="Confirmation Email",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email],
        )
        msg.body = f"Hi {username}, thanks for registering to our website!"
        mail.send(msg)
        return jsonify({"message": "Confirmation email sent."}), 200
    except SMTPException as _:
        return jsonify({"error": "Failed to send email"}), 500


@router.route("/user/<int:user_id>/role", methods=["PUT"])
@role_required("superadmin")  # Only superadmins can change roles
def update_user_role(user_id):
    """Update a user's role by their ID in the database."""
    data = request.json
    new_role = data.get("role")

    if new_role not in ("user", "admin", "superadmin"):
        return jsonify({"error": "Invalid role"}), HTTPStatus.BAD_REQUEST

    # Prevent superadmin from demoting themselves
    if g.current_user.id == user_id:
        return {"error": "Cannot change your own role"}, HTTPStatus.FORBIDDEN

    user = db.session.query(UserModel).get(user_id)
    if not user:
        return {"error": "User not found"}, HTTPStatus.NOT_FOUND

    user.role = new_role
    db.session.commit()
    return user_serializer.jsonify(user)
