"""
Test cases for the FastAPI activities API
"""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that the response contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_info in data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)
    
    def test_activity_participants_are_emails(self, client):
        """Test that participants are strings (email addresses)"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_info in data.values():
            for participant in activity_info["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Chess Club"]["participants"])
        
        # Sign up
        client.post("/activities/Chess%20Club/signup?email=test123@mergington.edu")
        
        # Check new count
        response2 = client.get("/activities")
        new_count = len(response2.json()["Chess Club"]["participants"])
        
        assert new_count == initial_count + 1
        assert "test123@mergington.edu" in response2.json()["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student can't sign up twice for the same activity"""
        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Duplicate signup
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with valid email containing special characters"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=user+test@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test that multiple different students can sign up"""
        emails = ["alice@test.edu", "bob@test.edu", "charlie@test.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Tennis%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are added
        response = client.get("/activities")
        participants = response.json()["Tennis Club"]["participants"]
        for email in emails:
            assert email in participants


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        # Verify participant exists
        response1 = client.get("/activities")
        assert "michael@mergington.edu" in response1.json()["Chess Club"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        
        # Verify participant is removed
        response2 = client.get("/activities")
        assert "michael@mergington.edu" not in response2.json()["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from activity that doesn't exist"""
        response = client.delete(
            "/activities/Fake%20Club/participants?email=test@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregistering someone who isn't registered"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=notarealstudent@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_twice_fails(self, client, reset_activities):
        """Test that unregistering twice fails"""
        # First unregister
        response1 = client.delete(
            "/activities/Basketball/participants?email=james@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            "/activities/Basketball/participants?email=james@mergington.edu"
        )
        assert response2.status_code == 404


class TestRootRedirect:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestStaticFiles:
    """Tests for static file serving"""
    
    def test_can_get_index_html(self, client):
        """Test that we can retrieve index.html"""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_can_get_app_js(self, client):
        """Test that we can retrieve app.js"""
        response = client.get("/static/app.js")
        assert response.status_code == 200
    
    def test_can_get_styles_css(self, client):
        """Test that we can retrieve styles.css"""
        response = client.get("/static/styles.css")
        assert response.status_code == 200


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete signup and unregister workflow"""
        email = "integration@test.edu"
        activity = "Art%20Studio"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signed up
        check1 = client.get("/activities").json()
        assert email in check1["Art Studio"]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/participants?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        check2 = client.get("/activities").json()
        assert email not in check2["Art Studio"]["participants"]
    
    def test_capacity_updates(self, client, reset_activities):
        """Test that capacity numbers update correctly"""
        activity = "Music%20Ensemble"
        
        # Check initial capacity
        initial = client.get("/activities").json()
        initial_count = len(initial["Music Ensemble"]["participants"])
        
        # Add participant
        client.post(f"/activities/{activity}/signup?email=newmusician@test.edu")
        
        # Check new capacity
        after_add = client.get("/activities").json()
        after_add_count = len(after_add["Music Ensemble"]["participants"])
        
        assert after_add_count == initial_count + 1
        
        # Remove participant
        client.delete(f"/activities/{activity}/participants?email=newmusician@test.edu")
        
        # Check back to initial
        after_remove = client.get("/activities").json()
        after_remove_count = len(after_remove["Music Ensemble"]["participants"])
        
        assert after_remove_count == initial_count
