from http import HTTPStatus
from flask import Blueprint, request, jsonify
from marshmallow.exceptions import ValidationError
from app import db
from models import ContentModel
from serializers.content_serializer import ContentSerializer
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError

content_serializer = ContentSerializer()
router = Blueprint("content", __name__)


# --- Display Content section ---
@router.route("/content", methods=["GET"])
def get_content():
    content = ContentModel.query.all()  # Fetch all content
    serialized_content = ContentSerializer().dump(
        content, many=True
    )  # Correct place for 'many=True'
    return jsonify(serialized_content)  # Return the serialized data


# --- Update Content section ---
@router.route("/content/<int:content_id>", methods=["PUT"])
def update_content(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        data = request.json

        # Update all standard fields
        fields = [
            "about_title",
            "about_text",
            "breakfast_menus_text",
            "breakfast_menus_file",
            "lunch_menus_text",
            "lunch_menus_file",
            "dessert_menus_text",
            "dessert_menus_file",
            "winelist_menus_text",
            "winelist_menus_file",
            "cocktail_menus_text",
            "cocktail_menus_file",
            "image_one",
            "image_two",
            "image_three",
            "image_four",
            "image_five",
            "image_six",
            "reservation_title",
            "reservation_text",
            "breakfast_timing_day_one",
            "breakfast_timing_hours_one",
            "breakfast_timing_day_two",
            "breakfast_timing_hours_two",
            "lunch_timing_day_one",
            "lunch_timing_hours_one",
            "lunch_timing_day_two",
            "lunch_timing_hours_two",
            "dinner_timing_day_one",
            "dinner_timing_hours_one",
            "dinner_timing_day_two",
            "dinner_timing_hours_two",
            "reservation_line_one",
            "reservation_line_two",
            "phone",
            "email",
            "contact_title",
            "contact_adress_one",
            "contact_adress_two",
            "contact_opening_day_one",
            "contact_opening_hours_one",
            "contact_opening_day_two",
            "contact_opening_hours_two",
            "contact_opening_day_three",
            "contact_opening_hours_three",
            "map",
        ]

        for field in fields:
            if field in data:
                setattr(content, field, data[field])

        # --- Carousels update ---
        incoming_carousels = data.get("carousels", [])
        for incoming in incoming_carousels:
            carousel_id = incoming.get("id")
            if not carousel_id:
                continue
            for carousel in content.carousels:
                if carousel.id == carousel_id:
                    carousel.image = incoming.get("image", carousel.image)
                    carousel.caption = incoming.get(
                        "caption", getattr(carousel, "caption", "")
                    )
                    break

        db.session.commit()
        return content_serializer.jsonify(content)

    except Exception as e:
        print("Error updating content:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Display About section ---
@router.route("/content/<int:content_id>/about", methods=["GET"])
def get_about_section(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        about_data = {
            "about_title": content.about_title,
            "about_text": content.about_text,
        }

        return jsonify(about_data), HTTPStatus.OK

    except Exception as e:
        print("Error fetching about section:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Update About section ---
@router.route("/content/<int:content_id>/about", methods=["PUT"])
def update_about(content_id):

    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        data = request.json

        # Only update the about section
        if "about_title" in data:
            content.about_title = data["about_title"]

        if "about_text" in data:
            content.about_text = data["about_text"]

        db.session.commit()
        return content_serializer.jsonify(content)

    except Exception as e:
        print("Error updating about section:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Display Reservation section ---
@router.route("/content/<int:content_id>/reservation", methods=["GET"])
def get_reservation_section(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        reservation_data = {
            "reservation_title": content.reservation_title,
            "reservation_text": content.reservation_text,
            "reservation_line_one": content.reservation_line_one,
            "reservation_line_two": content.reservation_line_two,
            "breakfast_timing_day_one": content.breakfast_timing_day_one,
            "breakfast_timing_hours_one": content.breakfast_timing_hours_one,
            "breakfast_timing_day_two": content.breakfast_timing_day_two,
            "breakfast_timing_hours_two": content.breakfast_timing_hours_two,
            "lunch_timing_day_one": content.lunch_timing_day_one,
            "lunch_timing_hours_one": content.lunch_timing_hours_one,
            "lunch_timing_day_two": content.lunch_timing_day_two,
            "lunch_timing_hours_two": content.lunch_timing_hours_two,
            "dinner_timing_day_one": content.dinner_timing_day_one,
            "dinner_timing_hours_one": content.dinner_timing_hours_one,
            "dinner_timing_day_two": content.dinner_timing_day_two,
            "dinner_timing_hours_two": content.dinner_timing_hours_two,
            "phone": content.phone,
            "email": content.email,
        }

        return jsonify(reservation_data), HTTPStatus.OK

    except Exception as e:
        print("Error fetching reservation section:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Update Reservation section ---
@router.route("/content/<int:content_id>/reservation", methods=["PUT"])
def update_reservation(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        data = request.json

        # Only update the reservation section
        if "reservation_title" in data:
            content.reservation_title = data["reservation_title"]

        if "reservation_text" in data:
            content.reservation_text = data["reservation_text"]

        if "reservation_line_one" in data:
            content.reservation_line_one = data["reservation_line_one"]

        if "reservation_line_two" in data:
            content.reservation_line_two = data["reservation_line_two"]

        if "phone" in data:
            content.phone = data["phone"]

        if "email" in data:
            content.email = data["email"]

        if "breakfast_timing_day_one" in data:
            content.breakfast_timing_day_one = data["breakfast_timing_day_one"]

        if "breakfast_timing_hours_one" in data:
            content.breakfast_timing_hours_one = data["breakfast_timing_hours_one"]

        if "breakfast_timing_day_two" in data:
            content.breakfast_timing_day_two = data["breakfast_timing_day_two"]

        if "breakfast_timing_hours_two" in data:
            content.breakfast_timing_hours_two = data["breakfast_timing_hours_two"]

        if "lunch_timing_day_one" in data:
            content.lunch_timing_day_one = data["lunch_timing_day_one"]

        if "lunch_timing_hours_one" in data:
            content.lunch_timing_hours_one = data["lunch_timing_hours_one"]

        if "lunch_timing_day_two" in data:
            content.lunch_timing_day_two = data["lunch_timing_day_two"]

        if "lunch_timing_hours_two" in data:
            content.lunch_timing_hours_two = data["lunch_timing_hours_two"]
            
        if "dinner_timing_day_one" in data:
            content.dinner_timing_day_one = data["dinner_timing_day_one"]

        if "dinner_timing_hours_one" in data:
            content.dinner_timing_hours_one = data["dinner_timing_hours_one"]

        if "dinner_timing_day_two" in data:
            content.dinner_timing_day_two = data["dinner_timing_day_two"]

        if "dinner_timing_hours_two" in data:
            content.dinner_timing_hours_two = data["dinner_timing_hours_two"]

        if "phone" in data:
            content.phone = data["phone"]

        if "email" in data:
            content.email = data["email"]
            

        db.session.commit()
        return content_serializer.jsonify(content)

    except Exception as e:
        print("Error updating reservation section:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Display Contact section ---
@router.route("/content/<int:content_id>/contact", methods=["GET"])
def get_contact_section(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        contact_data = {
            "contact_title": content.contact_title,
            "phone": content.phone,
            "email": content.email,
            "contact_adress_one": content.contact_adress_one,
            "contact_adress_two": content.contact_adress_two,
            "contact_opening_day_one": content.contact_opening_day_one,
            "contact_opening_hours_one": content.contact_opening_hours_one,
            "contact_opening_day_two": content.contact_opening_day_two,
            "contact_opening_hours_two": content.contact_opening_hours_two,
            "contact_opening_day_three": content.contact_opening_day_three,
            "contact_opening_hours_three": content.contact_opening_hours_three,
            "map": content.map,
        }

        return jsonify(contact_data), HTTPStatus.OK

    except Exception as e:
        print("Error fetching contact section:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Update Contact section ---
@router.route("/content/<int:content_id>/contact", methods=["PUT"])
def update_contact(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        data = request.json

        # Only update the contact section
        if "contact_title" in data:
            content.contact_title = data["contact_title"]

        if "contact_adress_one" in data:
            content.contact_adress_one = data["contact_adress_one"]

        if "contact_adress_two" in data:
            content.contact_adress_two = data["contact_adress_two"]

        if "phone" in data:
            content.phone = data["phone"]

        if "email" in data:
            content.email = data["email"]

        if "contact_opening_day_one" in data:
            content.contact_opening_day_one = data["contact_opening_day_one"]

        if "contact_opening_hours_one" in data:
            content.contact_opening_hours_one = data["contact_opening_hours_one"]

        if "contact_opening_day_two" in data:
            content.contact_opening_day_two = data["contact_opening_day_two"]

        if "contact_opening_hours_two" in data:
            content.contact_opening_hours_two = data["contact_opening_hours_two"]

        if "contact_opening_day_three" in data:
            content.contact_opening_day_three = data["contact_opening_day_three"]

        if "contact_opening_hours_three" in data:
            content.contact_opening_hours_three = data["contact_opening_hours_three"]

        if "map" in data:
            content.map = data["map"]

        db.session.commit()
        return content_serializer.jsonify(content)

    except Exception as e:
        print("Error updating contact section:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Display Opening Hours section ---
@router.route("/content/<int:content_id>/opening_hours", methods=["GET"])
def get_opening_hours(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        opening_hours_data = {
            "breakfast_timing_day_one": content.breakfast_timing_day_one,
            "breakfast_timing_hours_one": content.breakfast_timing_hours_one,
            "breakfast_timing_day_two": content.breakfast_timing_day_two,
            "breakfast_timing_hours_two": content.breakfast_timing_hours_two,
        }

        return jsonify(opening_hours_data), HTTPStatus.OK

    except Exception as e:
        print("Error fetching opening hours:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


# --- Update Opening Hours section ---
@router.route("/content/<int:content_id>/opening_hours", methods=["PUT"])
def update_opening_hours(content_id):
    try:
        content = db.session.query(ContentModel).get(content_id)
        if content is None:
            return jsonify({"message": "Content not found"}), HTTPStatus.NOT_FOUND

        data = request.json

        # Only update the opening hours section
        if "breakfast_timing_day_one" in data:
            content.breakfast_timing_day_one = data["breakfast_timing_day_one"]

        if "breakfast_timing_hours_one" in data:
            content.breakfast_timing_hours_one = data["breakfast_timing_hours_one"]

        if "breakfast_timing_day_two" in data:
            content.breakfast_timing_day_two = data["breakfast_timing_day_two"]

        if "breakfast_timing_hours_two" in data:
            content.breakfast_timing_hours_two = data["breakfast_timing_hours_two"]

        db.session.commit()
        return content_serializer.jsonify(content)

    except Exception as e:
        print("Error updating opening hours:", str(e))
        return jsonify({"message": "Something went very wrong"}), HTTPStatus.BAD_REQUEST


@router.route("/content/<int:content_id>/update_grid", methods=["PUT"])
def update_grid(content_id):
    try:
        # Get the content by ID
        content = db.session.query(ContentModel).get(content_id)
        if not content:
            return jsonify({"error": "Content not found"}), 404

        # Get the request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # List of valid image fields
        image_fields = [
            "image_one",
            "image_two",
            "image_three",
            "image_four",
            "image_five",
            "image_six",
        ]

        # Update only the fields that are provided in the request
        updated = False
        for field in image_fields:
            if field in data and data[field] is not None:
                setattr(content, field, data[field])
                updated = True

        if not updated:
            return jsonify({"error": "No valid fields to update"}), 400

        # Save changes to database
        try:
            db.session.commit()
            return (
                jsonify(
                    {
                        "message": "Grid updated successfully",
                        "content": content_serializer.dump(content),
                    }
                ),
                200,
            )
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error: {str(db_error)}")
            return jsonify({"error": "Database update failed"}), 500

    except Exception as e:
        print(f"Error updating grid: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
