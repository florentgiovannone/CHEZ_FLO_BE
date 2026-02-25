"""User model module defining the UserModel for authentication and user management."""
from sqlalchemy.ext.hybrid import hybrid_property
from application import db, bcrypt


class UserModel(db.Model):
    """Represents a user with authentication and role management."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=True)
    password_confirmation = db.Column(db.Text, nullable=True)
    image = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(20), nullable=False, default="user")
    __table_args__ = (
        db.CheckConstraint(
            role.in_(["user", "admin", "superadmin"]), name="valid_roles"
        ),
    )

    @hybrid_property
    def password(self):
        """Placeholder for the password property."""

    @password.setter
    def password(self, password_plaintext):
        encoded_hashed_pw = bcrypt.generate_password_hash(password_plaintext)
        self.password_hash = encoded_hashed_pw.decode("utf-8")

    def validate_password(self, password_plaintext):
        """Validate the password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password_plaintext)

    def remove(self):
        """Delete the user from the database."""
        db.session.delete(self)
        db.session.commit()
