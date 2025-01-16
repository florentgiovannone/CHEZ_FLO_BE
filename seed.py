from flask import Blueprint, request, jsonify, g
from app import app, db
from models.users_model import UserModel

with app.app_context():

    try:
        print("connected")
        db.drop_all()
        db.create_all()

        Florent = UserModel(
            firstname="Florent",
            lastname="Giovannone",
            username="flo",
            email="f.giovannone@me.com",
            password="Hello123",
            password_confirmation="Hello123",
        )

        db.session.add(Florent)
        db.session.commit()

        db.session.commit()
        print("seeded!")

    except Exception as e:
        print(e)


