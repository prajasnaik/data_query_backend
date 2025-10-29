"""Tests for schema generation routes"""
import pytest
from io import BytesIO
from unittest.mock import patch, AsyncMock


@pytest.fixture
def uploaded_file_id(client, sample_csv_bytes):
    """Upload a CSV file and return its file_id"""
    files = {"file": ("test.csv", BytesIO(sample_csv_bytes), "text/csv")}
    response = client.post("/api/upload-csv", files=files)
    assert response.status_code == 200
    return response.json()["file_id"]


def test_generate_schema_file_not_found(client):
    """Test schema generation with non-existent file ID"""
    response = client.post(
        "/api/generate-schema",
        json={"file_id": "non-existent-id"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_generate_schema_with_provided_schema(client, uploaded_file_id):
    """Test schema generation when schema is provided"""
    schema = "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);"
    response = client.post(
        "/api/generate-schema",
        json={
            "file_id": uploaded_file_id,
            "sql_schema": schema
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["file_id"] == uploaded_file_id
    assert "sql_schema" in data
    assert "CREATE TABLE" in data["sql_schema"]


@patch('app.services.llm_service.LLMService.generate_schema')
async def test_generate_schema_with_llm_success(mock_llm, client, uploaded_file_id):
    """Test schema generation using LLM service"""
    # Mock LLM response
    mock_schema = "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, age INTEGER);"
    mock_llm.return_value = mock_schema
    
    response = client.post(
        "/api/generate-schema",
        json={"file_id": uploaded_file_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["file_id"] == uploaded_file_id
    assert "sql_schema" in data


@patch('app.services.llm_service.LLMService.generate_schema')
async def test_generate_schema_llm_failure_fallback(mock_llm, client, uploaded_file_id):
    """Test schema generation falls back when LLM fails"""
    # Mock LLM failure
    mock_llm.side_effect = Exception("LLM service unavailable")
    
    response = client.post(
        "/api/generate-schema",
        json={"file_id": uploaded_file_id}
    )
    
    # Should still succeed with fallback schema
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "sql_schema" in data
    assert "CREATE TABLE" in data["sql_schema"]
