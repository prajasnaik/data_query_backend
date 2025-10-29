"""Tests for database creation routes"""
import pytest
from io import BytesIO
from pathlib import Path


@pytest.fixture
def uploaded_file_and_schema(client, sample_csv_bytes):
    """Upload a CSV file and generate schema"""
    # Upload CSV
    files = {"file": ("test.csv", BytesIO(sample_csv_bytes), "text/csv")}
    upload_response = client.post("/api/upload-csv", files=files)
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]
    
    # Generate schema
    schema_response = client.post(
        "/api/generate-schema",
        json={"file_id": file_id}
    )
    assert schema_response.status_code == 200
    schema = schema_response.json()["sql_schema"]
    
    return {"file_id": file_id, "schema": schema}


def test_create_database_success(client, uploaded_file_and_schema):
    """Test successful database creation"""
    response = client.post(
        "/api/create-database",
        json={
            "file_id": uploaded_file_and_schema["file_id"],
            "sql_schema": uploaded_file_and_schema["schema"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Database created successfully"
    assert data["file_id"] == uploaded_file_and_schema["file_id"]
    assert "database_id" in data
    assert "database_path" in data
    assert "table_name" in data
    assert data["row_count"] == 3
    
    # Verify database file was created
    db_path = Path(data["database_path"])
    assert db_path.exists()
    assert db_path.suffix == ".db"


def test_create_database_with_custom_name(client, uploaded_file_and_schema):
    """Test database creation with custom name"""
    custom_name = "my_custom_database"
    response = client.post(
        "/api/create-database",
        json={
            "file_id": uploaded_file_and_schema["file_id"],
            "sql_schema": uploaded_file_and_schema["schema"],
            "db_name": custom_name
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert custom_name in data["database_path"]


def test_create_database_file_not_found(client):
    """Test database creation with non-existent file ID"""
    response = client.post(
        "/api/create-database",
        json={
            "file_id": "non-existent-id",
            "sql_schema": "CREATE TABLE test (id INTEGER);"
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_database_invalid_schema(client, sample_csv_bytes):
    """Test database creation with invalid SQL schema"""
    # Upload CSV first
    files = {"file": ("test.csv", BytesIO(sample_csv_bytes), "text/csv")}
    upload_response = client.post("/api/upload-csv", files=files)
    file_id = upload_response.json()["file_id"]
    
    # Try to create database with invalid schema
    response = client.post(
        "/api/create-database",
        json={
            "file_id": file_id,
            "sql_schema": "INVALID SQL STATEMENT"
        }
    )
    
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()
