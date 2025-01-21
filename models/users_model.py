from sqlalchemy.ext.hybrid import hybrid_property
from app import db, bcrypt

class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=True)
    password_confirmation = db.Column(db.Text, nullable=True)
    image = db.Column(db.Text, nullable=True)

    @hybrid_property
    def password(self):
        pass

    @password.setter
    def password(self, password_plaintext):
        encoded_hashed_pw = bcrypt.generate_password_hash(password_plaintext)
        self.password_hash = encoded_hashed_pw.decode("utf-8")

    def validate_password(self, password_plaintext):
        return bcrypt.check_password_hash(self.password_hash, password_plaintext)

    def remove(self):
        db.session.delete(self)
        db.session.commit()
