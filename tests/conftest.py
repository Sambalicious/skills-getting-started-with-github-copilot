"""
Test configuration and fixtures for the Mergington High School API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store original activities
    original_activities = {
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
        },
        # Sports Activities
        "Basketball Team": {
            "description": "Competitive basketball team training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Soccer skills development and friendly matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "carlos@mergington.edu"]
        },
        # Artistic Activities
        "Drama Club": {
            "description": "Acting, script writing, and theatrical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art projects",
            "schedule": "Fridays, 2:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        # Intellectual Activities
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu", "zoe@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "STEM competitions and advanced science projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu", "lily@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity():
    """Provide a sample activity for testing."""
    return {
        "description": "Test activity for unit tests",
        "schedule": "Test schedule",
        "max_participants": 5,
        "participants": ["test1@mergington.edu", "test2@mergington.edu"]
    }