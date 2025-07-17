from http import HTTPStatus
from flask import Blueprint, request, jsonify
from marshmallow.exceptions import ValidationError
from app import db
from models import ContentModel, MenusModel
from serializers.menus_serializer import MenusSerializer
from sqlalchemy.exc import SQLAlchemyError

menus_serializer = MenusSerializer()
router = Blueprint("menus", __name__)


# --- Display Menus section ---
@router.route("/content/<int:content_id>/menus", methods=["GET"])
def get_menus(content_id):
    try:
        menus = db.session.query(MenusModel).filter_by(content_id=content_id).all()
        if not menus:
            return jsonify({"message": "No menus found"}), HTTPStatus.NOT_FOUND

        return jsonify(menus_serializer.dump(menus, many=True)), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify({"message": "Something went wrong", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Create Menus section ---
@router.route("/content/<int:content_id>/menus", methods=["POST"])
def create_menus(content_id):
    try:
        menus_dictionary = request.json
        menus_dictionary["content_id"] = content_id
        # Ensure menus_type is lowercase of menus_text
        if "menus_text" in menus_dictionary:
            menus_dictionary["menus_type"] = menus_dictionary["menus_text"].lower()

        menus_model = menus_serializer.load(menus_dictionary, session=db.session)
        db.session.add(menus_model)
        db.session.commit()
        return jsonify(menus_serializer.dump(menus_model)), HTTPStatus.CREATED

    except ValidationError as e:
        return (
            jsonify({"error": "Validation error", "details": e.messages}),
            HTTPStatus.BAD_REQUEST,
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return (
            jsonify({"error": "Database error", "details": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Update Single Menu section ---
@router.route("/content/<int:content_id>/menus/<string:menu_type>", methods=["PUT"])
def update_single_menu(content_id, menu_type):
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"message": "Invalid data format. Request body is required"}),
                HTTPStatus.BAD_REQUEST,
            )

        menu = MenusModel.query.filter_by(
            content_id=content_id, menus_type=menu_type
        ).first()
        if not menu:
            return (
                jsonify({"message": "Menu not found"}),
                HTTPStatus.NOT_FOUND,
            )

        if "menus_text" in data:
            menu.menus_text = data["menus_text"]
            menu.menus_type = data["menus_text"].lower()
        if "menus_url" in data:
            menu.menus_url = data["menus_url"]

        db.session.commit()
        return jsonify(menus_serializer.dump(menu)), HTTPStatus.OK

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "Something went wrong", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Delete Menu section ---
@router.route("/content/<int:content_id>/menus/<string:menu_type>", methods=["DELETE"])
def delete_menu(content_id, menu_type):
    try:
        menu = MenusModel.query.filter_by(
            content_id=content_id, menus_type=menu_type
        ).first()
        if not menu:
            return jsonify({"message": "Menu not found"}), HTTPStatus.NOT_FOUND

        menu.remove()
        return (
            jsonify(
                {"message": f"{menu.menus_text.capitalize()} menu deleted successfully"}
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "Something went wrong", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    
    
