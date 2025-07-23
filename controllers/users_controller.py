from http import HTTPStatus
from flask import Blueprint, request, jsonify, g
from marshmallow.exceptions import ValidationError
from app import db, app
from models.users_model import UserModel
from serializers.users_serializer import UserSerializer
from datetime import datetime, timedelta, timezone
from config.environment import SECRET
import jwt
from middleware.secure_route import secure_route
import re
from flask_mail import Message
from app import mail

user_serializer = UserSerializer()
router = Blueprint("users", __name__)


# --- Signup section ---
@router.route("/signup", methods=["POST"])
def signup():
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
            db.session.add(user_model)
            db.session.commit()
            return user_serializer.jsonify(user_model)
    except ValidationError as e:
        return (
            jsonify(
                {
                    "error": "Something went wrong",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )
    except Exception as e:
        return {"error": "Something went very wrong"}


# --- Login section ---
@router.route("/login", methods=["POST"])
def login():
    credentials_dictionary = request.json

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
        "sub": str(user.id),  # Ensure sub is a string
    }
    secret = SECRET

    try:
        token = jwt.encode(payload, secret, algorithm="HS256")
        print(f"Generated Token: {token}")
        return jsonify({"message": "Login successful.", "token": token})

    except Exception as e:
        print(f"Error generating token: {e}")
        return (
            jsonify({"error": "Token generation failed"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Get urrent User section ---
@router.route("/user", methods=["GET"])
@secure_route
def get_current_user():
    try:
        user = db.session.query(UserModel).get(g.current_user.id)
        print(user_serializer.jsonify(user))
        return user_serializer.jsonify(user)
    except ValidationError as e:
        return {
            "errors": e.messages,
            "message": "Something went wrong",
        }, HTTPStatus.BAD_REQUEST
    except Exception as e:
        return {"message": "Something went very wrong"}


# --- Display All Users section ---
@router.route("/users", methods=["GET"])
def get_current_users():
    user = db.session.query(UserModel).all()
    print(user_serializer.jsonify(user, many=True))
    return user_serializer.jsonify(user, many=True)


# --- Display Single User section ---
@router.route("/user/<int:user_id>", methods=["GET"])
def get_single_user(user_id):
    post = db.session.query(UserModel).get(user_id)
    if post is None:
        return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)
    return user_serializer.jsonify(post)


# --- Update User section ---
import os
from werkzeug.utils import secure_filename
from flask import current_app


@router.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = db.session.query(UserModel).get(user_id)
        if user is None:
            return jsonify({"message": "User not found"}), HTTPStatus.NOT_FOUND

        # Handle file upload
        if "image" in request.files:
            image = request.files["image"]
            if image.filename != "":
                # Secure and save the file
                filename = secure_filename(image.filename)
                upload_folder = os.path.join(current_app.root_path, "static/uploads")

                # Optional: delete the old file if it exists
                if user.image:
                    old_path = os.path.join(upload_folder, user.image)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                # Save new image
                image.save(os.path.join(upload_folder, filename))
                user.image = filename

        # Update other user data (still in request.form, not JSON!)
        user.firstname = request.form.get("firstname", user.firstname)
        user.lastname = request.form.get("lastname", user.lastname)
        user.username = request.form.get("username", user.username)
        user.email = request.form.get("email", user.email)

        db.session.commit()
        return user_serializer.jsonify(user)

    except ValidationError as e:
        return {
            "errors": e.messages,
            "message": "Validation failed",
        }, HTTPStatus.BAD_REQUEST

    except Exception as e:
        print(e)
        return {
            "message": "Something went very wrong"
        }, HTTPStatus.INTERNAL_SERVER_ERROR


# --- Delete User section ---
@router.route("/user/<int:user_id>", methods=["DELETE"])
@secure_route
def delete_user(user_id):
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)

    user.remove()
    return jsonify({"error": "user deleted"})


# --- Change Password section ---
@router.route("/change-password", methods=["PUT"])
@secure_route
def change_password():
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
def send_confirmation():
    data = request.json
    email = data.get("email")
    username = data.get("username")

    # Validate email format
    import re

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
    except Exception as e:
        print(f"Email error: {e}")
        return jsonify({"error": "Failed to send email"}), 500
