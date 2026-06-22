"""
Tests for POST /activities/{activity_name}/signup endpoint.
"""

import pytest


class TestSignupForActivity:
    """Test suite for the signup endpoint."""

    def test_signup_new_student_successfully(self, client, reset_activities):
        """
        Test successful signup of a new student to an activity.
        
        Arrange: Prepare email for a student not yet signed up.
        Act: Send POST request to signup endpoint.
        Assert: Verify status 200, success message, and participant list updated.
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Test that signup to a nonexistent activity returns 404.
        
        Arrange: Prepare parameters with invalid activity name.
        Act: Send POST request to signup endpoint.
        Assert: Verify status 404 and error detail message.
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        """
        Test that duplicate signup returns 400 with appropriate error message.
        
        Arrange: Use a student already signed up for the activity.
        Act: Send POST request to signup endpoint with duplicate email.
        Assert: Verify status 400 and error detail about duplicate signup.
        """
        # Arrange
        activity_name = "Chess Club"
        duplicate_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_full_activity_returns_400(self, client, reset_activities):
        """
        Test that signup to a full activity returns 400.
        
        Arrange: Create a scenario where activity is at max capacity.
        Act: Send POST request to signup endpoint when activity is full.
        Assert: Verify status 400 and error detail about full activity.
        """
        # Arrange
        activity_name = "Tennis Club"
        max_participants = 10
        
        # Get current participant count
        activities_response = client.get("/activities")
        activities = activities_response.json()
        current_count = len(activities[activity_name]["participants"])
        
        # Sign up students until full
        for i in range(max_participants - current_count):
            email = f"fillstudent{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Act - Try to sign up one more when at capacity
        overfull_email = "overfull@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": overfull_email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"

    def test_signup_multiple_students_to_same_activity(self, client, reset_activities):
        """
        Test that multiple different students can sign up for the same activity.
        
        Arrange: Prepare multiple unique email addresses.
        Act: Sign up each student sequentially.
        Assert: Verify all students are added and counts increase appropriately.
        """
        # Arrange
        activity_name = "Programming Class"
        new_emails = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Act & Assert for each signup
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert all students were added
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities[activity_name]["participants"])
        assert final_count == initial_count + len(new_emails)
        for email in new_emails:
            assert email in final_activities[activity_name]["participants"]

    def test_signup_email_case_sensitivity(self, client, reset_activities):
        """
        Test signup with different email case variations.
        
        Arrange: Prepare two similar emails with different cases.
        Act: Sign up with lowercase, then attempt signup with uppercase.
        Assert: Verify they are treated as different emails (case-sensitive).
        """
        # Arrange
        activity_name = "Music Band"
        email_lower = "newmusician@mergington.edu"
        email_upper = "NEWMUSICIAN@MERGINGTON.EDU"

        # Act - Sign up with lowercase
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_lower}
        )

        # Act - Try to sign up with uppercase
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_upper}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200  # Treated as different email
        
        # Verify both are in participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email_lower in activities[activity_name]["participants"]
        assert email_upper in activities[activity_name]["participants"]
