"""
Tests for GET /activities endpoint.
"""

import pytest


class TestGetActivities:
    """Test suite for the activities list endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: No setup needed, using default state.
        Act: Make GET request to /activities.
        Assert: Verify status 200 and all activities are returned with expected fields.
        """
        # Arrange
        expected_activity_count = 9
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert activity_name  # Not empty
            assert set(activity_data.keys()) == expected_fields

    def test_get_activities_returns_chess_club(self, client, reset_activities):
        """
        Test that GET /activities includes Chess Club with correct initial state.
        
        Arrange: No setup needed, using default state.
        Act: Make GET request to /activities.
        Assert: Verify Chess Club exists with expected participants.
        """
        # Arrange
        expected_activity = "Chess Club"
        expected_initial_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert expected_activity in activities
        assert activities[expected_activity]["participants"] == expected_initial_participants

    def test_get_activities_participant_lists_are_lists(self, client, reset_activities):
        """
        Test that participants field is always a list in all activities.
        
        Arrange: No setup needed, using default state.
        Act: Make GET request to /activities.
        Assert: Verify all participants lists are of type list.
        """
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants is not a list"

    def test_get_activities_max_participants_is_positive_integer(self, client, reset_activities):
        """
        Test that max_participants is a positive integer for all activities.
        
        Arrange: No setup needed, using default state.
        Act: Make GET request to /activities.
        Assert: Verify max_participants is a positive integer.
        """
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0, \
                f"{activity_name} max_participants is not positive"
