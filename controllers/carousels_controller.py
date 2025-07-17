from http import HTTPStatus
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app import db
from models import CarouselModel
from serializers.carousel_serializer import CarouselSerializer
from sqlalchemy.exc import SQLAlchemyError


carousels_serializer = CarouselSerializer(session=db.session)
router = Blueprint("carousels", __name__)


# --- Display Carousel section ---
@router.route("/content/<int:content_id>/carousel", methods=["GET"])
def get_carousels(content_id):
    carousels = db.session.query(CarouselModel).filter_by(content_id=content_id).all()
    if not carousels:
        return jsonify({"message": "No carousels found"}), HTTPStatus.NOT_FOUND

    data = [
        {
            "id": c.id,
            "carousel_url": c.carousel_url,
            "content_id": c.content_id,
        }
        for c in carousels
    ]
    return jsonify(data), HTTPStatus.OK


# --- Delete Carousel section ---
@router.route(
    "/content/<int:content_id>/carousel/<int:carousel_id>", methods=["DELETE"]
)
def delete_carousel(content_id, carousel_id):
    carousel = CarouselModel.query.get(carousel_id)
    if not carousel:
        return jsonify({"message": "Carousel not found"}, HTTPStatus.NOT_FOUND)

    carousel.remove()
    return jsonify({"error": "Carousel deleted"})


# --- Create Carousel section ---
@router.route("/content/<int:content_id>/carousel", methods=["POST"])
def create_carousel(content_id):
    try:
        carousel_dictionary = request.json
        carousel_dictionary["content_id"] = content_id
        carousel_model = carousels_serializer.load(
            carousel_dictionary, session=db.session
        )
        db.session.add(carousel_model)
        db.session.commit()
        return jsonify(carousels_serializer.dump(carousel_model)), HTTPStatus.CREATED

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


# --- Update Carousel section ---
@router.route("/content/<int:content_id>/carousel", methods=["PUT"])
def update_carousel(content_id):
    try:
        # Check if request is JSON
        if not request.is_json:
            return (
                jsonify(
                    {
                        "message": "Invalid request format",
                        "error": "Request must be JSON and Content-Type must be application/json",
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        # Get and validate JSON data
        try:
            data = request.get_json()
        except Exception as e:
            return (
                jsonify({"message": "Invalid JSON format", "error": str(e)}),
                HTTPStatus.BAD_REQUEST,
            )

        # Validate data is a list
        if not isinstance(data, list):
            return (
                jsonify(
                    {
                        "message": "Invalid data format",
                        "error": "Expected an array of carousels",
                        "received": type(data).__name__,
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        updated_carousels = []
        for index, carousel_data in enumerate(data):
            # Validate each carousel object
            if not isinstance(carousel_data, dict):
                return (
                    jsonify(
                        {
                            "message": "Invalid carousel format",
                            "error": f"Carousel at index {index} must be an object",
                            "received": type(carousel_data).__name__,
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Validate required fields
            carousel_id = carousel_data.get("id")
            carousel_url = carousel_data.get("carousel_url")

            if carousel_id is None:
                return (
                    jsonify(
                        {
                            "message": "Missing required field",
                            "error": f"Carousel at index {index} is missing 'id' field",
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            if carousel_url is None:
                return (
                    jsonify(
                        {
                            "message": "Missing required field",
                            "error": f"Carousel at index {index} is missing 'carousel_url' field",
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Validate carousel_id is an integer
            try:
                carousel_id = int(carousel_id)
            except (ValueError, TypeError):
                return (
                    jsonify(
                        {
                            "message": "Invalid carousel ID",
                            "error": f"Carousel ID at index {index} must be an integer",
                            "received": str(carousel_id),
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Update carousel if it exists
            carousel = CarouselModel.query.filter_by(
                id=carousel_id, content_id=content_id
            ).first()

            if carousel:
                carousel.carousel_url = carousel_url
                updated_carousels.append(
                    {"id": carousel.id, "carousel_url": carousel.carousel_url}
                )

        if not updated_carousels:
            return (
                jsonify(
                    {
                        "message": "No carousels were updated",
                        "error": "No matching carousels found for the given IDs and content_id",
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Carousels updated successfully",
                    "updated_carousels": updated_carousels,
                }
            ),
            HTTPStatus.OK,
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return (
            jsonify({"message": "Database error", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return (
            jsonify({"message": "Something went wrong", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


# --- Update Single Carousel section ---
@router.route("/content/<int:content_id>/carousel/<int:carousel_id>", methods=["PUT"])
def update_single_carousel(content_id, carousel_id):
    try:
        data = request.get_json()
        if not data or "carousel_url" not in data:
            return (
                jsonify({"message": "Invalid data format. 'carousel_url' is required"}),
                HTTPStatus.BAD_REQUEST,
            )

        carousel = CarouselModel.query.filter_by(
            id=carousel_id, content_id=content_id
        ).first()

        if not carousel:
            return (
                jsonify({"message": "Carousel not found"}),
                HTTPStatus.NOT_FOUND,
            )

        carousel.carousel_url = data["carousel_url"]
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Carousel updated successfully",
                    "carousel": {
                        "id": carousel.id,
                        "carousel_url": carousel.carousel_url,
                    },
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "Something went wrong", "error": str(e)}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
