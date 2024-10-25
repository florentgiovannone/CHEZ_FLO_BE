from marshmallow import fields, ValidationError
from app import marshy
from models.users_model import UserModel
import re

def validate_password(password):
    spec_chart = ["!", "@", "#", "$", "%", "&", "*"]
    if len(password) < 8:
        raise ValidationError ("Password needs to be a minimum of 8 characters long")
    if len(password) > 20:
        raise ValidationError("Password needs to be a maximum of 20 characters long")
    if not re.search("[a-z]", password):
        raise ValidationError("Password needs to contain at least 1 lowercase letter")
    if not re.search("[A-Z]", password):
        raise ValidationError("Password needs to contain at least 1 uppercase letter")
    if not re.search("[0-9]", password):
        raise ValidationError("Password needs to contain at least 1 digit")
    if not any(char in spec_chart for char in password):
        raise ValidationError("Password needs to contain at least 1 special character")

class UserSerializer(marshy.SQLAlchemyAutoSchema):
    password = fields.String(require=True, validate=validate_password)

    class Meta:
        model = UserModel
        load_instance = True
        Load_only = ("password", "password_hash", "password_confirmation")
