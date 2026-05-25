import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        AAA Test: Retrieve all activities and verify structure.
        Arrange: Client is ready.
        Act: Send GET request to /activities.
        Assert: Verify response contains all activities with correct keys.
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for activity_name in expected_activities:
            assert activity_name in data
            assert "description" in data[activity_name]
            assert "schedule" in data[activity_name]
            assert "max_participants" in data[activity_name]
            assert "participants" in data[activity_name]

    def test_get_activities_includes_participants(self, client):
        """
        AAA Test: Verify participant list is included for each activity.
        Arrange: Client is ready.
        Act: Send GET request to /activities.
        Assert: Verify participants list contains expected emails.
        """
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert data["Chess Club"]["participants"] == expected_chess_participants

    def test_get_activities_calculates_availability(self, client):
        """
        AAA Test: Verify availability is correctly calculated.
        Arrange: Chess Club has 2 participants, max 12 -> 10 spots left.
        Act: Send GET request to /activities.
        Assert: Verify spots available match calculation.
        """
        # Arrange
        chess_max = 12
        chess_participants = 2
        expected_spots_left = chess_max - chess_participants

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        actual_participants = len(data["Chess Club"]["participants"])
        assert actual_participants == chess_participants
        assert chess_max - actual_participants == expected_spots_left


class TestPostSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_adds_participant(self, client):
        """
        AAA Test: Successfully sign up a new participant.
        Arrange: New email ready to sign up for Chess Club (2 current participants).
        Act: Send POST signup request.
        Assert: Participant added, response confirms success, participant count increases.
        """
        # Arrange
        activity = "Chess Club"
        email = "alice@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

        # Verify participant was actually added
        verify_response = client.get("/activities")
        new_count = len(verify_response.json()[activity]["participants"])
        assert new_count == initial_count + 1
        assert email in verify_response.json()[activity]["participants"]

    def test_signup_activity_not_found_returns_404(self, client):
        """
        AAA Test: Signup to non-existent activity returns 404.
        Arrange: Non-existent activity name.
        Act: Send POST signup request.
        Assert: Response is 404 with appropriate error message.
        """
        # Arrange
        activity = "Nonexistent Club"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_signed_up_returns_400(self, client):
        """
        AAA Test: Signup with already-registered email returns 400.
        Arrange: Use email already signed up for Chess Club.
        Act: Send POST signup request with duplicate email.
        Assert: Response is 400 with conflict message.
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_different_activities(self, client):
        """
        AAA Test: Same email can sign up for multiple activities.
        Arrange: New email ready to sign up.
        Act: Sign up for two different activities.
        Assert: Participant appears in both activities.
        """
        # Arrange
        email = "bob@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(f"/activities/{activity1}/signup", params={"email": email})
        response2 = client.post(f"/activities/{activity2}/signup", params={"email": email})

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        verify_response = client.get("/activities")
        data = verify_response.json()
        assert email in data[activity1]["participants"]
        assert email in data[activity2]["participants"]


class TestDeleteParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_delete_participant_removes_from_activity(self, client):
        """
        AAA Test: Successfully remove a participant from an activity.
        Arrange: Participant "michael@mergington.edu" is in Chess Club.
        Act: Send DELETE request to remove participant.
        Assert: Participant removed, count decreases, response confirms.
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

        # Verify participant was actually removed
        verify_response = client.get("/activities")
        new_count = len(verify_response.json()[activity]["participants"])
        assert new_count == initial_count - 1
        assert email not in verify_response.json()[activity]["participants"]

    def test_delete_activity_not_found_returns_404(self, client):
        """
        AAA Test: Delete from non-existent activity returns 404.
        Arrange: Non-existent activity name.
        Act: Send DELETE request.
        Assert: Response is 404.
        """
        # Arrange
        activity = "Nonexistent Club"
        email = "alice@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_delete_participant_not_found_returns_404(self, client):
        """
        AAA Test: Delete non-existent participant returns 404.
        Arrange: Email not signed up for Chess Club.
        Act: Send DELETE request with non-existent email.
        Assert: Response is 404 with participant not found message.
        """
        # Arrange
        activity = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_delete_same_participant_twice_fails_second_time(self, client):
        """
        AAA Test: Attempting to delete the same participant twice fails on second attempt.
        Arrange: Participant in Chess Club.
        Act: Send DELETE request, then attempt again.
        Assert: First succeeds (200), second fails (404).
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        first_response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        second_response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 404


class TestIntegration:
    """Integration tests across multiple operations."""

    def test_signup_and_delete_flow(self, client):
        """
        AAA Test: Complete flow of signup and delete operations.
        Arrange: Fresh activities state.
        Act: Sign up new participant, verify in list, delete, verify gone.
        Assert: Each step has expected state.
        """
        # Arrange
        activity = "Programming Class"
        email = "charlie@mergington.edu"

        # Act & Assert - Initial state
        initial = client.get("/activities").json()
        assert email not in initial[activity]["participants"]

        # Act & Assert - After signup
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        after_signup = client.get("/activities").json()
        assert email in after_signup[activity]["participants"]

        # Act & Assert - After delete
        delete_response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert delete_response.status_code == 200
        after_delete = client.get("/activities").json()
        assert email not in after_delete[activity]["participants"]
