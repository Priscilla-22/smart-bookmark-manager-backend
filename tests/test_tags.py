"""Tests for tag management endpoints."""

import pytest
from fastapi.testclient import TestClient

def test_create_tag(client: TestClient):
    """Test creating a new tag."""
    response = client.post(
        "/api/tags/",
        json={"name": "work", "color": "#FF0000"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "work"
    assert data["color"] == "#FF0000"
    assert "id" in data

def test_get_tags(client: TestClient):
    """Test getting all tags."""
    client.post("/api/tags/", json={"name": "work"})
    client.post("/api/tags/", json={"name": "personal"})
    
    response = client.get("/api/tags/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_tag_by_id(client: TestClient):
    """Test getting a tag by ID."""
    create_response = client.post(
        "/api/tags/",
        json={"name": "work"}
    )
    tag_id = create_response.json()["id"]
    
    response = client.get(f"/api/tags/{tag_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "work"

def test_create_duplicate_tag(client: TestClient):
    """Test creating a tag with duplicate name."""
    client.post("/api/tags/", json={"name": "work"})
    
    response = client.post("/api/tags/", json={"name": "work"})
    assert response.status_code == 400

def test_update_tag(client: TestClient):
    """Test updating a tag."""
    create_response = client.post(
        "/api/tags/",
        json={"name": "work"}
    )
    tag_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/tags/{tag_id}",
        json={"name": "business", "color": "#00FF00"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "business"
    assert data["color"] == "#00FF00"

def test_delete_tag(client: TestClient):
    """Test deleting a tag."""
    create_response = client.post(
        "/api/tags/",
        json={"name": "work"}
    )
    tag_id = create_response.json()["id"]
    
    response = client.delete(f"/api/tags/{tag_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/api/tags/{tag_id}")
    assert get_response.status_code == 404

def test_bookmark_with_tags(client: TestClient):
    """Test creating bookmark with tags."""
    user_response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com"}
    )
    user_id = user_response.json()["id"]
    
    tag_response = client.post("/api/tags/", json={"name": "work"})
    tag_id = tag_response.json()["id"]
    
    response = client.post(
        "/api/bookmarks/",
        json={
            "url": "https://example.com",
            "title": "Work Bookmark",
            "user_id": user_id,
            "tag_ids": [tag_id]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "work"