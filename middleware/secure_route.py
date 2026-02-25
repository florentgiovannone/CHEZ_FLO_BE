"""Secure route middleware for authentication and role-based access control."""

from functools import wraps
from http import HTTPStatus

import jwt
from flask import request, g

from app import db
from config.environment import SECRET
from models.users_model import UserModel


def secure_route(route_function):
    """Decorator to check if the user is authenticated."""

    @wraps(route_function)
    def wrapper(*args, **kwargs):
        raw_token = request.headers.get("Authorization")
        if not raw_token:
            return {"message": "Not authorized"}, HTTPStatus.UNAUTHORIZED

        token = raw_token.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id or not isinstance(user_id, str):
                return {
                    "message": "Invalid token, 'sub' field missing or malformed"
                }, HTTPStatus.UNAUTHORIZED

            user = db.session.query(UserModel).get(user_id)
            if not user:
                return {"message": "User not found"}, HTTPStatus.UNAUTHORIZED

            g.current_user = user
            return route_function(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return {"message": "Token is expired"}, HTTPStatus.UNAUTHORIZED

        except jwt.DecodeError:
            return {"message": "Invalid token"}, HTTPStatus.UNAUTHORIZED

        except jwt.InvalidTokenError:
            return {"message": "Invalid token"}, HTTPStatus.UNAUTHORIZED

        except jwt.PyJWTError:
            return {"message": "Not authorized"}, HTTPStatus.UNAUTHORIZED

    return wrapper


def role_required(*allowed_roles):
    """Decorator to check if the user has the required role."""

    def decorator(route_function):
        @wraps(route_function)
        def wrapper(*args, **kwargs):
            raw_token = request.headers.get("Authorization")
            if not raw_token:
                return {"message": "Not authorized"}, HTTPStatus.UNAUTHORIZED

            token = raw_token.replace("Bearer ", "")
            try:
                payload = jwt.decode(token, SECRET, algorithms=["HS256"])
                user_id = payload.get("sub")
                if not user_id or not isinstance(user_id, str):
                    return {
                        "message": "Invalid token, 'sub' field missing or malformed"
                    }, HTTPStatus.UNAUTHORIZED

                user = db.session.query(UserModel).get(user_id)
                if not user:
                    return {"message": "User not found"}, HTTPStatus.UNAUTHORIZED

                g.current_user = user

                # Role check — this is the key difference from secure_route
                if g.current_user.role not in allowed_roles:
                    return {
                        "message": "Forbidden: insufficient permissions"
                    }, HTTPStatus.FORBIDDEN

                return route_function(*args, **kwargs)

            except jwt.ExpiredSignatureError:
                return {"message": "Token is expired"}, HTTPStatus.UNAUTHORIZED

            except jwt.DecodeError:
                return {"message": "Invalid token"}, HTTPStatus.UNAUTHORIZED

            except jwt.InvalidTokenError:
                return {"message": "Invalid token"}, HTTPStatus.UNAUTHORIZED

            except jwt.PyJWTError:
                return {"message": "Not authorized"}, HTTPStatus.UNAUTHORIZED

        return wrapper

    return decorator
