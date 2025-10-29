# API Contract Documentation

This document describes the API contract between the backend and frontend for the Data Query Backend API. The frontend is responsible for all LLM interactions, while the backend handles file processing, database creation, and data management.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Upload CSV File

**Endpoint:** `POST /api/upload-csv`

**Description:** Upload a CSV file for processing. The backend will analyze the file and return metadata including column information, data types, and a preview of the data.

**Request:**
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Body:**
  - `file`: CSV file (required)

**Response:**
```json
{
  "success": true,
  "message": "CSV file uploaded successfully",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "example.csv",
  "row_count": 100,
  "column_count": 5,
  "columns": ["id", "name", "age", "email", "city"],
  "preview": [
    {"id": 1, "name": "John Doe", "age": 30, "email": "john@example.com", "city": "New York"},
    {"id": 2, "name": "Jane Smith", "age": 25, "email": "jane@example.com", "city": "Los Angeles"}
  ],
  "column_types": {
    "id": "INTEGER",
    "name": "TEXT",
    "age": "INTEGER",
    "email": "TEXT",
    "city": "TEXT"
  }
}
```

**Frontend Responsibilities:**
1. Allow user to select and upload a CSV file
2. Display the preview data and column information to the user
3. Store the `file_id` for subsequent API calls

---

### 2. Generate Database Schema

**Endpoint:** `POST /api/generate-schema`

**Description:** Generate a database schema for the uploaded CSV. The frontend can either:
- Send an LLM-generated schema (recommended)
- Let the backend generate a basic schema

**Request:**
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "schema": {
    "table_name": "users",
    "columns": [
      {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
      {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
      {"name": "age", "type": "INTEGER", "constraints": "CHECK(age >= 0)"},
      {"name": "email", "type": "TEXT", "constraints": "UNIQUE NOT NULL"},
      {"name": "city", "type": "TEXT", "constraints": ""}
    ]
  },
  "user_instructions": "Create a users table with proper constraints and indexing"
}
```

**Schema Object Structure:**
- `table_name` (string, required): Name of the table
- `columns` (array, required): List of column definitions
  - Each column object contains:
    - `name` (string): Column name
    - `type` (string): SQL data type (TEXT, INTEGER, REAL, BLOB, DATETIME, BOOLEAN)
    - `constraints` (string): SQL constraints (e.g., "PRIMARY KEY", "NOT NULL", "UNIQUE", "CHECK(...)")

**Response:**
```json
{
  "success": true,
  "message": "Database schema generated successfully",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "schema": {
    "table_name": "users",
    "columns": [
      {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
      {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
      {"name": "age", "type": "INTEGER", "constraints": "CHECK(age >= 0)"},
      {"name": "email", "type": "TEXT", "constraints": "UNIQUE NOT NULL"},
      {"name": "city", "type": "TEXT", "constraints": ""}
    ]
  }
}
```

**Frontend Responsibilities - LLM Integration:**

1. **Prepare LLM Prompt:**
   After receiving the upload response, construct a prompt for your LLM:
   
   ```
   You are a database schema designer. Based on the following CSV data, generate an appropriate SQLite database schema.
   
   CSV Information:
   - Filename: {filename}
   - Columns: {columns}
   - Column Types: {column_types}
   - Sample Data: {preview}
   
   User Instructions: {user_instructions if any}
   
   Generate a schema with:
   1. An appropriate table name (snake_case)
   2. Proper column types (TEXT, INTEGER, REAL, BLOB, DATETIME, BOOLEAN)
   3. Appropriate constraints (PRIMARY KEY, NOT NULL, UNIQUE, CHECK, etc.)
   4. Consider adding indexes for frequently queried columns
   
   Return the schema as a JSON object with this structure:
   {
     "table_name": "table_name",
     "columns": [
       {"name": "column_name", "type": "SQL_TYPE", "constraints": "CONSTRAINTS"}
     ]
   }
   ```

2. **Parse LLM Response:**
   Extract the JSON schema from the LLM response and validate it

3. **Display to User:**
   Show the generated schema to the user for review/editing

4. **Send to Backend:**
   Send the schema to this endpoint for validation and storage

**Fallback Behavior:**
If `schema` is not provided in the request, the backend will generate a basic schema with:
- Table name derived from the filename
- An auto-incrementing `id` column
- All CSV columns with their inferred types
- No additional constraints

---

### 3. Create Database

**Endpoint:** `POST /api/create-database`

**Description:** Create a SQLite database using the provided schema and CSV data.

**Request:**
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "schema": {
    "table_name": "users",
    "columns": [
      {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
      {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
      {"name": "age", "type": "INTEGER", "constraints": "CHECK(age >= 0)"},
      {"name": "email", "type": "TEXT", "constraints": "UNIQUE NOT NULL"},
      {"name": "city", "type": "TEXT", "constraints": ""}
    ]
  },
  "db_name": "users_database"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Database created successfully",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "database_id": "660e8400-e29b-41d4-a716-446655440001",
  "database_path": "databases/users_database.db",
  "table_name": "users",
  "row_count": 100
}
```

**Frontend Responsibilities:**
1. Allow user to review and confirm the schema before database creation
2. Optionally allow user to specify a custom database name
3. Display success message with database information
4. Store `database_id` for future queries

---

### 4. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-28T12:00:00.000000"
}
```

---

### 5. Root Endpoint

**Endpoint:** `GET /`

**Description:** Get API information and available endpoints.

**Response:**
```json
{
  "message": "Data Query Backend API",
  "version": "0.1.0",
  "endpoints": {
    "upload_csv": "/api/upload-csv",
    "generate_schema": "/api/generate-schema",
    "create_database": "/api/create-database",
    "health": "/health"
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

**4xx Client Errors:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**5xx Server Errors:**
```json
{
  "detail": "Error uploading file: {specific error message}"
}
```

**Common Error Codes:**
- `400` - Bad Request (invalid file type, invalid schema, etc.)
- `404` - Not Found (file_id not found)
- `500` - Internal Server Error

---

## Complete Workflow Example

### Step 1: Upload CSV
```bash
curl -X POST "http://localhost:8000/api/upload-csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data.csv"
```

### Step 2: Frontend LLM Schema Generation
```javascript
// Frontend JavaScript example
const uploadResponse = await fetch('http://localhost:8000/api/upload-csv', {
  method: 'POST',
  body: formData
});
const uploadData = await uploadResponse.json();

// Call your LLM API (OpenAI, Anthropic, Ollama, etc.)
const llmPrompt = `Generate a database schema for this CSV:
Columns: ${JSON.stringify(uploadData.columns)}
Types: ${JSON.stringify(uploadData.column_types)}
Preview: ${JSON.stringify(uploadData.preview)}`;

const llmResponse = await callYourLLMAPI(llmPrompt);
const schema = JSON.parse(llmResponse.content);
```

### Step 3: Generate Schema with LLM Result
```bash
curl -X POST "http://localhost:8000/api/generate-schema" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "schema": {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
        {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
      ]
    }
  }'
```

### Step 4: Create Database
```bash
curl -X POST "http://localhost:8000/api/create-database" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "schema": {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
        {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
      ]
    },
    "db_name": "my_users_db"
  }'
```

---

## Data Types

### Supported SQL Data Types
- `TEXT` - String/text data
- `INTEGER` - Whole numbers
- `REAL` - Floating point numbers
- `BLOB` - Binary data
- `DATETIME` - Date and time values
- `BOOLEAN` - True/false values

### Common Constraints
- `PRIMARY KEY` - Unique identifier for the row
- `AUTOINCREMENT` - Auto-incrementing integer (use with PRIMARY KEY)
- `NOT NULL` - Column cannot contain NULL values
- `UNIQUE` - All values in column must be unique
- `CHECK(condition)` - Values must satisfy a condition
- `DEFAULT value` - Default value if none provided
- `FOREIGN KEY` - Reference to another table

---

## Notes for Frontend Developers

1. **File Upload:**
   - Use `FormData` to upload CSV files
   - Maximum file size: 100MB (configurable)
   - Only CSV files are accepted

2. **LLM Integration:**
   - The frontend is responsible for ALL LLM calls
   - The backend does not have LLM capabilities
   - Parse LLM responses carefully to extract valid JSON schema
   - Validate schema structure before sending to backend

3. **Schema Validation:**
   - Ensure table names use snake_case and contain only alphanumeric characters and underscores
   - Ensure column names match this pattern as well
   - Verify all required fields are present in the schema

4. **Error Handling:**
   - Always check response status codes
   - Display user-friendly error messages
   - Handle network errors gracefully

5. **CORS:**
   - Currently configured to allow all origins (development)
   - Update for production deployment

---

## Running the Backend

```bash
# Install dependencies
uv sync

# Run the server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`
