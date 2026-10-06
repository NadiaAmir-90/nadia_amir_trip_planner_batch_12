from datetime import datetime

from database.db import db
from models.trip import Trip


def trip_to_dict(trip):
    return {
        "id": trip.id,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "budget": trip.budget,
        "max_travelers": trip.max_travelers,
        "status": trip.status,
        "created_at": trip.created_at.isoformat(),
        "updated_at": trip.updated_at.isoformat(),
    }


def create_trip(data):
    trip = Trip(
        destination=data["destination"].strip(),
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
        end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
        budget=data["budget"],
        max_travelers=data["max_travelers"],
        status=data.get("status", "PLANNED").upper(),
    )
    db.session.add(trip)
    db.session.commit()
    return trip


def get_all_trips():
    return Trip.query.order_by(Trip.id).all()


def get_trip_by_id(trip_id):
    return db.session.get(Trip, trip_id)


def update_trip(trip, data):
    if "destination" in data:
        trip.destination = data["destination"].strip()
    if "start_date" in data:
        trip.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if "end_date" in data:
        trip.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    if "budget" in data:
        trip.budget = data["budget"]
    if "max_travelers" in data:
        trip.max_travelers = data["max_travelers"]
    if "status" in data:
        trip.status = data["status"].upper()

    db.session.commit()
    return trip


def delete_trip(trip):
    db.session.delete(trip)
    db.session.commit()