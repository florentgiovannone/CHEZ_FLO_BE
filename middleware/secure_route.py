from http import HTTPStatus
from flask import request, g
import jwt
from functools import wraps
from config.environment import SECRET

from app import db
from models.users_model import UserModel


from functools import wraps
from flask import request, g
from http import HTTPStatus
import jwt


from functools import wraps
from flask import request, g
from http import HTTPStatus
import jwt


def secure_route(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        raw_token = request.headers.get("Authorization")
        if not raw_token:
            return {"message": "Not authorized"}, HTTPStatus.UNAUTHORIZED

        token = raw_token.replace("Bearer ", "")
        try:
            print("Decoding token...")
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            print("Decoded Payload:", payload)
            user_id = payload.get("sub")
            if not user_id or not isinstance(user_id, str):
                print("No 'sub' in token or 'sub' is not a string")
                return {
                    "message": "Invalid token, 'sub' field missing or malformed"
                }, HTTPStatus.UNAUTHORIZED
            user = db.session.query(UserModel).get(user_id)

            if not user:
                print("User not found")
                return {"message": "User not found"}, HTTPStatus.UNAUTHORIZED
            g.current_user = user
            print(f"Current user is: {g.current_user.username}")
            return route_function(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return {"message": "Token is expired"}, HTTPStatus.UNAUTHORIZED
        
        except jwt.DecodeError:
            print("Token decoding failed")
            return {"message": "Invalid token"}, HTTPStatus.UNAUTHORIZED
        
        except jwt.InvalidTokenError:
            print("Invalid token")
            return {"message": "Invalid token"}, HTTPStatus.UNAUTHORIZED
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {"message": "Not authorized"}, HTTPStatus.UNAUTHORIZED
        
    return wrapper
