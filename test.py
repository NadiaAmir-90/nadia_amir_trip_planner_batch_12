import os
import tempfile
import pytest

# Use a throw-away SQLite file so the real database is never touched.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

try:
    from app import create_app
except ImportError:  
    from app import app as _global_app

    def create_app():
        return _global_app

from database.db import db 

PREFIX = ""  


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.remove()


def teardown_module(module):
    os.close(_db_fd)
    os.remove(_db_path)


# helper function
def url(path):
    return f"{PREFIX}{path}"


def trip_payload(**overrides):
    payload = {
        "destination": "Cox's Bazar",
        "start_date": "2026-12-10",
        "end_date": "2026-12-15",
        "budget": 50000,
        "max_travelers": 3,
    }
    payload.update(overrides)
    return payload


def create_trip(client, **overrides):
    res = client.post(url("/create_trip"), json=trip_payload(**overrides))
    assert res.status_code == 201, res.get_json()
    return res.get_json()


def add_traveler(client, trip_id, name="Rahim", email="rahim@example.com"):
    return client.post(
        url(f"/add_traveler/trip/{trip_id}"),
        json={"name": name, "email": email},
    )


def set_status(client, trip_id, status):
    return client.patch(
        url(f"/update_status_of_trip/{trip_id}"), json={"status": status}
    )


#TRIP CRUD
class TestTripCrud:
    def test_create_trip_success(self, client):
        trip = create_trip(client)
        assert trip["id"] == 1
        assert trip["destination"] == "Cox's Bazar"
        assert trip["status"] == "PLANNED"  

    def test_create_trip_status_is_uppercased(self, client):
        trip = create_trip(client, status="planned")
        assert trip["status"] == "PLANNED"

    def test_create_trip_strips_destination(self, client):
        trip = create_trip(client, destination="  Sylhet  ")
        assert trip["destination"] == "Sylhet"

    @pytest.mark.parametrize(
        "overrides",
        [
            {"destination": ""},
            {"destination": 123},
            {"start_date": "10-12-2026"},
            {"end_date": "not-a-date"},
            {"end_date": "2026-12-01"},  
            {"budget": -5},
            {"budget": "lots"},
            {"budget": True},
            {"max_travelers": 0},
            {"max_travelers": 2.5},
            {"status": "UNKNOWN"},
        ],
    )
    def test_create_trip_validation_errors(self, client, overrides):
        res = client.post(url("/create_trip"), json=trip_payload(**overrides))
        assert res.status_code == 400

    @pytest.mark.parametrize(
        "missing", ["destination", "start_date", "end_date", "budget", "max_travelers"]
    )
    def test_create_trip_missing_required_field(self, client, missing):
        payload = trip_payload()
        payload.pop(missing)
        res = client.post(url("/create_trip"), json=payload)
        assert res.status_code == 400

    def test_get_all_trips(self, client):
        create_trip(client, destination="A")
        create_trip(client, destination="B")
        res = client.get(url("/all_trips"))
        assert res.status_code == 200
        assert [t["destination"] for t in res.get_json()] == ["A", "B"]

    def test_get_one_trip(self, client):
        trip = create_trip(client)
        res = client.get(url(f"/get_trip/{trip['id']}"))
        assert res.status_code == 200
        assert res.get_json()["id"] == trip["id"]

    def test_get_trip_not_found(self, client):
        assert client.get(url("/get_trip/999")).status_code == 404

    def test_update_trip_full(self, client):
        trip = create_trip(client)
        res = client.put(
            url(f"/update_trip/{trip['id']}"),
            json=trip_payload(budget=70000, status="PLANNED"),
        )
        assert res.status_code == 200
        assert res.get_json()["budget"] == 70000

    def test_update_trip_partial(self, client):
        trip = create_trip(client)
        res = client.put(url(f"/update_trip/{trip['id']}"), json={"budget": 60000})
        assert res.status_code == 200
        assert res.get_json()["budget"] == 60000

    def test_update_trip_not_found(self, client):
        res = client.put(url("/update_trip/999"), json={"budget": 1})
        assert res.status_code == 404

    def test_cannot_update_completed_trip(self, client):
        trip = create_trip(client)
        set_status(client, trip["id"], "ONGOING")
        set_status(client, trip["id"], "COMPLETED")
        res = client.put(url(f"/update_trip/{trip['id']}"), json={"budget": 1})
        assert res.status_code == 409

    def test_update_max_travelers_below_current_count(self, client):
        trip = create_trip(client, max_travelers=3)
        add_traveler(client, trip["id"], "A", "a@example.com")
        add_traveler(client, trip["id"], "B", "b@example.com")
        res = client.put(
            url(f"/update_trip/{trip['id']}"), json={"max_travelers": 1}
        )
        assert res.status_code == 409

    def test_delete_trip(self, client):
        trip = create_trip(client)
        res = client.delete(url(f"/detele_trip/{trip['id']}"))  # route typo kept
        assert res.status_code == 200
        assert client.get(url(f"/get_trip/{trip['id']}")).status_code == 404

    def test_delete_trip_not_found(self, client):
        assert client.delete(url("/detele_trip/999")).status_code == 404

# Status lifecycle
class TestStatusTransitions:
    def test_planned_to_ongoing_to_completed(self, client):
        trip = create_trip(client)
        assert set_status(client, trip["id"], "ONGOING").status_code == 200
        res = set_status(client, trip["id"], "COMPLETED")
        assert res.status_code == 200
        assert res.get_json()["status"] == "COMPLETED"

    def test_status_is_case_insensitive(self, client):
        trip = create_trip(client)
        res = set_status(client, trip["id"], "ongoing")
        assert res.status_code == 200
        assert res.get_json()["status"] == "ONGOING"

    def test_planned_to_cancelled(self, client):
        trip = create_trip(client)
        assert set_status(client, trip["id"], "CANCELLED").status_code == 200

    def test_cannot_skip_ongoing(self, client):
        trip = create_trip(client)
        assert set_status(client, trip["id"], "COMPLETED").status_code == 409

    @pytest.mark.parametrize("final", ["COMPLETED", "CANCELLED"])
    def test_final_states_cannot_change(self, client, final):
        trip = create_trip(client)
        if final == "COMPLETED":
            set_status(client, trip["id"], "ONGOING")
        set_status(client, trip["id"], final)
        assert set_status(client, trip["id"], "PLANNED").status_code == 409
        assert set_status(client, trip["id"], "ONGOING").status_code == 409

    def test_invalid_status_value(self, client):
        trip = create_trip(client)
        assert set_status(client, trip["id"], "FLYING").status_code == 400

    def test_missing_status(self, client):
        trip = create_trip(client)
        res = client.patch(url(f"/update_status_of_trip/{trip['id']}"), json={})
        assert res.status_code == 400

    def test_status_trip_not_found(self, client):
        assert set_status(client, 999, "ONGOING").status_code == 404


