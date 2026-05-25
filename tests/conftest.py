import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture for FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Fixture providing fresh test activities.
    Returns a copy of the activities dict with known initial state.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }


@pytest.fixture(autouse=True)
def reset_activities(fresh_activities):
    """
    Auto-used fixture to reset activities before each test.
    Ensures test isolation by providing fresh data for each test.
    """
    from src.app import activities
    activities.clear()
    activities.update(fresh_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(fresh_activities)
