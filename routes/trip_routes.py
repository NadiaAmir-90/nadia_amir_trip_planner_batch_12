from flask import Blueprint, jsonify, request

from services.trip_service import (
    trip_to_dict,
    create_trip,
    get_all_trips,
    get_trip_by_id,
    update_trip,
    delete_trip,
)

from utils.validation import validate_trip_data

trip_bp = Blueprint("trips", __name__)


# create a trip
@trip_bp.route("/create_trip", methods=["POST"])
def create_trip_route():
    data = request.get_json()

    errors = validate_trip_data(data)
    if errors:
        return jsonify(
            {
                "message": "Data are not valid",
                "error": errors,
            }
        ), 400

    trip = create_trip(data)
    return jsonify(trip_to_dict(trip)), 201


# get all trips
@trip_bp.route("/all_trips", methods=["GET"])
def get_all_trips_route():
    trips = get_all_trips()
    return jsonify([trip_to_dict(trip) for trip in trips]), 200


# get one trip
@trip_bp.route("/get_trip/<int:trip_id>", methods=["GET"])
def get_one(trip_id):
    trip = get_trip_by_id(trip_id)

    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify(trip_to_dict(trip)), 200


# update the trip
@trip_bp.route("/update_trip/<int:trip_id>", methods=["PUT"])
def update(trip_id):
    trip = get_trip_by_id(trip_id)

    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json(silent=True)
    errors = validate_trip_data(data, allow_missing_attribute=True)

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    trip = update_trip(trip, data)
    return jsonify(trip_to_dict(trip)), 200


# delete trip
@trip_bp.route("/detele_trip/<int:trip_id>", methods=["DELETE"])
def delete(trip_id):
    trip = get_trip_by_id(trip_id)

    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    delete_trip(trip)
    return jsonify({"message": "Trip deleted successfully"}), 200