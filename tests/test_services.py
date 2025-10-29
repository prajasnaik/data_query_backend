"""Tests for service layer"""
import pytest
from pathlib import Path
from app.services.csv_handler import CSVHandler
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService
from unittest.mock import AsyncMock, patch
import httpx


def test_csv_handler_initialization(test_upload_dir):
    """Test CSV handler initialization"""
    handler = CSVHandler(upload_dir=test_upload_dir)
    assert handler.upload_dir == test_upload_dir
    assert test_upload_dir.exists()


def test_database_service_initialization(test_db_dir):
    """Test database service initialization"""
    service = DatabaseService(db_dir=test_db_dir)
    assert service.db_dir == test_db_dir
    assert test_db_dir.exists()


def test_llm_service_initialization():
    """Test LLM service initialization"""
    service = LLMService()
    assert service.llm_url is not None
    assert service.timeout > 0


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_llm_service_generate_schema_success(mock_client_class):
    """Test LLM service schema generation success"""
    # Create mock client instance
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {"schema": "CREATE TABLE test (id INTEGER);"}
    mock_response.raise_for_status = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = AsyncMock()
    mock_client_class.return_value = mock_client
    
    service = LLMService()
    schema = await service.generate_schema(
        file_id="test-id",
        filename="test.csv",
        columns=[{"name": "id", "type": "integer", "sample_values": ["1", "2"]}],
        sample_data=[{"id": "1"}],
        row_count=10
    )
    
    assert schema == "CREATE TABLE test (id INTEGER);"
    assert mock_client.post.called


@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_llm_service_generate_schema_timeout(mock_post):
    """Test LLM service handles timeout"""
    # Mock timeout
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    
    service = LLMService()
    with pytest.raises(Exception) as exc_info:
        await service.generate_schema(
            file_id="test-id",
            filename="test.csv",
            columns=[],
            sample_data=[],
            row_count=10
        )
    
    assert "timeout" in str(exc_info.value).lower()


@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_llm_service_generate_schema_http_error(mock_post):
    """Test LLM service handles HTTP errors"""
    # Mock HTTP error
    mock_post.side_effect = httpx.HTTPError("Server error")
    
    service = LLMService()
    with pytest.raises(Exception) as exc_info:
        await service.generate_schema(
            file_id="test-id",
            filename="test.csv",
            columns=[],
            sample_data=[],
            row_count=10
        )
    
    assert "error" in str(exc_info.value).lower()
