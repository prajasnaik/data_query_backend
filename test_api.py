"""
Simple test script to verify the API is working correctly.
Run this after starting the server with: python main.py
"""
import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_upload_csv():
    """Test CSV upload"""
    print("\n=== Testing CSV Upload ===")
    
    # Check if test file exists
    test_file = Path("test_data.csv")
    if not test_file.exists():
        print("❌ test_data.csv not found!")
        return None
    
    with open(test_file, 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/upload-csv", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ File uploaded successfully!")
        print(f"File ID: {data['file_id']}")
        print(f"Columns: {data['columns']}")
        print(f"Rows: {data['row_count']}")
        print(f"Preview: {json.dumps(data['preview'][:2], indent=2)}")
        return data['file_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None


def test_generate_schema(file_id):
    """Test schema generation"""
    print("\n=== Testing Schema Generation ===")
    
    # Test with custom LLM-like schema
    schema = {
        "table_name": "users",
        "columns": [
            {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY"},
            {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
            {"name": "age", "type": "INTEGER", "constraints": "CHECK(age >= 0)"},
            {"name": "email", "type": "TEXT", "constraints": "UNIQUE NOT NULL"},
            {"name": "city", "type": "TEXT", "constraints": ""}
        ]
    }
    
    payload = {
        "file_id": file_id,
        "schema": schema
    }
    
    response = requests.post(f"{BASE_URL}/api/generate-schema", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Schema generated successfully!")
        print(f"Table: {data['schema']['table_name']}")
        print(f"Columns: {len(data['schema']['columns'])}")
        return data['schema']
    else:
        print(f"❌ Schema generation failed: {response.text}")
        return None


def test_create_database(file_id, schema):
    """Test database creation"""
    print("\n=== Testing Database Creation ===")
    
    payload = {
        "file_id": file_id,
        "schema": schema,
        "db_name": "test_users"
    }
    
    response = requests.post(f"{BASE_URL}/api/create-database", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Database created successfully!")
        print(f"Database ID: {data['database_id']}")
        print(f"Database Path: {data['database_path']}")
        print(f"Table: {data['table_name']}")
        print(f"Rows inserted: {data['row_count']}")
        return True
    else:
        print(f"❌ Database creation failed: {response.text}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Data Query Backend API - Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        if not test_health_check():
            print("\n❌ Health check failed. Is the server running?")
            return
        
        # Test 2: Upload CSV
        file_id = test_upload_csv()
        if not file_id:
            print("\n❌ CSV upload failed. Cannot continue tests.")
            return
        
        # Test 3: Generate schema
        schema = test_generate_schema(file_id)
        if not schema:
            print("\n❌ Schema generation failed. Cannot continue tests.")
            return
        
        # Test 4: Create database
        if test_create_database(file_id, schema):
            print("\n" + "=" * 50)
            print("✅ All tests passed successfully!")
            print("=" * 50)
        else:
            print("\n❌ Some tests failed.")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the server.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
