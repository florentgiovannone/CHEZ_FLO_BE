from http import HTTPStatus
from flask import request, g
import jwt
from functools import wraps
from config.environment import SECRET

from app import db
from models.users_model import UserModel


def secure_route(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):
        raw_token = request.headers.get("Authorization")
        if not raw_token:
            return {"message": "not authorised"}, HTTPStatus.UNAUTHORIZED
        token = raw_token.replace("Bearer ", "")

        try:
            print("Token was valid")
            payload = jwt.decode(token, SECRET, "HS256")
            user_id = payload["sub"]
            user = db.session.query(UserModel).get(user_id)
            g.current_user = user
            print("current user is: ", g.current_user.username, g.current_user)

            return route_function(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            print("Expired")
            return {"message": "Token is expired"}, HTTPStatus.UNAUTHORIZED
        except Exception:
            print("Issue with token")
            return {"message": "not authorised"}, HTTPStatus.UNAUTHORIZED

    return wrapper
