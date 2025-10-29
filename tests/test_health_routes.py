"""Tests for health check routes"""
import pytest
from datetime import datetime


def test_root_endpoint(client):
    """Test root endpoint returns correct information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Data Query Backend API"
    assert data["version"] == "0.1.0"
    assert "endpoints" in data
    assert "upload_csv" in data["endpoints"]
    assert "generate_schema" in data["endpoints"]
    assert "create_database" in data["endpoints"]


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    # Verify timestamp is valid ISO format
    timestamp = datetime.fromisoformat(data["timestamp"])
    assert isinstance(timestamp, datetime)
