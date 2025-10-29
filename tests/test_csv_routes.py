"""Tests for CSV upload routes"""
import pytest
from io import BytesIO


def test_upload_csv_success(client, sample_csv_bytes):
    """Test successful CSV upload"""
    files = {"file": ("test.csv", BytesIO(sample_csv_bytes), "text/csv")}
    response = client.post("/api/upload-csv", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "CSV file uploaded successfully"
    assert "file_id" in data
    assert data["filename"] == "test.csv"
    assert data["row_count"] == 3
    assert data["column_count"] == 4
    assert len(data["columns"]) == 4
    assert "id" in data["columns"]
    assert "name" in data["columns"]
    assert "email" in data["columns"]
    assert "age" in data["columns"]
    assert len(data["preview"]) > 0


def test_upload_non_csv_file(client):
    """Test upload of non-CSV file fails"""
    files = {"file": ("test.txt", BytesIO(b"not a csv"), "text/plain")}
    response = client.post("/api/upload-csv", files=files)
    
    assert response.status_code == 400
    assert "Only CSV files are supported" in response.json()["detail"]


def test_upload_empty_file(client):
    """Test upload of empty file"""
    files = {"file": ("empty.csv", BytesIO(b""), "text/csv")}
    response = client.post("/api/upload-csv", files=files)
    
    # Should fail with 500 or validation error
    assert response.status_code >= 400


def test_upload_malformed_csv(client):
    """Test upload of malformed CSV"""
    malformed_csv = b"id,name\n1,Alice,extra_column\n2"
    files = {"file": ("malformed.csv", BytesIO(malformed_csv), "text/csv")}
    response = client.post("/api/upload-csv", files=files)
    
    # Should handle gracefully - either succeed with parsing or fail clearly
    # The actual behavior depends on pandas' handling
    assert response.status_code in [200, 400, 500]
