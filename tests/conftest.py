"""
Pytest configuration and fixtures for testing the FastAPI app
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    initial_state = {
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
        "Basketball": {
            "description": "Team basketball practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and competitive matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["aiden@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation skills and compete in debates",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu", "noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore science experiments and scientific inquiry",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu"]
        }
    }
    yield
    # Reset after test
    activities.clear()
    activities.update(initial_state)
