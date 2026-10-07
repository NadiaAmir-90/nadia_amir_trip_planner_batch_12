from datetime import datetime

from database.db import db
from models.trip import (
    Trip,
    Traveler,
    TripTraveler,
    Expense
)

# Business logic for the trips table
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


#business logic for the travelers table :

def add_traveler_to_trip(trip_id,data):
    
    #find trip 
    trip=db.session.get(Trip,trip_id)
    if not trip :
        return (
            {
                "error":"Trip not found",
                "message":"A Non-existing Trip cannot be added a Traveler  "
            }
        ),404
    
    if trip.status!= "PLANNED":
        return {
                "error":"Traveler not allowed",
                "message":"Traveler only added the PLANNED trip"
            },409
    
    #validate the trraveler  data
    name=data["name"].strip()
    email=data["email"].strip().lower()

    # find the existing traveler by email :
    traveler=Traveler.query.filter_by(
        email=email
    ).first()

    if not traveler :
        traveler=Traveler(
            name=name,
            email=email
        )
    db.session.add(traveler)
    db.session.flush() # pushes all database changes from python memory to the actua database

    # check one traveler join a trip twice ?

    existing_registration=TripTraveler.query.filter_by(
        trip_id=trip_id,
        traveler_id=traveler.id
    ).first()

    if existing_registration:
        return {
            "error":"Traveler already registered",
            "message":"Traveler cannot be added twice in a signle trip"
        },409
    
    #check capacity of trip:

    traveler_count=TripTraveler.query.filter_by(
        trip_id=trip_id
    ).count()

    if traveler_count >=trip.max_travelers:
        return{
                "error":"Exceed max_travelers",
                "message":"Trip has reached the maximum capacity of travelers"
            },409
    

    #check the overlapping the trip :
    overlapping_trip=find_overlapping_trip(traveler.id,trip)

    if overlapping_trip:
        return {
                "error":"Trip overlap",
                "message":"Traveler have another trip in the same date"
            },409
    
    registraton=TripTraveler(
        trip_id=trip_id,
        traveler_id=traveler.id
    )
    db.session.add(registraton)
    db.session.commit()

    return {
        "trip_id": trip.id,
        "traveler_id": traveler.id,
        "name": traveler.name,
        "email": traveler.email
    }, 201



#overlapping trip
def find_overlapping_trip(traveler_id, new_trip):

    registrations = TripTraveler.query.filter_by(
        traveler_id=traveler_id
    ).all()

    for registration in registrations:

        existing_trip = db.session.get(
            Trip,
            registration.trip_id
        )

        if existing_trip is None:
            continue

        # Overlap condition
        if (
            new_trip.start_date < existing_trip.end_date
            and
            new_trip.end_date > existing_trip.start_date
        ):
            return existing_trip

    return None




def remove_traveler_from_trip(trip_id,traveler_id):

    trip=db.session.get(Trip,trip_id)

    if not trip:
        return {
            "error":"Trip not found",
            "message":"Traveler does not removed from non-existin trip"
        },404
    
    registration=TripTraveler.query.filter_by(
        trip_id=trip_id,
        traveler_id=traveler_id
    ).first()

    if not registration:
        return {
            "error":"Not register!",
            "message":"Traveler is not registered in this trip yet!"
        },400
    
    db.session.delete(registration)
    db.session.commit()

    return {
        "error":"Sucessfully removed!",
        "message":"Traveler is removed from this trip"
    },200



def add_expense_to_trip(trip_id,data):

    trip=db.session.get(Trip,trip_id)

    if not trip :
        return {
            "error":"Trip not found",
            "message":"expense do not added in the non-existing Trip"
        },404
    if trip.status not in ["PLANNED","ONGOING"]:
        return {
            "error":"incorrect trip_status",
            "message":"expenses only added for planned and ongoing  trip"
        },409
    
    title = data["title"].strip()
    new_expense = float(data["amount"])
    

    # Calculate current expenses
    current_expense = db.session.query(
        db.func.coalesce(
            db.func.sum(Expense.amount),
            0
        )
    ).filter(
        Expense.trip_id == trip_id
    ).scalar()



    # Check budget
    if current_expense + new_expense > trip.budget:
        return {
            "error":"Isufficient budget",
            "message":"Expense should be less than the budget"
        },409
    expense = Expense(
        trip_id=trip_id,
        title=title,
        amount=new_expense
    )
    db.session.add(expense)
    db.session.commit()

    return {
        "id": expense.id,
        "trip_id": trip.id,
        "title": expense.title,
        "amount": expense.amount
    }, 201




def get_summary_trip(trip_id):

    trip=db.session.get(Trip,trip_id)

    if not trip:
        return {
            "error":"Trip not found",
            "message":"summary cannot be calcuted from unknown trip"
        },404
    
    traveler_count = TripTraveler.query.filter_by(
        trip_id=trip_id
    ).count()


    total_expenses = db.session.query(
        db.func.coalesce( 
            db.func.sum(Expense.amount),
            0
        )
    ).filter(
        Expense.trip_id == trip_id
    ).scalar()

    remaining_budget=trip.budget-total_expenses

    return {
        "trip_id": trip.id,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "status": trip.status,
        "budget": trip.budget,
        "max_travelers": trip.max_travelers,
        "traveler_count": traveler_count,
        "total_expenses": total_expenses,
        "remaining_budget": remaining_budget
    } ,200