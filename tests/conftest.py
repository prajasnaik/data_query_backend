"""Pytest configuration and fixtures"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from main import app
import shutil
import tempfile


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def test_upload_dir():
    """Create temporary upload directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup after test
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_db_dir():
    """Create temporary database directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup after test
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_csv_file(test_upload_dir):
    """Create a sample CSV file for testing"""
    csv_content = """id,name,email,age
1,Alice,alice@example.com,30
2,Bob,bob@example.com,25
3,Charlie,charlie@example.com,35
"""
    csv_path = test_upload_dir / "test.csv"
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_csv_bytes():
    """Sample CSV file as bytes for upload testing"""
    csv_content = """id,name,email,age
1,Alice,alice@example.com,30
2,Bob,bob@example.com,25
3,Charlie,charlie@example.com,35
"""
    return csv_content.encode('utf-8')
