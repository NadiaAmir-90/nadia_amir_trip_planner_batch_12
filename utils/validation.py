from datetime import datetime

# Allowed trip status values
ALLOWED_STATUSES = {
    "PLANNED",
    "ONGOING",
    "COMPLETED",
    "CANCELLED",
}


def validate_trip_data(data, allow_missing_attribute=False):
    errors = {}

    # check data format
    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object."}

    # check destination
    if not allow_missing_attribute or "destination" in data:
        destination = data.get("destination")
        if not destination:
            errors["destination"] = "Destination is required."
        elif not isinstance(destination, str):
            errors["destination"] = "Destination must be a string."
        elif not destination.strip():
            errors["destination"] = "Destination cannot be empty."
        elif len(destination.strip()) > 100:
            errors["destination"] = "Destination must not exceed 100 characters."

    # check start_date
    if not allow_missing_attribute or "start_date" in data:
        start_date = data.get("start_date")
        if not start_date:
            errors["start_date"] = "Start date is required."
        elif not isinstance(start_date, str):
            errors["start_date"] = "Start date must be in YYYY-MM-DD format."
        else:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                errors["start_date"] = "Start date must be in YYYY-MM-DD format."

    # check end_date
    if not allow_missing_attribute or "end_date" in data:
        end_date = data.get("end_date")
        if not end_date:
            errors["end_date"] = "End date is required."
        elif not isinstance(end_date, str):
            errors["end_date"] = "End date must be in YYYY-MM-DD format."
        else:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                errors["end_date"] = "End date must be in YYYY-MM-DD format."

    # check that end date is not before start date (only if both are present and valid)
    if (
        "start_date" not in errors
        and "end_date" not in errors
        and "start_date" in data
        and "end_date" in data
    ):
        start = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        if end < start:
            errors["end_date"] = "End date cannot be before start date."

    # check budget
    if not allow_missing_attribute or "budget" in data:
        budget = data.get("budget")

        if budget is None:
            errors["budget"] = "Budget is required."
        elif isinstance(budget, bool) or not isinstance(budget, (int, float)):
            errors["budget"] = "Budget must be a number."
        elif budget < 0:
            errors["budget"] = "Budget cannot be negative."

    # check max_travelers
    if not allow_missing_attribute or "max_travelers" in data:
        max_travelers = data.get("max_travelers")

        if max_travelers is None:
            errors["max_travelers"] = "Maximum travelers is required."
        elif isinstance(max_travelers, bool) or not isinstance(max_travelers, int):
            errors["max_travelers"] = "Maximum travelers must be an integer."
        elif max_travelers <= 0:
            errors["max_travelers"] = "Maximum travelers must be greater than 0."

    # check status
    if not allow_missing_attribute or "status" in data:
        status = data.get("status")

        if not status:
            return status
        elif not isinstance(status, str):
            errors["status"] = "Status must be a string."
        elif status.upper() not in ALLOWED_STATUSES:
            errors["status"] = (
                "Status must be one of: PLANNED, ONGOING, COMPLETED, CANCELLED."
            )

    return errors


def validate_traveler_data(data):
    if not isinstance(data,dict):
        return "Request Data must be JSON object!"

    name=data.get("name")
    email=data.get("email")
    
    if not name:
        return "Name is Required !"
    if not isinstance(name,str):
        return "Name must be string"
    if not email:
        return "email is required !"
    if not isinstance(email,str):
        return "email must be a string"
    
    return None


def validate_expense_data(data):

    if not isinstance(data,dict):
        return "Request body must be JSON object!"
    
    title=data.get("title")
    amount=data.get("amount")

    if not title:
        return "Title must be Required !"
    if not isinstance(title,str):
        return "Title must be string"
    if not amount:
        return "amount is required"
    if not isinstance(amount,int):
        return "amount must be a interger"
    if amount<=0:
        return "amount must be greater than 0"







    
    

    