from flask import Blueprint, jsonify, request

from services.trip_service import (
    #day-1 route 
    trip_to_dict,
    create_trip,
    get_all_trips,
    get_trip_by_id,
    update_trip,
    delete_trip,


    #day -2 route
    add_traveler_to_trip,
    find_overlapping_trip,
    remove_traveler_from_trip,
    add_expense_to_trip,
    get_summary_trip
)

from utils.validation import (
    validate_trip_data,
    validate_traveler_data,
    validate_expense_data,
    )

trip_bp = Blueprint("trips", __name__)


# create a trip
@trip_bp.route("/create_trip", methods=["POST"])
def create_trip_route():
    data = request.get_json()

    errors = validate_trip_data(data)
    if errors:
        return jsonify(
            {
                "error": errors,
                "message": "Data are not valid",
                
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

    if not trip:
        return jsonify(
            {
                "error": "Trip not found",
                "message":"trip is not created yet"
            }
            ), 404

    return jsonify(trip_to_dict(trip)), 200


# update the trip
@trip_bp.route("/update_trip/<int:trip_id>", methods=["PUT"])
def update(trip_id):
    trip = get_trip_by_id(trip_id)

    if trip is None:
        return jsonify(
            {
                "error": "Trip not found",
                "message": "Trip not to be updated if it does not exist"

            }
            ), 404

    data = request.get_json(silent=True)
    errors = validate_trip_data(data, allow_missing_attribute=True)

    if errors:
        return jsonify(
            {
                "error": "Validation failed", 
                "message": errors
            }
            ), 400

    trip = update_trip(trip, data)
    return jsonify(trip_to_dict(trip)), 200


# delete trip
@trip_bp.route("/detele_trip/<int:trip_id>", methods=["DELETE"])
def delete(trip_id):
    trip = get_trip_by_id(trip_id)

    if trip is None:
        return jsonify(
            {
                "error": "Trip not found",
                "message":"Trip cannot be deleted if it does not exits"
            }
            ), 404

    delete_trip(trip)
    return jsonify(
        {
            "message": "Trip deleted successfully"
        }
        ), 200


#add_traveler_to_trip:
@trip_bp.route("/add_traveler/trip/<int:trip_id>",methods=["POST"])
def add_traveler(trip_id):
     
    data=request.get_json()

    error=validate_traveler_data(data)
    if error:
        return jsonify({
            "error":"Data are not valid ",
            "message":"Traveler_data has wrong information"
        }),400
    
    results,status_code=add_traveler_to_trip(trip_id,data)

    if status_code>=400:
        return jsonify(
            {
                "error":"Traveler are not added",
                "message":results
            }
            ),status_code
    
    return jsonify(results),status_code



# remove traveler from trip 
@trip_bp.route("/delete_trip/<int:trip_id>/for_traveler/<int:traveler_id>",methods=["DELETE"])
def remove_traveler(trip_id,traveler_id):
    results,status_code=remove_traveler_from_trip(trip_id,traveler_id)

    if status_code>=400:
        return jsonify(
            {
              "error":"Traveler are not removed",
              "message":results
        }),status_code
    return jsonify(results),status_code


#expense_at_trip
@trip_bp.route("/expense_at_trip/<int:trip_id>",methods=["POST"])
def add_expense(trip_id):
    data=request.get_json()

    error=validate_expense_data(data)
    if error:
        return jsonify(
            {
                "error":error,
                "message":"Expense data are not valid"
            }
        ),400
    
    results,status_code=add_expense_to_trip(trip_id,data)

    if status_code>=400:
        return jsonify(
            {
                "error":"invalid expense",
                "message":results
            }
            ),status_code
    
    return jsonify(results),status_code


#summary_of_trip
@trip_bp.route("/summary_of_trip/<int:trip_id>",methods=["GET"])
def summary_of_trip(trip_id):
    results,status_code=get_summary_trip(trip_id)

    if status_code>=400:
        return jsonify(
              {
                "error":"Trip is not found",
                "message":results
              }
            ),status_code
    return jsonify(results),status_code
