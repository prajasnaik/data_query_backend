"""Routes for database creation and management"""
from fastapi import APIRouter, HTTPException
from app.models import DatabaseCreationRequest, DatabaseCreationResponse
from app.services.csv_handler import CSVHandler
from app.services.database_service import DatabaseService
from pathlib import Path

router = APIRouter(prefix="/api", tags=["database"])

# Initialize services
UPLOAD_DIR = Path("uploads")
DB_DIR = Path("databases")
UPLOAD_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

csv_handler = CSVHandler(upload_dir=UPLOAD_DIR)
db_service = DatabaseService(db_dir=DB_DIR)


@router.post("/create-database", response_model=DatabaseCreationResponse)
async def create_database(request: DatabaseCreationRequest):
    """
    Create a SQLite database using the provided schema and CSV data.
    
    Args:
        request: DatabaseCreationRequest containing file_id, schema, and optional db_name
        
    Returns:
        DatabaseCreationResponse with database file path and metadata
    """
    try:
        # Validate that the file exists
        csv_info = csv_handler.get_csv_info(request.file_id)
        if not csv_info:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {request.file_id} not found"
            )
        
        # Create database from CSV and schema
        result = db_service.create_database(
            file_id=request.file_id,
            csv_info=csv_info,
            schema=request.sql_schema,
            db_name=request.db_name,
        )
        
        return DatabaseCreationResponse(
            success=True,
            message="Database created successfully",
            file_id=request.file_id,
            database_id=result["database_id"],
            database_path=result["database_path"],
            table_name=result["table_name"],
            row_count=result["row_count"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating database: {str(e)}"
        )
