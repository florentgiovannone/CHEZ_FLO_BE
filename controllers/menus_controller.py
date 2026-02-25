"""Menu controller for managing restaurant menu updates and scheduling."""

from http import HTTPStatus
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import MenusModel
from serializers.menus_serializer import MenusSerializer
from middleware.secure_route import role_required

menus_serializer = MenusSerializer()
router = Blueprint("menus", __name__)


# --- Display Menus section ---
@router.route("/content/<int:content_id>/menus", methods=["GET"])
def get_menus(content_id):
    """Get all menus for a specific content ID."""
    try:
        menus = db.session.query(MenusModel).filter_by(content_id=content_id).all()
        if not menus:
            return jsonify({"message": "No menus found"}), HTTPStatus.NOT_FOUND

        return jsonify(menus_serializer.dump(menus, many=True)), HTTPStatus.OK

    except ValidationError as _:
        return (
            jsonify({"message": "Something went wrong", "error": str(_)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Create Menus section ---
@router.route("/content/<int:content_id>/menus", methods=["POST"])
@role_required("admin", "superadmin")
def create_menus(content_id):
    """Create a new menu for a specific content ID."""
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

    except ValidationError as _:
        return (
            jsonify({"error": "Validation error", "details": _.messages}),
            HTTPStatus.BAD_REQUEST,
        )
    except SQLAlchemyError as _:
        db.session.rollback()
        return (
            jsonify({"error": "Database error", "details": str(_)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Update Single Menu section ---
@router.route("/content/<int:content_id>/menus/<string:menu_type>", methods=["PUT"])
def update_single_menu(content_id, menu_type):
    """Update a single menu for a specific content ID and menu type."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid data"}), HTTPStatus.BAD_REQUEST

        menu = MenusModel.query.filter_by(
            content_id=content_id, menus_type=menu_type
        ).first()
        if not menu:
            return jsonify({"message": "Menu not found"}), HTTPStatus.NOT_FOUND

        # Use UTC for consistent timezone handling
        now_utc = datetime.now(timezone.utc)
        scheduled_at = data.get("scheduled_at")

        # Case 1: Scheduled update
        if scheduled_at:
            try:
                # Handle incomplete time formats by adding seconds if missing
                if len(scheduled_at) == 16:  # "2025-07-24T16:04" format
                    scheduled_at += ":00"  # Make it "2025-07-24T16:04:00"

                # Parse the time as BST (keep it as BST, don't convert to UTC)
                parsed_time_bst = datetime.fromisoformat(scheduled_at)

                # For comparison, convert current UTC time to BST
                now_bst = now_utc.astimezone(
                    timezone(timedelta(hours=1))
                )  # Convert UTC to BST

                # Add some buffer time to avoid immediate execution due to processing delay
                buffer_seconds = 30
                min_future_time_bst = now_bst.replace(tzinfo=None) + timedelta(
                    seconds=buffer_seconds
                )

                # Check if scheduled time is sufficiently in the future (both in BST)
                if parsed_time_bst > min_future_time_bst:
                    menu.scheduled_text = data.get("menus_text")
                    menu.scheduled_url = data.get("menus_url")
                    # Store as naive BST datetime
                    menu.scheduled_at = parsed_time_bst
                    menu.applied = False
                    db.session.commit()
                    return (
                        jsonify(
                            {
                                "message": "Menu update scheduled",
                                "scheduled_for_bst": parsed_time_bst.isoformat(),
                                "current_time_bst": now_bst.replace(
                                    tzinfo=None
                                ).isoformat(),
                                "minimum_schedule_time_bst": min_future_time_bst.isoformat(),
                            }
                        ),
                        HTTPStatus.OK,
                    )
                else:
                    # Scheduled time is too close to now or in the past
                    return (
                        jsonify(
                            {
                                "message": "Scheduled time must be at least"
                                " 30 seconds in the future",
                                "scheduled_time_bst": parsed_time_bst.isoformat(),
                                "current_time_bst": now_bst.replace(
                                    tzinfo=None
                                ).isoformat(),
                                "minimum_schedule_time_bst": min_future_time_bst.isoformat(),
                            }
                        ),
                        HTTPStatus.BAD_REQUEST,
                    )

            except ValueError as _:
                return (
                    jsonify(
                        {
                            "message": "Invalid date format",
                            "error": str(_),
                            "received": scheduled_at,
                            "expected_format": "BST time like"
                            " 2025-07-24T17:30:00 or 2025-07-24T17:30",
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

    except ValidationError as _:
        db.session.rollback()
        return (
            jsonify({"message": "Error", "error": str(_)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Delete Menu section ---
@router.route("/content/<int:content_id>/menus/<string:menu_type>", methods=["DELETE"])
@role_required("admin", "superadmin")
def delete_menu(content_id, menu_type):
    """Delete a menu for a specific content ID and menu type."""
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

    except ValidationError as _:
        db.session.rollback()
        return (
            jsonify({"message": "Something went wrong", "error": str(_)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Check Scheduled Updates ---
@router.route("/content/<int:content_id>/menus/scheduled", methods=["GET"])
def get_scheduled_updates(content_id):
    """Check pending scheduled updates for debugging purposes"""
    try:
        now_utc = datetime.now(timezone.utc)
        now_bst = now_utc.astimezone(timezone(timedelta(hours=1)))  # Convert UTC to BST
        now_bst_naive = now_bst.replace(tzinfo=None)  # Remove timezone for comparison

        # Get all scheduled updates for this content
        scheduled_menus = MenusModel.query.filter(
            MenusModel.content_id == content_id,
            MenusModel.scheduled_at.isnot(None),
            MenusModel.applied.is_(False),
        ).all()

        scheduled_updates = []
        for menu in scheduled_menus:
            # Database stores naive BST datetime
            scheduled_bst = menu.scheduled_at

            scheduled_updates.append(
                {
                    "id": menu.id,
                    "menus_type": menu.menus_type,
                    "current_text": menu.menus_text,
                    "current_url": menu.menus_url,
                    "scheduled_text": menu.scheduled_text,
                    "scheduled_url": menu.scheduled_url,
                    "scheduled_at_bst": scheduled_bst.isoformat(),
                    "is_due": scheduled_bst <= now_bst_naive,
                    "applied": menu.applied,
                    "minutes_until_due": (
                        int((scheduled_bst - now_bst_naive).total_seconds() / 60)
                        if scheduled_bst > now_bst_naive
                        else 0
                    ),
                }
            )

        return (
            jsonify(
                {
                    "message": f"Found {len(scheduled_updates)} scheduled updates",
                    "current_time_bst": now_bst_naive.isoformat(),
                    "current_time_utc": now_utc.isoformat(),
                    "scheduled_updates": scheduled_updates,
                }
            ),
            HTTPStatus.OK,
        )

    except ValidationError as _:
        return (
            jsonify({"message": "Error checking scheduled updates", "error": str(_)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Manual trigger for scheduled updates (for testing) ---
@router.route("/content/<int:content_id>/menus/apply-scheduled", methods=["POST"])
def apply_scheduled_updates_manually(content_id):
    """Manually trigger the application of scheduled updates for testing"""
    try:
        now_utc = datetime.now(timezone.utc)
        now_bst = now_utc.astimezone(timezone(timedelta(hours=1)))  # Convert UTC to BST
        now_bst_naive = now_bst.replace(tzinfo=None)  # Remove timezone for comparison

        # Find scheduled updates that are due for this content (using BST)
        scheduled_menus = MenusModel.query.filter(
            MenusModel.content_id == content_id,
            MenusModel.scheduled_at <= now_bst_naive,  # Database stores naive BST
            MenusModel.applied.is_(False),
            MenusModel.scheduled_at.isnot(None),
        ).all()

        if not scheduled_menus:
            return (
                jsonify(
                    {
                        "message": "No scheduled updates due for this content",
                        "current_time_bst": now_bst_naive.isoformat(),
                        "current_time_utc": now_utc.isoformat(),
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

    except ValidationError as _:
        db.session.rollback()
        return (
            jsonify({"message": "Error applying scheduled updates", "error": str(_)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
