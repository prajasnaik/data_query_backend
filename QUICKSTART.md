# Quick Start Guide

## 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

## 2. Start the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

## 3. Test the API

Open a new terminal and run:

```bash
python test_api.py
```

This will run a complete test suite that:
1. Checks if the API is healthy
2. Uploads a test CSV file
3. Generates a database schema
4. Creates a SQLite database

## 4. Explore the API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 5. Manual Testing with curl

### Upload a CSV file
```bash
curl -X POST "http://localhost:8000/api/upload-csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_data.csv"
```

### Generate schema
```bash
curl -X POST "http://localhost:8000/api/generate-schema" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "YOUR_FILE_ID_HERE",
    "schema": {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"},
        {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
      ]
    }
  }'
```

### Create database
```bash
curl -X POST "http://localhost:8000/api/create-database" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "YOUR_FILE_ID_HERE",
    "schema": {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"},
        {"name": "name", "type": "TEXT", "constraints": "NOT NULL"}
      ]
    },
    "db_name": "my_test_db"
  }'
```

## 6. Check Created Files

After testing, you'll see:
- `uploads/` - Contains uploaded CSV files and metadata
- `databases/` - Contains created SQLite databases

You can inspect the databases with:
```bash
sqlite3 databases/your_database.db
```

Then run SQL queries:
```sql
.tables
SELECT * FROM users;
.quit
```

## Next Steps

1. Read the [API_CONTRACT.md](./API_CONTRACT.md) for detailed API documentation
2. Integrate with your frontend application
3. Configure your LLM to generate schemas based on the guidelines in API_CONTRACT.md

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Verify Python version is 3.12+
- Make sure all dependencies are installed

### Upload fails
- Check file size (max 100MB by default)
- Ensure the file is a valid CSV
- Check server logs for detailed error messages

### Database creation fails
- Verify the schema structure is correct
- Check that the file_id exists
- Ensure column names in schema match CSV columns (with underscores instead of spaces)
