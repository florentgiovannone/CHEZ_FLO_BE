from http import HTTPStatus
from flask import Blueprint, request, jsonify
from marshmallow.exceptions import ValidationError
from app import db
from models import ContentModel, MenusModel
from serializers.menus_serializer import MenusSerializer
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

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
            return jsonify({"message": "Invalid data"}), HTTPStatus.BAD_REQUEST

        menu = MenusModel.query.filter_by(
            content_id=content_id, menus_type=menu_type
        ).first()
        if not menu:
            return jsonify({"message": "Menu not found"}), HTTPStatus.NOT_FOUND

        now = datetime.now()
        scheduled_at = data.get("scheduled_at")

        # Case 1: Scheduled update
        if scheduled_at:
            try:
                # Handle incomplete time formats by adding seconds if missing
                if len(scheduled_at) == 16:  # "2025-07-24T16:04" format
                    scheduled_at += ":00"  # Make it "2025-07-24T16:04:00"

                parsed_time = datetime.fromisoformat(scheduled_at)

                # Add some buffer time to avoid immediate execution due to processing delay
                buffer_seconds = 30
                min_future_time = now.replace(second=0, microsecond=0) + timedelta(
                    seconds=buffer_seconds
                )

                # Check if scheduled time is sufficiently in the future
                if parsed_time > min_future_time:
                    menu.scheduled_text = data.get("menus_text")
                    menu.scheduled_url = data.get("menus_url")
                    menu.scheduled_at = parsed_time
                    menu.applied = False
                    db.session.commit()
                    return (
                        jsonify(
                            {
                                "message": "Menu update scheduled",
                                "scheduled_for": parsed_time.isoformat(),
                                "current_time": now.isoformat(),
                                "minimum_schedule_time": min_future_time.isoformat(),
                            }
                        ),
                        HTTPStatus.OK,
                    )
                else:
                    # Scheduled time is too close to now or in the past
                    return (
                        jsonify(
                            {
                                "message": "Scheduled time must be at least 30 seconds in the future",
                                "scheduled_time": parsed_time.isoformat(),
                                "current_time": now.isoformat(),
                                "minimum_schedule_time": min_future_time.isoformat(),
                            }
                        ),
                        HTTPStatus.BAD_REQUEST,
                    )

            except ValueError as e:
                return (
                    jsonify(
                        {
                            "message": "Invalid date format",
                            "error": str(e),
                            "received": scheduled_at,
                            "expected_format": "ISO format like 2025-07-24T17:30:00 or 2025-07-24T17:30",
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

        # Case 2: Immediate update (only if no scheduled_at provided)
        if "menus_text" in data:
            menu.menus_text = data["menus_text"]
        if "menus_url" in data:
            menu.menus_url = data["menus_url"]

        # Clear any old scheduled data
        menu.scheduled_text = None
        menu.scheduled_url = None
        menu.scheduled_at = None
        menu.applied = True

        db.session.commit()
        return jsonify({"message": "Menu updated immediately"}), HTTPStatus.OK

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "Error", "error": str(e)}),
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


# --- Check Scheduled Updates ---
@router.route("/content/<int:content_id>/menus/scheduled", methods=["GET"])
def get_scheduled_updates(content_id):
    """Check pending scheduled updates for debugging purposes"""
    try:
        now = datetime.now()

        # Get all scheduled updates for this content
        scheduled_menus = MenusModel.query.filter(
            MenusModel.content_id == content_id,
            MenusModel.scheduled_at.isnot(None),
            MenusModel.applied == False,
        ).all()

        scheduled_updates = []
        for menu in scheduled_menus:
            scheduled_updates.append(
                {
                    "id": menu.id,
                    "menus_type": menu.menus_type,
                    "current_text": menu.menus_text,
                    "current_url": menu.menus_url,
                    "scheduled_text": menu.scheduled_text,
                    "scheduled_url": menu.scheduled_url,
                    "scheduled_at": (
                        menu.scheduled_at.isoformat() if menu.scheduled_at else None
                    ),
                    "is_due": menu.scheduled_at <= now if menu.scheduled_at else False,
                    "applied": menu.applied,
                }
            )

        return (
            jsonify(
                {
                    "message": f"Found {len(scheduled_updates)} scheduled updates",
                    "current_time": now.isoformat(),
                    "scheduled_updates": scheduled_updates,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return (
            jsonify({"message": "Error checking scheduled updates", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Manual trigger for scheduled updates (for testing) ---
@router.route("/content/<int:content_id>/menus/apply-scheduled", methods=["POST"])
def apply_scheduled_updates_manually(content_id):
    """Manually trigger the application of scheduled updates for testing"""
    try:
        now = datetime.now()

        # Find scheduled updates that are due for this content
        scheduled_menus = MenusModel.query.filter(
            MenusModel.content_id == content_id,
            MenusModel.scheduled_at <= now,
            MenusModel.applied == False,
            MenusModel.scheduled_at.isnot(None),
        ).all()

        if not scheduled_menus:
            return (
                jsonify(
                    {
                        "message": "No scheduled updates due for this content",
                        "current_time": now.isoformat(),
                    }
                ),
                HTTPStatus.OK,
            )

        applied_updates = []

        for menu in scheduled_menus:
            # Apply the scheduled changes
            if menu.scheduled_text:
                menu.menus_text = menu.scheduled_text
            if menu.scheduled_url:
                menu.menus_url = menu.scheduled_url

            applied_updates.append(
                {
                    "id": menu.id,
                    "menus_type": menu.menus_type,
                    "new_text": menu.menus_text,
                    "new_url": menu.menus_url,
                }
            )

            # Clear scheduled fields and mark as applied
            menu.scheduled_text = None
            menu.scheduled_url = None
            menu.scheduled_at = None
            menu.applied = True

        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Successfully applied {len(applied_updates)} scheduled updates",
                    "applied_updates": applied_updates,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "Error applying scheduled updates", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
