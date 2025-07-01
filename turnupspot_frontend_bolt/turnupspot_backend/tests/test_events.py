import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


def get_auth_headers(client: TestClient, user_data):
    """Helper function to get authentication headers"""
    # Register and login user
    client.post("/api/v1/auth/register", json=user_data)
    login_response = client.post("/api/v1/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_event(client: TestClient, test_user_data, test_event_data):
    """Test creating an event"""
    headers = get_auth_headers(client, test_user_data)
    
    response = client.post("/api/v1/events/", json=test_event_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == test_event_data["title"]
    assert data["event_type"] == test_event_data["event_type"]
    assert data["venue_name"] == test_event_data["venue_name"]


def test_get_events(client: TestClient, test_user_data, test_event_data):
    """Test getting events"""
    headers = get_auth_headers(client, test_user_data)
    
    # Create an event first
    client.post("/api/v1/events/", json=test_event_data, headers=headers)
    
    # Publish the event
    # Note: In a real scenario, you'd need to update the event status to PUBLISHED
    
    # Get events
    response = client.get("/api/v1/events/")
    assert response.status_code == 200
    
    # Since the event is in DRAFT status by default, it won't appear in public listing
    data = response.json()
    assert len(data) == 0  # No published events


def test_register_for_event(client: TestClient, test_user_data, test_event_data):
    """Test registering for an event"""
    headers = get_auth_headers(client, test_user_data)
    
    # Create and publish an event
    create_response = client.post("/api/v1/events/", json=test_event_data, headers=headers)
    event_id = create_response.json()["id"]
    
    # Update event status to published
    update_data = {"status": "published"}
    client.put(f"/api/v1/events/{event_id}", json=update_data, headers=headers)
    
    # Create another user to register for the event
    attendee_data = {
        "email": "attendee@example.com",
        "password": "password123",
        "first_name": "Attendee",
        "last_name": "User"
    }
    attendee_headers = get_auth_headers(client, attendee_data)
    
    # Register for the event
    response = client.post(f"/api/v1/events/{event_id}/register", json={}, headers=attendee_headers)
    assert response.status_code == 200
    assert "Registered successfully" in response.json()["message"]


def test_unregister_from_event(client: TestClient, test_user_data, test_event_data):
    """Test unregistering from an event"""
    headers = get_auth_headers(client, test_user_data)
    
    # Create and publish an event
    create_response = client.post("/api/v1/events/", json=test_event_data, headers=headers)
    event_id = create_response.json()["id"]
    
    # Update event status to published
    update_data = {"status": "published"}
    client.put(f"/api/v1/events/{event_id}", json=update_data, headers=headers)
    
    # Create another user to register and unregister
    attendee_data = {
        "email": "attendee@example.com",
        "password": "password123",
        "first_name": "Attendee",
        "last_name": "User"
    }
    attendee_headers = get_auth_headers(client, attendee_data)
    
    # Register for the event
    client.post(f"/api/v1/events/{event_id}/register", json={}, headers=attendee_headers)
    
    # Unregister from the event
    response = client.post(f"/api/v1/events/{event_id}/unregister", headers=attendee_headers)
    assert response.status_code == 200
    assert "Unregistered successfully" in response.json()["message"]


def test_get_event_attendees(client: TestClient, test_user_data, test_event_data):
    """Test getting event attendees (creator only)"""
    headers = get_auth_headers(client, test_user_data)
    
    # Create and publish an event
    create_response = client.post("/api/v1/events/", json=test_event_data, headers=headers)
    event_id = create_response.json()["id"]
    
    # Update event status to published
    update_data = {"status": "published"}
    client.put(f"/api/v1/events/{event_id}", json=update_data, headers=headers)
    
    # Get attendees (should work for creator)
    response = client.get(f"/api/v1/events/{event_id}/attendees", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_event_attendees_unauthorized(client: TestClient, test_user_data, test_event_data):
    """Test getting event attendees without authorization"""
    # Create event creator
    creator_headers = get_auth_headers(client, test_user_data)
    create_response = client.post("/api/v1/events/", json=test_event_data, headers=creator_headers)
    event_id = create_response.json()["id"]
    
    # Create another user
    other_user_data = {
        "email": "other@example.com",
        "password": "password123",
        "first_name": "Other",
        "last_name": "User"
    }
    other_headers = get_auth_headers(client, other_user_data)
    
    # Try to get attendees as non-creator
    response = client.get(f"/api/v1/events/{event_id}/attendees", headers=other_headers)
    assert response.status_code == 403