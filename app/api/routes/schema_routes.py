"""Routes for database schema generation"""
from fastapi import APIRouter, HTTPException
from app.models import SchemaGenerationRequest, SchemaGenerationResponse
from app.services.csv_handler import CSVHandler
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService
from pathlib import Path

router = APIRouter(prefix="/api", tags=["schema"])

# Initialize services
UPLOAD_DIR = Path("uploads")
DB_DIR = Path("databases")
UPLOAD_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

csv_handler = CSVHandler(upload_dir=UPLOAD_DIR)
db_service = DatabaseService(db_dir=DB_DIR)
llm_service = LLMService()


@router.post("/generate-schema", response_model=SchemaGenerationResponse)
async def generate_schema(request: SchemaGenerationRequest):
    """
    Generate a database schema based on the uploaded CSV.
    
    This endpoint calls an external LLM service to generate an intelligent schema
    based on the CSV structure and sample data.
    
    Args:
        request: SchemaGenerationRequest containing file_id and optional pre-generated schema
        
    Returns:
        SchemaGenerationResponse with the generated schema
    """
    try:
        # Validate that the file exists
        csv_info = csv_handler.get_csv_info(request.file_id)
        if not csv_info:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {request.file_id} not found"
            )
        
        # If schema is already provided (e.g., from cached LLM response), use it
        if request.sql_schema:
            schema = request.sql_schema
        else:
            # Call LLM service to generate schema
            try:
                schema = await llm_service.generate_schema(
                    file_id=request.file_id,
                    filename=csv_info["filename"],
                    columns=csv_info["columns"],
                    sample_data=csv_info["preview"],
                    row_count=csv_info["row_count"],
                )
            except Exception as llm_error:
                # If LLM service fails, fall back to basic schema generation
                print(f"LLM service error: {llm_error}. Using fallback schema generation.")
                schema = db_service.generate_basic_schema(csv_info)
        
        return SchemaGenerationResponse(
            success=True,
            message="Database schema generated successfully",
            file_id=request.file_id,
            sql_schema=schema,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating schema: {str(e)}"
        )
