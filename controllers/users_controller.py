from http import HTTPStatus
from flask import Blueprint, request, jsonify, g
from marshmallow.exceptions import ValidationError
from app import db
from models.users_model import UserModel
from serializers.users_serializer import UserSerializer
from datetime import datetime, timedelta, timezone
from config.environment import SECRET
import jwt
from middleware.secure_route import secure_route
import re


user_serializer = UserSerializer()
router = Blueprint("users", __name__)


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


@router.route("/users", methods=["GET"])
def get_current_users():
    user = db.session.query(UserModel).all()
    print(user_serializer.jsonify(user, many=True))
    return user_serializer.jsonify(user, many=True)


@router.route("/users/<int:user_id>", methods=["GET"])
def get_single_user(user_id):
    post = db.session.query(UserModel).get(user_id)
    if post is None:
        return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)
    return user_serializer.jsonify(post)


@router.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
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

    except ValidationError as e:
        return {
            "errors": e.message,
            "message": "Something went wrong",
        }, HTTPStatus.BAD_REQUEST

    except Exception as e:
        return {"message": "Something went very wrong"}, HTTPStatus.BAD_REQUEST


@router.route("/all_users", methods=["GET"])
def get_all_user():
    users = db.session.query(UserModel).all()
    print(user_serializer.jsonify(users, many=True))
    return user_serializer.jsonify(users, many=True)


@router.route("/users/<int:user_id>", methods=["DELETE"])
@secure_route
def delete_user(user_id):
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)

    user.remove()
    return jsonify({"error": "user deleted"})
