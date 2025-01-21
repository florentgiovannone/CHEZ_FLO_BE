from http import HTTPStatus
from flask import Blueprint, request, jsonify, g
from marshmallow.exceptions import ValidationError
from app import db
from models.content_model import ContentModel
from serializers.content_serializer import ContentSerializer
from datetime import datetime, timedelta, timezone


content_serializer = ContentSerializer()
router = Blueprint("content", __name__)

@router.route("/content/<int:content_id>", methods=["PUT"])
def update_user(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "user not found"}, HTTPStatus.NOT_FOUND)
        content_data = request.json
        content.about_title = content_data.get("about_title", content.about_title)
        content.about_text = content_data.get("about_text", content.about_text)
        content.breakfast_menus_text = content_data.get(
            "breakfast_menus_text", content.breakfast_menus_text)
        content.breakfast_menus_file = content_data.get(
            "breakfast_menus_file", content.breakfast_menus_file
        )
        content.lunch_menus_text = content_data.get(
            "lunch_menus_text", content.lunch_menus_text
        )
        content.lunch_menus_file = content_data.get(
            "lunch_menus_file", content.lunch_menus_file
        )
        content.dinner_menus_text = content_data.get(
            "dinner_menus_text", content.dinner_menus_text
        )
        content.dinner_menus_file = content_data.get(
            "dinner_menus_file", content.dinner_menus_file
        )
        content.winelist_menus_text = content_data.get(
            "winelist_menus_text", content.winelist_menus_text
        )
        content.winelist_menus_text = content_data.get(
            "winelist_menus_text", content.winelist_menus_text
        )
        content.cocktail_menus_text = content_data.get(
            "cocktail_menus_text", content.cocktail_menus_text
        )
        content.cocktail_menus_file = content_data.get(
            "aboutTitle", content.cocktail_menus_file
        )
        content.image_one = content_data.get("image_one", content.image_one)
        content.image_two = content_data.get("image_two", content.image_two)
        content.image_three = content_data.get("image_three", content.image_three)
        content.image_four = content_data.get("image_four", content.image_four)
        content.image_five = content_data.get("image_five", content.image_five)
        content.image_six = content_data.get("image_six", content.image_six)
        content.reservation_title = content_data.get(
            "reservation_title", content.reservation_title
        )
        content.reservation_text = content_data.get(
            "reservation_text", content.reservation_text
        )
        content.breakfast_timing_title = content_data.get(
            "breakfast_timing_title", content.breakfast_timing_title
        )
        content.breakfast_timing_mtof = content_data.get(
            "breakfast_timing_mtof", content.breakfast_timing_mtof
        )
        content.breakfast_timing_sands = content_data.get(
            "breakfast_timing_sands", content.breakfast_timing_sands
        )
        content.lunch_timing_title = content_data.get(
            "lunch_timing_title", content.lunch_timing_title
        )
        content.lunch_timing_mtos = content_data.get(
            "lunch_timing_mtos", content.lunch_timing_mtos
        )
        content.lunch_timing_sun = content_data.get(
            "lunch_timing_sun", content.lunch_timing_sun
        )
        content.dinner_timing_title = content_data.get(
            "dinner_timing_title", content.dinner_timing_title
        )
        content.dinner_timing_mtos = content_data.get(
            "dinner_timing_mtos", content.dinner_timing_mtos
        )
        content.dinner_timing_sun = content_data.get(
            "dinner_timing_sun", content.dinner_timing_sun
        )
        content.reservation_line_one = content_data.get(
            "reservation_line_one", content.reservation_line_one
        )
        content.reservation_line_two = content_data.get(
            "reservation_line_two", content.reservation_line_two
        )
        content.phone = content_data.get("phone", content.phone)
        content.email = content_data.get("email", content.email)
        content.contact_title = content_data.get("contact_title", content.contact_title)
        content.contact_adress_one = content_data.get(
            "contact_adress_one", content.contact_adress_one
        )
        content.contact_adress_two = content_data.get(
            "contact_adress_two", content.contact_adress_two
        )
        content.contact_opening_mtof = content_data.get(
            "contact_opening_mtof", content.contact_opening_mtof
        )
        content.contact_opening_sat = content_data.get(
            "contact_opening_sat", content.contact_opening_sat
        )
        content.contact_opening_sun = content_data.get(
            "contact_opening_sun", content.contact_opening_sun
        )
        db.session.commit()
        return content_serializer.jsonify(content)

    except ValidationError as e:
        return {
            "errors": e.message,
            "message": "Something went wrong",
        }, HTTPStatus.BAD_REQUEST

    except Exception as e:
        return {"message": "Something went very wrong"}, HTTPStatus.BAD_REQUEST


@router.route("/content", methods=["GET"])
def get_content():
    content = db.session.query(ContentModel).all()
    print(content_serializer.jsonify(content, many=True))
    return content_serializer.jsonify(content, many=True)
