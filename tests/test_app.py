import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participant lists before each test to avoid state leakage."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_200():
    # Arrange - client is already set up

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_all_activities():
    # Arrange - client is already set up

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_expected_fields():
    # Arrange - client is already set up

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant():
    # Arrange
    email = "test@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    response = client.get("/activities")

    # Assert
    assert email in response.json()[activity_name]["participants"]


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    email = "test@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404


def test_signup_duplicate_returns_400():
    # Arrange
    email = "dup@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400


# --- DELETE /activities/{activity_name}/signup ---

def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    response = client.get("/activities")

    # Assert
    assert email not in response.json()[activity_name]["participants"]


def test_unregister_nonexistent_activity_returns_404():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_nonexistent_participant_returns_404():
    # Arrange
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
