"""
Tests for POST /activities/{activity_name}/unregister endpoint.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for the unregister endpoint."""

    def test_unregister_existing_participant_successfully(self, client, reset_activities):
        """
        Test successful unregistration of a student from an activity.
        
        Arrange: Use a student already signed up for the activity.
        Act: Send POST request to unregister endpoint.
        Assert: Verify status 200, success message, and participant removed.
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email_to_remove not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Test that unregister from a nonexistent activity returns 404.
        
        Arrange: Prepare parameters with invalid activity name.
        Act: Send POST request to unregister endpoint.
        Assert: Verify status 404 and error detail message.
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_non_participant_returns_400(self, client, reset_activities):
        """
        Test that unregister of a non-participant returns 400.
        
        Arrange: Use a student not signed up for the activity.
        Act: Send POST request to unregister endpoint with non-participant email.
        Assert: Verify status 400 and appropriate error detail.
        """
        # Arrange
        activity_name = "Art Studio"
        non_participant_email = "notinart@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": non_participant_email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_and_rejoin_activity(self, client, reset_activities):
        """
        Test that a student can unregister and then sign up again.
        
        Arrange: Use an activity and an email to add, remove, and re-add.
        Act: Sign up, unregister, sign up again.
        Assert: Verify status codes at each step and final participant list is correct.
        """
        # Arrange
        activity_name = "Debate Team"
        email = "rejoin@mergington.edu"

        # Act & Assert - Initial signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

        # Act & Assert - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

        # Act & Assert - Rejoin
        rejoin_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert rejoin_response.status_code == 200
        
        # Verify re-added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_unregister_multiple_students_sequentially(self, client, reset_activities):
        """
        Test unregistering multiple students from the same activity.
        
        Arrange: Sign up multiple new students, track their count.
        Act: Unregister each student sequentially.
        Assert: Verify participant count decreases correctly at each step.
        """
        # Arrange
        activity_name = "Science Club"
        new_emails = [
            "sciencestudent1@mergington.edu",
            "sciencestudent2@mergington.edu",
            "sciencestudent3@mergington.edu"
        ]
        
        # Sign up new students
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Get count after signups
        activities_response = client.get("/activities")
        count_after_signup = len(activities_response.json()[activity_name]["participants"])

        # Act & Assert - Unregister each student
        for i, email in enumerate(new_emails):
            response = client.post(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
            
            # Verify count decreased
            activities_response = client.get("/activities")
            current_count = len(activities_response.json()[activity_name]["participants"])
            expected_count = count_after_signup - (i + 1)
            assert current_count == expected_count

    def test_unregister_preserves_other_participants(self, client, reset_activities):
        """
        Test that unregistering one student doesn't affect other participants.
        
        Arrange: Get list of current participants and identify one to remove.
        Act: Unregister that participant.
        Assert: Verify other participants remain in the activity.
        """
        # Arrange
        activity_name = "Basketball Team"
        
        # Get current participants
        activities_response = client.get("/activities")
        current_participants = activities_response.json()[activity_name]["participants"].copy()
        email_to_remove = current_participants[0]
        other_participants = current_participants[1:]

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify removed participant is gone
        activities_response = client.get("/activities")
        final_participants = activities_response.json()[activity_name]["participants"]
        assert email_to_remove not in final_participants
        
        # Verify other participants are still there
        for email in other_participants:
            assert email in final_participants
