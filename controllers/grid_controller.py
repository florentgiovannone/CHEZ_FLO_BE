from http import HTTPStatus
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from application import db
from models.grid_model import GridModel
from serializers.grid_serializer import GridSerializer
from sqlalchemy.exc import SQLAlchemyError


grid_serializer = GridSerializer(session=db.session)
router = Blueprint("grid", __name__)


# --- Display Carousel section ---
@router.route("/content/<int:content_id>/grid", methods=["GET"])
def get_grid(content_id):
    grid = db.session.query(GridModel).filter_by(content_id=content_id).all()
    if not grid:
        return jsonify({"message": "No grid found"}), HTTPStatus.NOT_FOUND

    data = [
        {
            "id": c.id,
            "position": c.position,
            "grid_url": c.grid_url,
            "height": c.height,
            "width": c.width,
            "content_id": c.content_id,
        }
        for c in grid
    ]
    return jsonify(data), HTTPStatus.OK


# --- Delete Carousel section ---
@router.route("/content/<int:content_id>/grid/<int:grid_id>", methods=["DELETE"])
def delete_grid(content_id, grid_id):
    grid = GridModel.query.get(grid_id)
    if not grid:
        return jsonify({"message": "Grid not found"}, HTTPStatus.NOT_FOUND)

    grid.remove()
    return jsonify({"error": "Grid deleted"})


# --- Create Carousel section ---
@router.route("/content/<int:content_id>/grid", methods=["POST"])
def create_grid(content_id):
    try:
        grid_dictionary = request.json
        grid_dictionary["content_id"] = content_id
        grid_model = grid_serializer.load(grid_dictionary, session=db.session)
        db.session.add(grid_model)
        db.session.commit()
        return jsonify(grid_serializer.dump(grid_model)), HTTPStatus.CREATED

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
@router.route("/content/<int:content_id>/grid", methods=["PUT"])
def update_grid(content_id):
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
                        "error": "Expected an array of grids",
                        "received": type(data).__name__,
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        updated_grids = []
        for index, grid_data in enumerate(data):
            # Validate each grid object
            if not isinstance(grid_data, dict):
                return (
                    jsonify(
                        {
                            "message": "Invalid grid format",
                            "error": f"Grid at index {index} must be an object",
                            "received": type(grid_data).__name__,
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Validate required fields
            grid_id = grid_data.get("id")
            grid_url = grid_data.get("grid_url")

            if grid_id is None:
                return (
                    jsonify(
                        {
                            "message": "Missing required field",
                            "error": f"Grid at index {index} is missing 'id' field",
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            if grid_url is None:
                return (
                    jsonify(
                        {
                            "message": "Missing required field",
                            "error": f"Grid at index {index} is missing 'grid_url' field",
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Validate grid_id is an integer
            try:
                grid_id = int(grid_id)
            except (ValueError, TypeError):
                return (
                    jsonify(
                        {
                            "message": "Invalid grid ID",
                            "error": f"Grid ID at index {index} must be an integer",
                            "received": str(grid_id),
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Update carousel if it exists
            grid = GridModel.query.filter_by(id=grid_id, content_id=content_id).first()

            if grid:
                grid.grid_url = grid_url
                updated_grids.append(
                    {
                        "id": grid.id,
                        "grid_url": grid.grid_url,
                        "position": grid.position,
                        "height": grid.height,
                        "width": grid.width,
                    }
                )

        if not updated_grids:
            return (
                jsonify(
                    {
                        "message": "No grids were updated",
                        "error": "No matching grids found for the given IDs and content_id",
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Grids updated successfully",
                    "updated_grids": updated_grids,
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
@router.route("/content/<int:content_id>/grid/<int:grid_id>", methods=["PUT"])
def update_single_grid(content_id, grid_id):
    try:
        data = request.get_json()
        if not data or "grid_url" not in data:
            return (
                jsonify({"message": "Invalid data format. 'grid_url' is required"}),
                HTTPStatus.BAD_REQUEST,
            )

        grid = GridModel.query.filter_by(id=grid_id, content_id=content_id).first()

        if not grid:
            return (
                jsonify({"message": "Grid not found"}),
                HTTPStatus.NOT_FOUND,
            )

        grid.grid_url = data["grid_url"]
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Grid updated successfully",
                    "grid": {
                        "id": grid.id,
                        "grid_url": grid.grid_url,
                        "position": grid.position,
                        "height": grid.height,
                        "width": grid.width,
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
