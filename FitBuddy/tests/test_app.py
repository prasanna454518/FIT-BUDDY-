import os
import uuid

os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db


init_db()
client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_generate_demo_plan():
    payload = {
        "username": "Test User",
        "user_id": "test_api_001",
        "age": 22,
        "weight": 68,
        "goal": "general wellness",
        "intensity": "medium",
    }
    # Avoid duplicate failures if the test is rerun against an existing DB.
    client.post("/admin/login", data={"username": "admin", "password": "fitbuddy-admin"})
    response = client.post("/api/generate-workout", json=payload)
    if response.status_code == 409:
        response = client.get("/api/users/test_api_001")
    assert response.status_code == 200
    assert "workout_plan" in response.json() or "plan" in response.json()


def test_generate_workout_form_renders_result_page():
    user_id = f"browser_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/generate-workout",
        data={
            "username": "Browser User",
            "user_id": user_id,
            "age": 26,
            "weight": 72,
            "goal": "general wellness",
            "intensity": "medium",
        },
    )
    assert response.status_code == 200
    assert "YOUR PERSONAL PLAN" in response.text
    assert "7-Day Workout Plan" in response.text


def test_feedback_demo_plan():
    response = client.post(
        "/api/submit-feedback",
        json={"user_id": "test_api_001", "feedback": "Add more recovery days."},
    )
    assert response.status_code == 200
    assert "updated_plan" in response.json()
