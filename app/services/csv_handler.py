"""CSV handling service"""
import os
import uuid
import pandas as pd
from pathlib import Path
from fastapi import UploadFile
from typing import Dict, Any, Optional
import json


class CSVHandler:
    """Service for handling CSV file uploads and processing"""
    
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(exist_ok=True)
        self.metadata_file = self.upload_dir / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata from file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    async def save_csv(self, file: UploadFile) -> Dict[str, Any]:
        """
        Save uploaded CSV file and extract metadata
        
        Args:
            file: Uploaded CSV file
            
        Returns:
            Dictionary containing file metadata and preview
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_path = self.upload_dir / f"{file_id}.csv"
        content = await file.read()
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Read and analyze CSV
        df = pd.read_csv(file_path)
        
        # Get column types
        column_types = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            # Map pandas dtypes to SQL-like types
            if dtype.startswith('int'):
                column_types[col] = 'INTEGER'
            elif dtype.startswith('float'):
                column_types[col] = 'REAL'
            elif dtype.startswith('datetime'):
                column_types[col] = 'DATETIME'
            elif dtype.startswith('bool'):
                column_types[col] = 'BOOLEAN'
            else:
                column_types[col] = 'TEXT'
        
        # Create preview (first 5 rows)
        preview = df.head(5).to_dict('records')
        
        # Store metadata
        metadata = {
            'file_id': file_id,
            'filename': file.filename,
            'file_path': str(file_path),
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'column_types': column_types,
            'preview': preview,
        }
        # Backwards compatible key for older metadata readers
        metadata['filepath'] = metadata['file_path']
        
        self.metadata[file_id] = metadata
        self._save_metadata()
        
        return {
            'file_id': file_id,
            'filename': file.filename,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'preview': preview,
            'column_types': column_types,
        }
    
    def get_csv_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific CSV file
        
        Args:
            file_id: ID of the file
            
        Returns:
            Metadata dictionary or None if not found
        """
        self._load_metadata()
        return self.metadata.get(file_id)
    
    def get_dataframe(self, file_id: str) -> Optional[pd.DataFrame]:
        """
        Load CSV file as pandas DataFrame
        
        Args:
            file_id: ID of the file
            
        Returns:
            DataFrame or None if not found
        """
        info = self.get_csv_info(file_id)
        if not info:
            return None

        file_path = info.get('file_path') or info.get('filepath')
        if not file_path:
            return None

        return pd.read_csv(file_path)
