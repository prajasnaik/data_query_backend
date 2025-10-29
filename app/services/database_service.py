"""Database service for creating and managing SQLite databases"""
import os
import uuid
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import json
import re


class DatabaseService:
    """Service for creating and managing SQLite databases"""
    
    def __init__(self, db_dir: Path):
        self.db_dir = db_dir
        self.db_dir.mkdir(exist_ok=True)
        self.metadata_file = self.db_dir / "db_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load database metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save database metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def generate_basic_schema(self, csv_info: Dict[str, Any]) -> str:
        """
        Generate a basic SQL schema from CSV metadata
        
        Args:
            csv_info: CSV file metadata
            
        Returns:
            SQL CREATE TABLE statement
        """
        # Use filename (without extension) as table name
        table_name = Path(csv_info['filename']).stem.replace(' ', '_').replace('-', '_')
        
        # Build columns
        columns = []
        columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        
        # Add columns from CSV
        for col_name, col_type in csv_info['column_types'].items():
            # Clean column name (replace spaces with underscores)
            clean_name = col_name.replace(' ', '_').replace('-', '_')
            
            # Map pandas types to SQLite types
            if col_type.lower() in ['int64', 'integer']:
                sql_type = "INTEGER"
            elif col_type.lower() in ['float64', 'float']:
                sql_type = "REAL"
            else:
                sql_type = "TEXT"
            
            columns.append(f"{clean_name} {sql_type}")
        
        # Build CREATE TABLE statement
        columns_sql = ",\n    ".join(columns)
        schema = f"CREATE TABLE {table_name} (\n    {columns_sql}\n);"
        
        return schema
    
    def create_database(
        self,
        file_id: str,
        csv_info: Dict[str, Any],
        schema: str,
        db_name: str = None
    ) -> Dict[str, Any]:
        """
        Create a SQLite database from CSV data and schema
        
        Args:
            file_id: ID of the CSV file
            csv_info: CSV file metadata
            schema: SQL CREATE TABLE statement
            db_name: Optional custom database name
            
        Returns:
            Dictionary containing database information
        """
        # Generate database ID and path
        db_id = str(uuid.uuid4())
        if db_name:
            db_filename = f"{db_name}.db"
        else:
            db_filename = f"{file_id}.db"
        
        db_path = self.db_dir / db_filename
        
        # Extract table name from schema
        table_name = self._extract_table_name(schema)
        
        try:
            # Create database and execute schema
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Execute the schema (CREATE TABLE statement)
            cursor.execute(schema)
            
            # Load CSV data
            file_path = csv_info.get('file_path') or csv_info.get('filepath')
            if not file_path:
                raise KeyError("CSV metadata missing 'file_path'")
            csv_path = Path(file_path)
            df = pd.read_csv(csv_path)
            
            # Insert data into table
            df.to_sql(table_name, conn, if_exists='append', index=False)
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            # Save metadata
            self.metadata[db_id] = {
                "database_id": db_id,
                "file_id": file_id,
                "database_path": str(db_path),
                "table_name": table_name,
                "row_count": row_count,
            }
            self._save_metadata()
            
            return {
                "database_id": db_id,
                "database_path": str(db_path),
                "table_name": table_name,
                "row_count": row_count,
            }
            
        except Exception as e:
            # Clean up on error
            if db_path.exists():
                db_path.unlink()
            raise Exception(f"Error creating database: {str(e)}")
    
    def _extract_table_name(self, schema: str) -> str:
        """Extract table name from CREATE TABLE statement"""
        # Match CREATE TABLE table_name
        match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)', schema, re.IGNORECASE)
        if match:
            return match.group(1).strip('`"[]')
        raise ValueError("Could not extract table name from schema")
    
    def get_database_info(self, db_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific database
        
        Args:
            db_id: Database ID
            
        Returns:
            Database metadata
        """
        return self.metadata.get(db_id)
