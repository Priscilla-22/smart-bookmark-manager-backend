"""Tests for bookmark management endpoints."""

import pytest
from fastapi.testclient import TestClient

def create_test_user(client: TestClient):
    """Helper function to create a test user."""
    response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    return response.json()["id"]

def test_create_bookmark(client: TestClient):
    """Test creating a new bookmark."""
    user_id = create_test_user(client)
    
    response = client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example.com",
            "title": "Test Bookmark",
            "description": "A test bookmark",
            "user_id": user_id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Bookmark"
    assert data["url"] == "https://example.com"
    assert data["user_id"] == user_id

def test_get_bookmarks(client: TestClient):
    """Test getting all bookmarks."""
    user_id = create_test_user(client)
    
    client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example1.com",
            "title": "Bookmark 1",
            "user_id": user_id
        }
    )
    client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example2.com",
            "title": "Bookmark 2",
            "user_id": user_id
        }
    )
    
    response = client.get("/api/bookmarks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_bookmarks_by_user(client: TestClient):
    """Test getting bookmarks filtered by user."""
    user_id1 = create_test_user(client)
    user_id2 = client.post(
        "/api/users/",
        json={"username": "testuser2", "email": "test2@example.com"}
    ).json()["id"]
    
    client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example1.com",
            "title": "User 1 Bookmark",
            "user_id": user_id1
        }
    )
    client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example2.com",
            "title": "User 2 Bookmark",
            "user_id": user_id2
        }
    )
    
    response = client.get(f"/api/bookmarks/?user_id={user_id1}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == user_id1

def test_get_bookmark_by_id(client: TestClient):
    """Test getting a bookmark by ID."""
    user_id = create_test_user(client)
    
    create_response = client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example.com",
            "title": "Test Bookmark",
            "user_id": user_id
        }
    )
    bookmark_id = create_response.json()["id"]
    
    response = client.get(f"/api/bookmarks/{bookmark_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Bookmark"

def test_update_bookmark(client: TestClient):
    """Test updating a bookmark."""
    user_id = create_test_user(client)
    
    create_response = client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example.com",
            "title": "Test Bookmark",
            "user_id": user_id
        }
    )
    bookmark_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/bookmarks/{bookmark_id}",
        json={
            "title": "Updated Bookmark",
            "description": "Updated description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Bookmark"
    assert data["description"] == "Updated description"

def test_delete_bookmark(client: TestClient):
    """Test deleting a bookmark."""
    user_id = create_test_user(client)
    
    create_response = client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example.com",
            "title": "Test Bookmark",
            "user_id": user_id
        }
    )
    bookmark_id = create_response.json()["id"]
    
    response = client.delete(f"/api/bookmarks/{bookmark_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/api/bookmarks/{bookmark_id}")
    assert get_response.status_code == 404