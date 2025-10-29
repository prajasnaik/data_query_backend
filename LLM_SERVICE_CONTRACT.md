# LLM Service Contract

This document describes the contract between the FastAPI backend and the external LLM service (e.g., Next.js frontend with Vercel AI SDK).

## Overview

The FastAPI backend expects an external LLM service to generate intelligent database schemas based on CSV file analysis. The LLM service should analyze column names, data types, sample values, and infer appropriate SQL schema definitions.

## LLM Service Endpoint

### Endpoint URL
```
POST /api/generate-schema
```

Configure this URL in your `.env` file:
```bash
LLM_SERVICE_URL=http://localhost:3000/api/generate-schema
LLM_SERVICE_TIMEOUT=60
```

---

## Request Format

### HTTP Method
`POST`

### Headers
```
Content-Type: application/json
```

### Request Body

```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sales_data.csv",
  "row_count": 1500,
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "sample_values": ["1", "2", "3", "4", "5"]
    },
    {
      "name": "customer_name",
      "type": "string",
      "sample_values": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown"]
    },
    {
      "name": "email",
      "type": "string",
      "sample_values": ["john@example.com", "jane@example.com", "bob@example.com", "alice@example.com", "charlie@example.com"]
    },
    {
      "name": "purchase_date",
      "type": "datetime",
      "sample_values": ["2024-01-15", "2024-02-20", "2024-03-10", "2024-04-05", "2024-05-12"]
    },
    {
      "name": "amount",
      "type": "float",
      "sample_values": ["99.99", "149.50", "29.99", "199.00", "89.95"]
    },
    {
      "name": "status",
      "type": "string",
      "sample_values": ["completed", "pending", "completed", "shipped", "completed"]
    }
  ],
  "sample_data": [
    {
      "id": "1",
      "customer_name": "John Doe",
      "email": "john@example.com",
      "purchase_date": "2024-01-15",
      "amount": "99.99",
      "status": "completed"
    },
    {
      "id": "2",
      "customer_name": "Jane Smith",
      "email": "jane@example.com",
      "purchase_date": "2024-02-20",
      "amount": "149.50",
      "status": "pending"
    }
  ]
}
```

### Request Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `file_id` | string (UUID) | Unique identifier for the uploaded CSV file |
| `filename` | string | Original filename of the CSV |
| `row_count` | integer | Total number of rows in the CSV file |
| `columns` | array | List of column definitions with inferred types and sample values |
| `columns[].name` | string | Column name from CSV header |
| `columns[].type` | string | Inferred data type: `integer`, `float`, `string`, `datetime`, `boolean` |
| `columns[].sample_values` | array[string] | First 5 unique values from this column |
| `sample_data` | array | First 2-5 complete rows from the CSV as preview |

---

## Response Format

### Success Response (200 OK)

```json
{
  "schema": "CREATE TABLE sales_data (\n    id INTEGER PRIMARY KEY,\n    customer_name TEXT NOT NULL,\n    email TEXT UNIQUE,\n    purchase_date DATE NOT NULL,\n    amount DECIMAL(10, 2) NOT NULL,\n    status TEXT CHECK(status IN ('pending', 'completed', 'shipped', 'cancelled')),\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);"
}
```

**Alternative key names accepted:**
```json
{
  "sql": "CREATE TABLE sales_data (...)"
}
```

### Response Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `schema` or `sql` | string | Complete SQL DDL statement(s) for creating the database schema |

---

## Schema Generation Requirements

The LLM should generate SQL DDL that:

### 1. **Uses SQLite-compatible syntax**
   - SQLite is the database engine used by the backend
   - Use standard SQLite data types: `INTEGER`, `REAL`, `TEXT`, `BLOB`, `DATE`, `DATETIME`, `TIMESTAMP`

### 2. **Infers appropriate constraints**
   - `PRIMARY KEY`: Identify unique identifier columns (usually named `id`, `uuid`, etc.)
   - `NOT NULL`: Mark essential fields based on context
   - `UNIQUE`: Identify unique fields (emails, usernames, codes)
   - `CHECK`: Add value constraints for enumerated types
   - `DEFAULT`: Add sensible defaults (timestamps, status values)

### 3. **Derives intelligent table names**
   - Base table name on the filename (remove `.csv` extension)
   - Use singular form: `users`, `products`, `transactions`
   - Use snake_case: `sales_data`, `customer_orders`

### 4. **Maps data types intelligently**
   
   | Inferred Type | SQLite Type | Notes |
   |--------------|-------------|-------|
   | `integer` | `INTEGER` | Whole numbers |
   | `float` | `REAL` | Decimals, prices, percentages |
   | `string` | `TEXT` | Text, names, descriptions |
   | `datetime` | `DATETIME` or `DATE` | Dates and timestamps |
   | `boolean` | `INTEGER` | 0 or 1 in SQLite |

### 5. **Add metadata columns (optional but recommended)**
   ```sql
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   ```

### 6. **Return valid, executable SQL**
   - The backend will execute this SQL directly
   - Ensure proper syntax and formatting
   - Support multi-statement schemas if needed (separated by semicolons)

---

## Error Handling

### Error Response (4xx, 5xx)

```json
{
  "error": "LLM generation failed",
  "detail": "The AI model encountered an error while analyzing the data structure",
  "code": "LLM_ERROR"
}
```

### Timeout Behavior
- The backend will wait up to 60 seconds (configurable) for the LLM response
- If timeout occurs, the backend will fall back to a basic schema generation

### Fallback Strategy
If the LLM service is unavailable or fails:
1. Backend generates a basic schema using simple type inference
2. All columns become `TEXT` type except obvious numbers
3. First column becomes `PRIMARY KEY` if it looks like an ID

---

## Example LLM Prompts

### Recommended System Prompt
```
You are a database schema expert. Given CSV data with column names, types, and sample values, 
generate an optimal SQLite database schema. Analyze the data to:
- Infer appropriate data types and constraints
- Identify primary keys and unique fields
- Add CHECK constraints for enumerated values
- Suggest indexes for commonly queried fields
- Use semantic column naming conventions

Return only valid SQLite DDL (CREATE TABLE statement) without any explanation or markdown formatting.
```

### Example User Prompt
```
Generate a SQLite schema for a CSV file named "sales_data.csv" with 1500 rows and the following structure:

Columns:
- id (integer): 1, 2, 3, 4, 5
- customer_name (string): John Doe, Jane Smith, Bob Johnson, ...
- email (string): john@example.com, jane@example.com, ...
- purchase_date (datetime): 2024-01-15, 2024-02-20, ...
- amount (float): 99.99, 149.50, 29.99, ...
- status (string): completed, pending, shipped, ...

Sample data:
Row 1: {"id": "1", "customer_name": "John Doe", "email": "john@example.com", ...}
Row 2: {"id": "2", "customer_name": "Jane Smith", "email": "jane@example.com", ...}

Generate the CREATE TABLE statement.
```

---

## Implementation Examples

### Using Vercel AI SDK (Next.js)

```typescript
// app/api/generate-schema/route.ts
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

export async function POST(req: Request) {
  const { file_id, filename, columns, sample_data, row_count } = await req.json();
  
  const prompt = `Generate a SQLite schema for a CSV file named "${filename}" with ${row_count} rows.
  
Columns: ${JSON.stringify(columns, null, 2)}
Sample data: ${JSON.stringify(sample_data, null, 2)}

Return only the CREATE TABLE statement without any markdown or explanation.`;

  try {
    const { text } = await generateText({
      model: openai('gpt-4-turbo'),
      prompt,
      system: 'You are a database schema expert. Generate only valid SQLite DDL statements.',
    });
    
    return Response.json({ schema: text });
  } catch (error) {
    return Response.json(
      { error: 'Schema generation failed', detail: error.message },
      { status: 500 }
    );
  }
}
```

### Using Ollama (Local LLM)

```typescript
// app/api/generate-schema/route.ts
export async function POST(req: Request) {
  const { file_id, filename, columns, sample_data, row_count } = await req.json();
  
  const prompt = `Generate a SQLite schema for "${filename}"...`;
  
  const response = await fetch('http://localhost:11434/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llama2',
      prompt,
      stream: false,
    }),
  });
  
  const data = await response.json();
  return Response.json({ schema: data.response });
}
```

---

## Testing the Contract

### Test Request (curl)
```bash
curl -X POST http://localhost:3000/api/generate-schema \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "test-123",
    "filename": "test.csv",
    "row_count": 10,
    "columns": [
      {"name": "id", "type": "integer", "sample_values": ["1", "2", "3"]},
      {"name": "name", "type": "string", "sample_values": ["Alice", "Bob", "Charlie"]}
    ],
    "sample_data": [{"id": "1", "name": "Alice"}]
  }'
```

### Expected Response
```json
{
  "schema": "CREATE TABLE test (\n    id INTEGER PRIMARY KEY,\n    name TEXT NOT NULL\n);"
}
```

---

## Summary

**Backend sends:**
- File metadata (ID, name, row count)
- Column definitions with inferred types
- Sample values and preview data

**LLM service returns:**
- Valid SQLite CREATE TABLE statement(s)
- Intelligent constraints and data types
- Properly formatted SQL DDL

The backend will execute this SQL to create the database and import the CSV data.
