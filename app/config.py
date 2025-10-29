"""Configuration settings for the application"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Application settings
    app_name: str = "Data Query Backend"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Directory settings
    upload_dir: Path = Path("uploads")
    db_dir: Path = Path("databases")
    
    # File settings
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: list = [".csv"]
    
    # CORS settings
    allowed_origins: list = ["*"]
    
    # LLM Service settings
    llm_service_url: str = "http://localhost:3000/api/generate-schema"
    llm_service_timeout: int = 60


settings = Settings()
