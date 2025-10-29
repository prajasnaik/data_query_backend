"""Dependency injection for API routes"""
from functools import lru_cache
from pathlib import Path
from app.services.csv_handler import CSVHandler
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService


# Singleton instances
_csv_handler = None
_db_service = None
_llm_service = None


def get_csv_handler() -> CSVHandler:
    """Get CSV handler singleton"""
    global _csv_handler
    if _csv_handler is None:
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        _csv_handler = CSVHandler(upload_dir=upload_dir)
    return _csv_handler


def get_db_service() -> DatabaseService:
    """Get database service singleton"""
    global _db_service
    if _db_service is None:
        db_dir = Path("databases")
        db_dir.mkdir(exist_ok=True)
        _db_service = DatabaseService(db_dir=db_dir)
    return _db_service


def get_llm_service() -> LLMService:
    """Get LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
