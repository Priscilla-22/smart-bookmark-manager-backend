"""Tests for user management endpoints."""

import pytest
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    """Test creating a new user."""
    response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_users(client: TestClient):
    """Test getting all users."""
    client.post(
        "/api/users/",
        json={"username": "testuser1", "email": "test1@example.com"}
    )
    client.post(
        "/api/users/",
        json={"username": "testuser2", "email": "test2@example.com"}
    )
    
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_user_by_id(client: TestClient):
    """Test getting a user by ID."""
    create_response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    user_id = create_response.json()["id"]
    
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_get_nonexistent_user(client: TestClient):
    """Test getting a nonexistent user."""
    response = client.get("/api/users/999")
    assert response.status_code == 404

def test_create_duplicate_user(client: TestClient):
    """Test creating a user with duplicate username/email."""
    client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    
    response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "different@example.com"}
    )
    assert response.status_code == 400

def test_update_user(client: TestClient):
    """Test updating a user."""
    create_response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    user_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/users/{user_id}",
        json={"username": "updateduser", "email": "updated@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"

def test_delete_user(client: TestClient):
    """Test deleting a user."""
    create_response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    user_id = create_response.json()["id"]
    
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404