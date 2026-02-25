"""User serializer module defining the UserSerializer for user authentication and management."""
import re
from marshmallow import fields, ValidationError
from app import marshy
from models.users_model import UserModel


def validate_password(password):
    """Validate the password against the stored hash."""
    spec_chart = ["!", "@", "#", "$", "%", "&", "*"]
    if len(password) < 8:
        raise ValidationError("Password needs to be a minimum of 8 characters long")
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
    """Serializer for the UserModel."""

    password = fields.String(required=True, validate=validate_password)

    class Meta:
        """Meta class for the UserSerializer."""

        model = UserModel
        load_instance = True
        load_only = ("password", "password_hash", "password_confirmation")
        dump_only = ("role",)
