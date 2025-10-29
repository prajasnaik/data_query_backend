"""Routes for CSV file operations"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import UploadResponse
from app.services.csv_handler import CSVHandler
from pathlib import Path

router = APIRouter(prefix="/api", tags=["csv"])

# Initialize CSV handler
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
csv_handler = CSVHandler(upload_dir=UPLOAD_DIR)


@router.post("/upload-csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file for processing.
    
    Args:
        file: CSV file to upload
        
    Returns:
        UploadResponse with file_id, preview data, and metadata
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported"
            )
        
        # Save and process the file
        result = await csv_handler.save_csv(file)
        
        return UploadResponse(
            success=True,
            message="CSV file uploaded successfully",
            file_id=result["file_id"],
            filename=result["filename"],
            row_count=result["row_count"],
            column_count=result["column_count"],
            columns=result["columns"],
            preview=result["preview"],
            column_types=result["column_types"],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
