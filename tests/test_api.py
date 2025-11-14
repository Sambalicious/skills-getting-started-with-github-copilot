"""
Test cases for the Mergington High School Activities API endpoints.
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Test cases for the root endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index page."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test cases for the activities endpoint."""

    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of activities."""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that response contains expected default activities."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_response_structure(self, client, reset_activities):
        """Test the structure of activities response."""
        response = client.get("/activities")
        data = response.json()
        
        # Test a specific activity structure
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test cases for the signup endpoint."""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify the participant was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity."""
        email = "test@mergington.edu"
        activity_name = "Non-existent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_signed_up(self, client, reset_activities):
        """Test signup when student is already registered."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response.json()["detail"]

    def test_signup_at_capacity(self, client, reset_activities):
        """Test signup when activity is at maximum capacity."""
        from src.app import activities
        
        # Fill up Chess Club to capacity
        activity_name = "Chess Club"
        chess_club = activities[activity_name]
        max_participants = chess_club["max_participants"]
        
        # Fill to capacity with dummy emails
        chess_club["participants"] = [f"student{i}@mergington.edu" for i in range(max_participants)]
        
        # Try to add one more
        email = "overflow@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "maximum capacity" in response.json()["detail"]

    def test_signup_with_special_characters_in_activity_name(self, client, reset_activities):
        """Test signup with URL encoding for activity names."""
        from src.app import activities
        
        # Add an activity with special characters
        special_activity = "Art & Crafts Club"
        activities[special_activity] = {
            "description": "Creative arts and crafts",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 10,
            "participants": []
        }
        
        email = "artist@mergington.edu"
        encoded_activity = "Art%20%26%20Crafts%20Club"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK

    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with URL encoding for email addresses."""
        email = "test+user@mergington.edu"
        activity_name = "Chess Club"
        encoded_email = "test%2Buser%40mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={encoded_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the participant was added with correct email
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Test cases for the unregister endpoint."""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify the participant was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister for non-existent activity."""
        email = "test@mergington.edu"
        activity_name = "Non-existent Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregister when student is not registered."""
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not signed up" in response.json()["detail"]

    def test_unregister_with_special_characters(self, client, reset_activities):
        """Test unregister with URL encoding."""
        from src.app import activities
        
        # Add a test participant with special characters
        email = "test+user@mergington.edu"
        activity_name = "Chess Club"
        activities[activity_name]["participants"].append(email)
        
        encoded_email = "test%2Buser%40mergington.edu"
        response = client.delete(f"/activities/{activity_name}/unregister?email={encoded_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration test scenarios covering multiple operations."""

    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete signup and unregister workflow."""
        email = "workflow@mergington.edu"
        activity_name = "Programming Class"
        
        # Initial state - check participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup
        after_signup_response = client.get("/activities")
        after_signup_count = len(after_signup_response.json()[activity_name]["participants"])
        assert after_signup_count == initial_count + 1
        assert email in after_signup_response.json()[activity_name]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify unregister
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count
        assert email not in final_response.json()[activity_name]["participants"]

    def test_multiple_activities_signup(self, client, reset_activities):
        """Test signing up for multiple activities."""
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Basketball Team"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]

    def test_capacity_edge_cases(self, client, reset_activities):
        """Test edge cases around activity capacity."""
        from src.app import activities
        
        activity_name = "Basketball Team"
        activity = activities[activity_name]
        max_participants = activity["max_participants"]
        
        # Fill to one below capacity
        current_count = len(activity["participants"])
        emails_to_add = max_participants - current_count - 1
        
        for i in range(emails_to_add):
            email = f"filler{i}@mergington.edu"
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Add the last allowed participant
        last_email = "lastspot@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={last_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Try to add one more (should fail)
        overflow_email = "overflow@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={overflow_email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Remove one participant and try again (should succeed)
        client.delete(f"/activities/{activity_name}/unregister?email={last_email}")
        response = client.post(f"/activities/{activity_name}/signup?email={overflow_email}")
        assert response.status_code == status.HTTP_200_OK