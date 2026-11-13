import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import httpx

# Route the database to an in-memory or temp file for testing before importing the app
os.environ["SYNC_DB_PATH"] = "test_sync.db"
from src.app import app, DB_PATH

@pytest.fixture(autouse=True)
def setup_db():
    # Clean up before test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    # Using TestClient within a context manager automatically triggers FastAPI's lifespan events (DB creation)
    with TestClient(app) as client:
        yield client
        
    # Clean up after test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_valid_submission(setup_db):
    client = setup_db
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        # CLANCY FIX: use a real httpx.Response. Setting attributes on the
        # AsyncMock's return value made .json() and .raise_for_status()
        # async, so resp.json() returned an un-awaited coroutine.
        mock_post.return_value = httpx.Response(201, json={"id": 11}, request=httpx.Request("POST", "https://jsonplaceholder.typicode.com/users"))
        
        payload = {"name": "Alice", "email": "alice@example.com", "message": "I need help."}
        response = client.post("/webhooks/contact", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "synced"
        assert data["crm_id"] == "11"
        assert "contact_id" in data
        mock_post.assert_called_once()
        
        # Verify sync log insertion
        log_res = client.get("/sync-log")
        assert log_res.status_code == 200
        logs = log_res.json()
        assert len(logs) == 1
        assert logs[0]["email"] == "alice@example.com"
        assert logs[0]["status"] == "synced"

def test_invalid_email(setup_db):
    payload = {"name": "Alice", "email": "not-an-email", "message": "Hi"}
    response = setup_db.post("/webhooks/contact", json=payload)
    assert response.status_code == 422

def test_missing_required_field(setup_db):
    payload = {"email": "alice@example.com", "message": "Hi"} # Missing 'name'
    response = setup_db.post("/webhooks/contact", json=payload)
    assert response.status_code == 422

def test_duplicate_email(setup_db):
    client = setup_db
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        # CLANCY FIX: real httpx.Response (see test_valid_submission).
        mock_post.return_value = httpx.Response(201, json={"id": 22}, request=httpx.Request("POST", "https://jsonplaceholder.typicode.com/users"))
        
        payload = {"name": "Bob", "email": "bob@example.com", "message": "First ask"}
        
        # First successful call
        res1 = client.post("/webhooks/contact", json=payload)
        assert res1.status_code == 201
        
        # Second call with the same email
        res2 = client.post("/webhooks/contact", json=payload)
        assert res2.status_code == 200
        data = res2.json()
        assert data["status"] == "duplicate"
        
        # Verify the downstream API was strictly only called once
        mock_post.assert_called_once()

def test_downstream_failure(setup_db):
    client = setup_db
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPError("Mocked network error")
        
        payload = {"name": "Charlie", "email": "charlie@example.com", "message": "Broken pipe"}
        response = client.post("/webhooks/contact", json=payload)
        
        assert response.status_code == 502
        assert response.json()["detail"]["status"] == "failed"
        
        # Verify it was logged as a failure in the SQLite DB
        logs = client.get("/sync-log").json()
        assert len(logs) == 1
        assert logs[0]["email"] == "charlie@example.com"
        assert logs[0]["status"] == "failed"
        assert logs[0]["crm_id"] is None

def test_health_endpoint(setup_db):
    response = setup_db.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
