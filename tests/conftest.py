"""
Shared pytest fixtures for backend API tests.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to preserve and restore the activities state between tests.
    Prevents test cross-contamination from in-memory state mutations.
    """
    # Save the initial state
    initial_state = deepcopy(activities)
    
    # Yield to the test
    yield
    
    # Restore the initial state after test
    activities.clear()
    activities.update(initial_state)
