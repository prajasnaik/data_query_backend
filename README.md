# Data Query Backend API

A FastAPI-based backend for CSV file processing, database schema generation, and SQLite database creation.

## Features

- **CSV Upload & Analysis**: Upload CSV files and get detailed metadata, column types, and preview data
- **Schema Generation**: Generate database schemas with support for LLM-based intelligent schema design
- **Database Creation**: Create SQLite databases from CSV data with custom schemas
- **RESTful API**: Clean, well-documented REST API with automatic OpenAPI documentation

## Architecture

This backend is designed to work with a separate frontend application that handles all LLM interactions. The backend focuses on:
- File handling and validation
- Data processing and analysis
- Database creation and management
- Data persistence

## Installation

### Prerequisites
- Python 3.12+
- uv (recommended) or pip

### Setup

1. Clone the repository and navigate to the project directory

2. Install dependencies:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Run the application:
```bash
# Using Python
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Core Endpoints

1. **Upload CSV** - `POST /api/upload-csv`
   - Upload and analyze CSV files
   - Returns file metadata, column types, and preview

2. **Generate Schema** - `POST /api/generate-schema`
   - Generate or validate database schema
   - Supports LLM-generated schemas from frontend

3. **Create Database** - `POST /api/create-database`
   - Create SQLite database from CSV and schema
   - Imports all data from CSV into the database

4. **Health Check** - `GET /health`
   - Check API health status

## API Contract

For detailed API documentation including request/response formats, data types, and integration examples, see [API_CONTRACT.md](./API_CONTRACT.md).

The API contract document includes:
- Complete endpoint specifications
- Request and response schemas
- LLM integration guidelines for frontend
- Example workflows
- Error handling patterns

## Project Structure

```
data_query_backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Application configuration
│   ├── models.py              # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── csv_handler.py     # CSV processing service
│       └── database_service.py # Database creation service
├── uploads/                    # CSV file storage (created at runtime)
├── databases/                  # SQLite databases (created at runtime)
├── main.py                    # FastAPI application
├── pyproject.toml             # Project dependencies
├── API_CONTRACT.md            # Detailed API documentation
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Usage Example

### 1. Upload a CSV file
```bash
curl -X POST "http://localhost:8000/api/upload-csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_data.csv"
```

### 2. Generate schema (with LLM-generated schema from frontend)
```bash
curl -X POST "http://localhost:8000/api/generate-schema" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-file-id",
    "schema": {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
        {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
      ]
    }
  }'
```

### 3. Create database
```bash
curl -X POST "http://localhost:8000/api/create-database" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-file-id",
    "schema": {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
        {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
      ]
    },
    "db_name": "my_database"
  }'
```

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and adjust as needed:

- `APP_NAME`: Application name
- `DEBUG`: Enable debug mode
- `UPLOAD_DIR`: Directory for uploaded CSV files
- `DB_DIR`: Directory for created databases
- `MAX_UPLOAD_SIZE`: Maximum file upload size in bytes
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)

## Development

### Running in Development Mode

```bash
python main.py
```

This starts the server with auto-reload enabled.

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Integration

This backend is designed to work with a frontend that handles LLM interactions. The frontend should:

1. **Upload CSV files** to the backend
2. **Call an LLM API** (OpenAI, Anthropic, Ollama, etc.) to generate intelligent database schemas
3. **Send the LLM-generated schema** back to the backend for validation and database creation
4. **Display results** to the user

See [API_CONTRACT.md](./API_CONTRACT.md) for detailed integration instructions.

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pandas**: Data analysis and CSV processing
- **SQLAlchemy**: SQL toolkit (for future extensions)
- **SQLite**: Lightweight database engine
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server

## Future Enhancements

- [ ] Query execution endpoint for created databases
- [ ] Database export/download endpoint
- [ ] Multiple table support
- [ ] Data validation and cleaning
- [ ] Advanced schema optimization
- [ ] Database migration support
- [ ] User authentication and authorization
- [ ] Rate limiting and caching

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
