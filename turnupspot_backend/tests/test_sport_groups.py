import pytest
from fastapi.testclient import TestClient


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


def test_create_sport_group(client: TestClient, test_user_data, test_sport_group_data):
    """Test creating a sport group"""
    headers = get_auth_headers(client, test_user_data)
    
    response = client.post("/api/v1/sport-groups/", json=test_sport_group_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == test_sport_group_data["name"]
    assert data["sport_type"] == test_sport_group_data["sport_type"]
    assert data["venue_name"] == test_sport_group_data["venue_name"]


def test_get_sport_groups(client: TestClient, test_user_data, test_sport_group_data):
    """Test getting sport groups"""
    headers = get_auth_headers(client, test_user_data)
    
    # Create a sport group first
    client.post("/api/v1/sport-groups/", json=test_sport_group_data, headers=headers)
    
    # Get sport groups
    response = client.get("/api/v1/sport-groups/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == test_sport_group_data["name"]


def test_get_sport_group_by_id(client: TestClient, test_user_data, test_sport_group_data):
    """Test getting a sport group by ID"""
    headers = get_auth_headers(client, test_user_data)
    
    # Create a sport group first
    create_response = client.post("/api/v1/sport-groups/", json=test_sport_group_data, headers=headers)
    group_id = create_response.json()["id"]
    
    # Get sport group by ID
    response = client.get(f"/api/v1/sport-groups/{group_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == group_id
    assert data["name"] == test_sport_group_data["name"]


def test_join_sport_group(client: TestClient, test_user_data, test_sport_group_data):
    """Test joining a sport group"""
    # Create group creator
    creator_headers = get_auth_headers(client, test_user_data)
    create_response = client.post("/api/v1/sport-groups/", json=test_sport_group_data, headers=creator_headers)
    group_id = create_response.json()["id"]
    
    # Create another user to join the group
    joiner_data = {
        "email": "joiner@example.com",
        "password": "password123",
        "first_name": "Joiner",
        "last_name": "User"
    }
    joiner_headers = get_auth_headers(client, joiner_data)
    
    # Join the group
    response = client.post(f"/api/v1/sport-groups/{group_id}/join", json={}, headers=joiner_headers)
    assert response.status_code == 200
    assert "Join request submitted successfully" in response.json()["message"]


def test_leave_sport_group(client: TestClient, test_user_data, test_sport_group_data):
    """Test leaving a sport group"""
    # Create group and join it
    creator_headers = get_auth_headers(client, test_user_data)
    create_response = client.post("/api/v1/sport-groups/", json=test_sport_group_data, headers=creator_headers)
    group_id = create_response.json()["id"]
    
    # Create another user to join and leave the group
    joiner_data = {
        "email": "joiner@example.com",
        "password": "password123",
        "first_name": "Joiner",
        "last_name": "User"
    }
    joiner_headers = get_auth_headers(client, joiner_data)
    
    # Join the group
    client.post(f"/api/v1/sport-groups/{group_id}/join", json={}, headers=joiner_headers)
    
    # Leave the group
    response = client.post(f"/api/v1/sport-groups/{group_id}/leave", headers=joiner_headers)
    assert response.status_code == 200
    assert "Left group successfully" in response.json()["message"]


def test_update_sport_group_unauthorized(client: TestClient, test_user_data, test_sport_group_data):
    """Test updating sport group without authorization"""
    # Create group
    creator_headers = get_auth_headers(client, test_user_data)
    create_response = client.post("/api/v1/sport-groups/", json=test_sport_group_data, headers=creator_headers)
    group_id = create_response.json()["id"]
    
    # Create another user
    other_user_data = {
        "email": "other@example.com",
        "password": "password123",
        "first_name": "Other",
        "last_name": "User"
    }
    other_headers = get_auth_headers(client, other_user_data)
    
    # Try to update group as non-admin
    update_data = {"name": "Updated Group Name"}
    response = client.put(f"/api/v1/sport-groups/{group_id}", json=update_data, headers=other_headers)
    assert response.status_code == 403