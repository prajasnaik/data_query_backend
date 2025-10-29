"""Service for interacting with external LLM API"""
import httpx
from typing import Dict, Any, List
from app.config import settings


class LLMService:
    """Service to call external LLM API for schema generation"""
    
    def __init__(self):
        self.llm_url = settings.llm_service_url
        self.timeout = settings.llm_service_timeout
    
    async def generate_schema(
        self,
        file_id: str,
        filename: str,
        columns: List[Dict[str, Any]],
        sample_data: List[Dict[str, Any]],
        row_count: int,
    ) -> str:
        """
        Call external LLM service to generate database schema.
        
        Args:
            file_id: Unique identifier for the uploaded file
            filename: Original filename
            columns: List of column definitions with types and sample values
            sample_data: Preview rows from the CSV
            row_count: Total number of rows in the CSV
            
        Returns:
            SQL schema string (CREATE TABLE statement)
        """
        payload = {
            "file_id": file_id,
            "filename": filename,
            "columns": columns,
            "sample_data": sample_data,
            "row_count": row_count,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.llm_url,
                    json=payload,
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract schema from response
                # Expected format: {"schema": "CREATE TABLE ..."}
                if "schema" in result:
                    return result["schema"]
                elif "sql" in result:
                    return result["sql"]
                else:
                    raise ValueError(f"Unexpected response format from LLM service: {result}")
                    
        except httpx.TimeoutException:
            raise Exception(f"LLM service timeout after {self.timeout} seconds")
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error calling LLM service: {str(e)}")
        except Exception as e:
            raise Exception(f"Error calling LLM service: {str(e)}")
