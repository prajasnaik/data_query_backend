# Software Requirements Specification (SRS)
## Intelligent Data Query Agent Platform

**Version:** 1.0  
**Date:** October 28, 2025  
**Project Name:** Data Query Agent  
**Document Type:** Software Requirements Specification

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Current System Analysis](#3-current-system-analysis)
4. [Proposed System Architecture](#4-proposed-system-architecture)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Technical Stack](#7-technical-stack)
8. [Database Design](#8-database-design)
9. [API Specification](#9-api-specification)
10. [User Interface Design](#10-user-interface-design)
11. [Security Requirements](#11-security-requirements)
12. [Migration Strategy](#12-migration-strategy)
13. [Success Criteria](#13-success-criteria)

---

## 1. Executive Summary

### 1.1 Purpose
This document specifies the requirements for building an **Intelligent Data Query Agent Platform** that enables users to upload CSV files, automatically generate database schemas using LLM reasoning, and interact with their data through a natural language chatbot interface.

### 1.2 Project Goals
- Create an intuitive data portal for CSV file management
- Leverage LLM (Ollama with Qwen2.5:14b) to generate intelligent database schemas
- Provide interactive schema visualization and editing capabilities
- Enable natural language data querying through AI agent with tool calling
- Build a modern, scalable architecture using Next.js and FastAPI

### 1.3 Scope
**In Scope:**
- CSV file upload and management (4-5 files per session)
- LLM-powered SQLite schema generation
- Interactive schema visualization and approval workflow
- Natural language chatbot for data queries
- Google OAuth authentication
- Tool calling architecture for SQL execution and data insertion

**Out of Scope (Future Phases):**
- Multi-user collaboration features
- Real-time data synchronization
- Advanced analytics dashboards
- Support for databases other than SQLite
- Excel/JSON file formats

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js 15)                          │
│                     React 19 + TypeScript + shadcn/ui                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────────┐   │
│  │ Auth Pages     │  │ Data Portal     │  │ Chat Query Interface │   │
│  │ - Login        │  │ - CSV Upload    │  │ - Natural Language   │   │
│  │ - OAuth Flow   │  │ - File Manager  │  │ - SQL Agent          │   │
│  └────────────────┘  │ - Schema Viewer │  │ - Results Display    │   │
│                      │ - Schema Editor  │  └──────────────────────┘   │
│                      └─────────────────┘                                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │              Vercel AI SDK (useChat, Tool Calling)                │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │ HTTP/REST + Server-Sent Events (SSE)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI + Python)                        │
│                        Managed by UV (fast package manager)             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────┐  │
│  │ Auth Service │  │ CSV Service      │  │ Schema Gen Service     │  │
│  │ - JWT        │  │ - Upload Handler │  │ - LLM Integration      │  │
│  │ - OAuth      │  │ - Parser         │  │ - Prompt Engineering   │  │
│  │ - Sessions   │  │ - Validator      │  │ - Schema Validator     │  │
│  └──────────────┘  └──────────────────┘  └────────────────────────┘  │
│                                                                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────┐  │
│  │ Query Agent  │  │ Tool Registry    │  │ Data Service           │  │
│  │ - LLM Chat   │  │ - SQL Executor   │  │ - SQLite Manager       │  │
│  │ - Tool Call  │  │ - Data Insert    │  │ - Query Builder        │  │
│  │ - Context    │  │ - Schema Read    │  │ - Transaction Handler  │  │
│  └──────────────┘  └──────────────────┘  └────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    Ollama API Client                              │ │
│  │              (Qwen2.5:14b - Text Generation + Tool Calling)       │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌───────────────────────┐        ┌──────────────────────────────┐    │
│  │  Application DB       │        │  User Data DBs               │    │
│  │  (SQLite - app.db)    │        │  (SQLite - per session)      │    │
│  │                       │        │                              │    │
│  │  - UserSessions       │        │  - DynamicTables             │    │
│  │  - CSVUploads         │        │  - UserData                  │    │
│  │  - GeneratedSchemas   │        │  - GeneratedByLLM            │    │
│  │  - QueryHistory       │        │                              │    │
│  └───────────────────────┘        └──────────────────────────────┘    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │            File Storage (CSV uploads, temp files)                 │ │
│  │                  user_data/csvs/{session_id}/                     │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 User Journey Flow

```
┌─────────────┐
│ User Login  │ (Google OAuth)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ Data Portal Dashboard       │
│ - Welcome Screen            │
│ - Quick Stats (files, DBs)  │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ CSV Upload Phase            │
│ 1. Drag & Drop CSVs (4-5)  │
│ 2. View Previews           │
│ 3. Validate Files          │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Schema Generation Phase     │
│ 1. Click "Generate Schema" │
│ 2. LLM Analyzes CSVs       │
│ 3. Shows Progress          │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Schema Review Phase         │
│ 1. Interactive Visual       │
│ 2. Table Relationships      │
│ 3. Edit Columns/Types       │
│ 4. View LLM Reasoning       │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Approval & Import           │
│ 1. User Approves Schema    │
│ 2. Creates SQLite DB       │
│ 3. Imports CSV Data        │
│ 4. Shows Success Status    │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Chat Query Interface        │
│ 1. Natural Language Input  │
│ 2. Agent Calls SQL Tools   │
│ 3. Displays Results        │
│ 4. Visualizations          │
└─────────────────────────────┘
```

---

## 3. Current System Analysis

### 3.1 Existing Features (RAG Chatbot)
The current system (`wsp_rag_app`) provides:

**Backend (Flask):**
- ✅ Google OAuth authentication
- ✅ JWT token management (RSA signing)
- ✅ User session management
- ✅ PDF document upload and parsing (PyPDF2)
- ✅ ChromaDB vector store for RAG
- ✅ LLM integration (originally Google Gemini)
- ✅ Streaming responses
- ✅ Document retrieval service
- ✅ Chat approach with history management

**Frontend (React + Vite):**
- ✅ Chat interface (ChatInput, MessageList)
- ✅ Login/logout flow
- ✅ File upload (PDF)
- ✅ Message history
- ✅ Copy to clipboard
- ✅ Auth context provider
- ✅ Loading states

### 3.2 Components to Migrate
From the existing system, we will migrate:

**Authentication System:**
- ✅ Google OAuth integration logic
- ✅ JWT service (token creation/validation)
- ✅ Session management
- ✅ Auth decorators/middleware

**Core Services (Reusable Patterns):**
- ✅ Base service architecture
- ✅ LLM service interface
- ✅ Configuration management
- ✅ Error handling patterns

### 3.3 What We're NOT Migrating
- Flask-specific blueprints (replaced by FastAPI routers)
- PDF parsing/ChromaDB (not needed for CSV-based system)
- React custom hooks (replaced by Vercel AI SDK hooks)
- Vite build system (replaced by Next.js)

---

## 4. Proposed System Architecture

### 4.1 Technology Stack

#### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 15.x | React framework with App Router |
| UI Library | React | 19.x | Component library |
| Language | TypeScript | 5.x | Type safety |
| UI Components | shadcn/ui | Latest | Pre-built accessible components |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| AI Integration | Vercel AI SDK | 6.x | LLM streaming, tool calling |
| Package Manager | pnpm | 9.x | Fast, efficient package manager |
| State Management | React Context + Hooks | - | Global state |
| Form Handling | React Hook Form | 7.x | Form validation |
| Data Viz | Recharts | 2.x | Charts for query results |
| Graph Viz | React Flow | 11.x | Schema relationship graphs |

#### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.115.x | Modern async Python API |
| Language | Python | 3.12+ | Backend language |
| Package Manager | uv | Latest | Ultra-fast Python package manager |
| Database ORM | SQLAlchemy | 2.0.x | Database abstraction |
| Database | SQLite | 3.x | Local file-based database |
| CSV Processing | Pandas | 2.x | Data manipulation |
| Authentication | python-jose | 3.x | JWT handling |
| OAuth | google-auth | 2.x | Google OAuth client |
| LLM Client | ollama | Latest | Ollama Python client |
| Validation | Pydantic | 2.x | Data validation |
| CORS | fastapi-cors | - | Cross-origin requests |
| File Upload | python-multipart | - | File handling |

### 4.2 Project Structure

```
data-query-agent/
├── README.md
├── PLAN.md
├── STEPS.md
├── .gitignore
│
├── frontend/                          # Next.js Application
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── components.json               # shadcn/ui config
│   │
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Home page
│   │   ├── globals.css
│   │   │
│   │   ├── auth/                      # Auth pages
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── callback/
│   │   │       └── page.tsx
│   │   │
│   │   ├── portal/                    # Data Portal
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               # Dashboard
│   │   │   ├── upload/
│   │   │   │   └── page.tsx
│   │   │   ├── schema/
│   │   │   │   ├── generate/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── review/
│   │   │   │       └── page.tsx
│   │   │   └── query/
│   │   │       └── page.tsx           # Chat query interface
│   │   │
│   │   └── api/                       # API Route Handlers
│   │       ├── auth/
│   │       │   └── [...nextauth]/
│   │       │       └── route.ts
│   │       └── chat/
│   │           └── route.ts           # Chat endpoint for AI SDK
│   │
│   ├── components/                    # React Components
│   │   ├── ui/                        # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── table.tsx
│   │   │   └── ...
│   │   │
│   │   ├── auth/
│   │   │   ├── LoginButton.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   │
│   │   ├── portal/
│   │   │   ├── CSVUploader.tsx
│   │   │   ├── FileList.tsx
│   │   │   ├── FilePreview.tsx
│   │   │   ├── SchemaVisualizer.tsx
│   │   │   ├── SchemaGraph.tsx
│   │   │   ├── SchemaEditor.tsx
│   │   │   └── GenerateSchemaButton.tsx
│   │   │
│   │   └── chat/
│   │       ├── ChatInterface.tsx
│   │       ├── MessageList.tsx
│   │       ├── MessageItem.tsx
│   │       ├── QueryInput.tsx
│   │       ├── ResultsTable.tsx
│   │       └── ResultsChart.tsx
│   │
│   ├── lib/                           # Utilities
│   │   ├── api.ts                     # API client
│   │   ├── utils.ts                   # Helper functions
│   │   └── auth.ts                    # Auth utilities
│   │
│   ├── hooks/                         # Custom React Hooks
│   │   ├── useAuth.ts
│   │   ├── useCSVUpload.ts
│   │   ├── useSchema.ts
│   │   └── useQuery.ts
│   │
│   ├── types/                         # TypeScript Types
│   │   ├── auth.ts
│   │   ├── csv.ts
│   │   ├── schema.ts
│   │   └── query.ts
│   │
│   └── public/                        # Static assets
│       ├── favicon.ico
│       └── images/
│
├── backend/                           # FastAPI Application
│   ├── pyproject.toml                 # UV project config
│   ├── uv.lock
│   ├── .env.example
│   ├── .env
│   │
│   ├── main.py                        # FastAPI entry point
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration
│   │   ├── database.py                # Database setup
│   │   │
│   │   ├── models/                    # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user_session.py
│   │   │   ├── csv_upload.py
│   │   │   ├── generated_schema.py
│   │   │   └── query_history.py
│   │   │
│   │   ├── schemas/                   # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── csv.py
│   │   │   ├── schema.py
│   │   │   └── query.py
│   │   │
│   │   ├── services/                  # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── base_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── jwt_service.py
│   │   │   ├── csv_service.py
│   │   │   ├── schema_generation_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── query_agent_service.py
│   │   │   ├── data_service.py
│   │   │   └── tool_registry.py
│   │   │
│   │   ├── routers/                   # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── csv.py
│   │   │   ├── schema.py
│   │   │   ├── query.py
│   │   │   └── chat.py
│   │   │
│   │   ├── dependencies/              # FastAPI Dependencies
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── database.py
│   │   │
│   │   ├── middleware/                # Middleware
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   └── error_handler.py
│   │   │
│   │   └── tools/                     # Agent Tools
│   │       ├── __init__.py
│   │       ├── sql_executor.py
│   │       ├── data_insert.py
│   │       └── schema_reader.py
│   │
│   ├── data/                          # Data Storage
│   │   ├── databases/
│   │   │   ├── app.db                 # Application database
│   │   │   └── user_data/             # User-specific databases
│   │   │       └── {session_id}.db
│   │   │
│   │   └── uploads/
│   │       └── csvs/
│   │           └── {session_id}/
│   │
│   ├── keys/                          # Cryptographic Keys
│   │   ├── private_key.pem
│   │   └── public_key.pem
│   │
│   └── tests/                         # Unit Tests
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_csv.py
│       ├── test_schema.py
│       └── test_query.py
│
└── docs/                              # Documentation
    ├── API.md
    ├── ARCHITECTURE.md
    └── DEPLOYMENT.md
```

---

## 5. Functional Requirements

### 5.1 User Authentication (FR-AUTH)

**FR-AUTH-001: Google OAuth Login**
- Users must be able to authenticate using Google OAuth 2.0
- System shall redirect to Google login page
- After successful authentication, user is redirected to dashboard
- Session tokens are stored securely in HTTP-only cookies

**FR-AUTH-002: Session Management**
- System shall issue JWT access tokens (5-minute expiry)
- System shall issue refresh tokens (7-day expiry)
- Access tokens shall be automatically refreshed using refresh tokens
- Users can logout, invalidating all tokens

**FR-AUTH-003: Protected Routes**
- All data portal pages require authentication
- Unauthenticated users are redirected to login
- Token validation occurs on every API request

### 5.2 CSV Upload Management (FR-CSV)

**FR-CSV-001: File Upload**
- Users can upload up to 5 CSV files per session
- Maximum file size: 10 MB per file
- Drag-and-drop interface supported
- Multiple file selection supported
- Upload progress indicators displayed

**FR-CSV-002: File Validation**
- System validates file format (must be valid CSV)
- System checks for duplicate files
- System rejects files exceeding size limits
- System validates CSV structure (consistent columns)

**FR-CSV-003: File Preview**
- Display first 10 rows of each uploaded CSV
- Show column names and inferred data types
- Display file metadata (size, rows, columns)
- Allow file deletion before schema generation

**FR-CSV-004: Metadata Extraction**
- Extract column names from CSV headers
- Infer data types (INTEGER, TEXT, REAL, DATETIME)
- Count total rows
- Detect potential primary key candidates
- Store sample data (first 5 rows)

### 5.3 Schema Generation (FR-SCHEMA)

**FR-SCHEMA-001: LLM-Powered Generation**
- User clicks "Generate Schema" button
- System sends all CSV metadata to LLM (Google Gemini)
- LLM analyzes:
  - Column names and data types
  - Potential relationships between tables
  - Primary key candidates
  - Foreign key relationships
  - Data normalization opportunities
- LLM returns structured JSON schema

**FR-SCHEMA-002: Schema Structure**
Generated schema includes:
- Table definitions with columns
- Data types (SQLite-compatible)
- Primary key constraints
- Foreign key relationships
- NOT NULL constraints
- UNIQUE constraints
- Suggested indexes
- LLM reasoning explanation

**FR-SCHEMA-003: Schema Validation**
- System validates generated schema syntax
- Checks for circular dependencies
- Ensures all foreign keys reference valid tables/columns
- Validates SQLite data type compatibility

### 5.4 Schema Visualization (FR-VIZ)

**FR-VIZ-001: Interactive Display**
- Display all tables as expandable cards
- Show columns with data types and constraints
- Color-code primary keys (gold) and foreign keys (blue)
- Display LLM reasoning in dedicated panel

**FR-VIZ-002: Relationship Graph**
- Visual graph representation using React Flow
- Nodes represent tables
- Edges represent foreign key relationships
- Interactive zoom and pan
- Click on nodes to highlight relationships

**FR-VIZ-003: Schema Editing**
- Users can edit:
  - Column names
  - Data types (dropdown selection)
  - Constraints (checkboxes)
  - Table names
- Validation on each edit
- Unsaved changes indicator

**FR-VIZ-004: Schema Approval**
- "Approve & Import" button
- Confirmation dialog before execution
- Option to download schema as SQL file
- Loading state during import process

### 5.5 Database Operations (FR-DB)

**FR-DB-001: Schema Execution**
- Create user-specific SQLite database
- Execute CREATE TABLE statements
- Set up foreign key constraints
- Create suggested indexes
- Handle errors gracefully

**FR-DB-002: Data Import**
- Import CSV data into created tables
- Handle data type conversions
- Validate data integrity
- Report import statistics (success/failed rows)
- Transaction rollback on errors

**FR-DB-003: Database Management**
- List all user databases
- View database schema
- Drop databases (with confirmation)
- Export database as SQL dump

### 5.6 Query Interface (FR-QUERY)

**FR-QUERY-001: Chat Interface**
- Natural language input field
- Message history display
- Streaming responses
- Loading indicators

**FR-QUERY-002: Agent Tool Calling**
- Agent has access to three tools:
  1. **execute_sql_query**: Run SELECT queries
  2. **insert_data**: Insert rows into tables
  3. **read_schema**: Get table structure

**FR-QUERY-003: SQL Execution Tool**
- Accepts SQL SELECT queries
- Returns results as JSON
- Limits: 100 rows per query
- Timeout: 10 seconds
- Read-only access (no DELETE, UPDATE, DROP)

**FR-QUERY-004: Data Insertion Tool**
- Accepts table name and row data
- Validates data against schema
- Executes INSERT statement
- Returns success/failure message

**FR-QUERY-005: Schema Reader Tool**
- Returns current database schema
- Lists all tables and columns
- Shows relationships
- Helps agent understand data structure

**FR-QUERY-006: Results Display**
- Table view for query results
- Pagination for large result sets
- Column sorting
- Export results as CSV
- Chart visualization for numeric data

**FR-QUERY-007: Query History**
- Store last 50 queries per session
- Display query timestamp
- Re-run previous queries
- Clear history option

### 5.7 Error Handling (FR-ERROR)

**FR-ERROR-001: User-Friendly Messages**
- Display clear error messages
- Suggest corrective actions
- Log errors server-side

**FR-ERROR-002: Validation Errors**
- Real-time form validation
- Highlight invalid fields
- Show validation messages

**FR-ERROR-003: LLM Failures**
- Retry failed LLM requests (max 3 attempts)
- Fallback to manual schema entry
- Display LLM error reasons

---

## 6. Non-Functional Requirements

### 6.1 Performance (NFR-PERF)

**NFR-PERF-001: Response Time**
- Page load time: < 2 seconds
- API response time: < 500ms (except LLM calls)
- LLM schema generation: < 30 seconds
- Query execution: < 5 seconds

**NFR-PERF-002: Concurrency**
- Support 50 concurrent users
- Handle 10 simultaneous LLM requests

**NFR-PERF-003: File Processing**
- CSV parsing: < 3 seconds for 10MB file
- Data import: < 10 seconds for 10,000 rows

### 6.2 Scalability (NFR-SCALE)

**NFR-SCALE-001: Data Limits**
- Max 5 CSV files per session
- Max 10 MB per CSV file
- Max 100,000 rows per CSV
- Max 20 tables per database

**NFR-SCALE-002: Storage**
- Max 100 MB per user session
- Auto-cleanup after 30 days of inactivity

### 6.3 Security (NFR-SEC)

**NFR-SEC-001: Authentication**
- JWT tokens signed with RSA-256
- HTTP-only cookies for token storage
- Tokens expire and require refresh
- Logout invalidates all tokens

**NFR-SEC-002: Authorization**
- Users can only access their own data
- Session-based data isolation
- No cross-user data leakage

**NFR-SEC-003: SQL Injection Prevention**
- Parameterized queries only
- Whitelist SQL operations
- Input sanitization
- Query validation before execution

**NFR-SEC-004: File Upload Security**
- Validate file types (CSV only)
- Scan for malicious content
- Limit file sizes
- Isolated file storage

### 6.4 Usability (NFR-USE)

**NFR-USE-001: User Interface**
- Intuitive navigation
- Responsive design (desktop, tablet)
- Accessible (WCAG 2.1 Level AA)
- Consistent design language (shadcn/ui)

**NFR-USE-002: Feedback**
- Loading states for all async operations
- Success/error notifications (toast messages)
- Progress indicators for long operations
- Helpful error messages

### 6.5 Maintainability (NFR-MAINT)

**NFR-MAINT-001: Code Quality**
- TypeScript strict mode
- Python type hints
- Comprehensive error handling
- Unit test coverage > 70%

**NFR-MAINT-002: Documentation**
- API documentation (OpenAPI/Swagger)
- Code comments for complex logic
- README files for setup
- Architecture diagrams

---

## 7. Technical Stack

### 7.1 Frontend Stack Details

#### Next.js 15 (App Router)
- **Why:** Server-side rendering, file-based routing, API routes, optimized performance
- **Features Used:**
  - App Router for nested layouts
  - Server Components for SEO
  - API Routes for chat endpoint
  - Middleware for auth checks

#### shadcn/ui
- **Why:** Beautiful, accessible, customizable components built on Radix UI
- **Components:**
  - Button, Card, Dialog, Table, Tabs
  - Form, Input, Label, Textarea
  - Toast, Alert, Badge
  - Dropdown Menu, Command Palette

#### Vercel AI SDK
- **Why:** Simplifies LLM streaming, tool calling, and chat interfaces
- **Features Used:**
  - `useChat` hook for chat interface
  - `streamText` for LLM streaming
  - Function calling for agent tools
  - Message history management

### 7.2 Backend Stack Details

#### FastAPI
- **Why:** Modern, fast, automatic API documentation, async support
- **Features Used:**
  - Async endpoints for LLM streaming
  - Pydantic models for validation
  - OpenAPI documentation
  - Dependency injection
  - WebSocket support (future)

#### UV Package Manager
- **Why:** 10-100x faster than pip, Rust-based, compatible with pip
- **Commands:**
  ```bash
  uv init          # Initialize project
  uv add fastapi   # Add dependency
  uv run main.py   # Run application
  uv sync          # Install dependencies
  ```

#### SQLAlchemy 2.0
- **Why:** Powerful ORM, supports dynamic table creation, migrations
- **Usage:**
  - Define models for metadata tables
  - Dynamic table creation for user data
  - Transaction management
  - Query building

#### Ollama with Qwen2.5:14b
- **Why:** Open-source, runs locally, no API costs, supports function calling
- **Model:**
  - `qwen2.5:14b` - Excellent reasoning and coding capabilities
  - Runs locally on GPU/CPU
  - 14B parameters - good balance of speed and quality
- **Features:**
  - Tool/function calling support
  - JSON mode for structured output
  - Streaming responses
  - No API rate limits
  - Privacy-friendly (local execution)

---

## 8. Database Design

### 8.1 Application Database Schema

**Table: user_sessions**
```sql
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,              -- User ID from Google OAuth
    refresh_token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_refresh_token ON user_sessions(refresh_token);
CREATE INDEX idx_user_active ON user_sessions(name, is_active);
```

**Table: csv_uploads**
```sql
CREATE TABLE csv_uploads (
    id TEXT PRIMARY KEY,
    user_session_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT NOT NULL,
    columns JSON NOT NULL,           -- ["col1", "col2", ...]
    column_types JSON NOT NULL,      -- {"col1": "INTEGER", "col2": "TEXT"}
    sample_data JSON NOT NULL,       -- [[row1], [row2], ...]
    row_count INTEGER NOT NULL,
    file_size INTEGER NOT NULL,      -- In bytes
    status TEXT DEFAULT 'uploaded',  -- uploaded, processed, imported, error
    
    FOREIGN KEY (user_session_id) REFERENCES user_sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_session ON csv_uploads(user_session_id);
CREATE INDEX idx_status ON csv_uploads(status);
```

**Table: generated_schemas**
```sql
CREATE TABLE generated_schemas (
    id TEXT PRIMARY KEY,
    user_session_id TEXT NOT NULL,
    csv_upload_ids JSON NOT NULL,    -- [csv_id1, csv_id2, ...]
    schema_json JSON NOT NULL,       -- Full schema structure
    create_statements JSON NOT NULL, -- SQL CREATE statements
    llm_reasoning TEXT,              -- LLM's explanation
    llm_model TEXT,                  -- Model used (e.g., qwen2.5:14b)
    status TEXT DEFAULT 'generated', -- generated, approved, executed, error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    database_path TEXT,              -- Path to created SQLite DB
    
    FOREIGN KEY (user_session_id) REFERENCES user_sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_schema_user ON generated_schemas(user_session_id);
CREATE INDEX idx_schema_status ON generated_schemas(status);
```

**Table: query_history**
```sql
CREATE TABLE query_history (
    id TEXT PRIMARY KEY,
    user_session_id TEXT NOT NULL,
    generated_schema_id TEXT NOT NULL,
    query_text TEXT NOT NULL,        -- Natural language query
    sql_query TEXT,                  -- Generated SQL (if any)
    result_json JSON,                -- Query results
    execution_time REAL,             -- In seconds
    status TEXT,                     -- success, error
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_session_id) REFERENCES user_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (generated_schema_id) REFERENCES generated_schemas(id) ON DELETE CASCADE
);

CREATE INDEX idx_query_user ON query_history(user_session_id);
CREATE INDEX idx_query_schema ON query_history(generated_schema_id);
```

### 8.2 User Data Database Schema (Dynamic)

Each user session gets a separate SQLite database: `user_data/{session_id}.db`

Schema is dynamically created based on LLM-generated structure. Example:

```sql
-- Example generated by LLM
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_customer_email ON customers(email);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
```

---

## 9. API Specification

### 9.1 Authentication Endpoints

**POST /api/auth/google/callback**
- **Description:** Handle Google OAuth callback
- **Request Body:**
  ```json
  {
    "code": "authorization_code",
    "redirect_uri": "http://localhost:3000/auth/callback"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "eyJ...",
    "expires_in": 300
  }
  ```
- **Cookies Set:**
  - `access_token` (5 min)
  - `refresh_token` (7 days)

**POST /api/auth/refresh**
- **Description:** Refresh access token
- **Request:** Requires `refresh_token` cookie
- **Response:**
  ```json
  {
    "access_token": "eyJ...",
    "expires_in": 300
  }
  ```

**GET /api/auth/status**
- **Description:** Check authentication status
- **Response:**
  ```json
  {
    "is_authenticated": true,
    "user_id": "google_user_id"
  }
  ```

**POST /api/auth/logout**
- **Description:** Logout and invalidate tokens
- **Response:**
  ```json
  {
    "message": "Logged out successfully"
  }
  ```

### 9.2 CSV Management Endpoints

**POST /api/csv/upload**
- **Description:** Upload CSV file(s)
- **Headers:** `Authorization: Bearer {token}`
- **Request:** `multipart/form-data`
- **Response:**
  ```json
  {
    "uploaded_files": [
      {
        "id": "csv_123",
        "filename": "customers.csv",
        "row_count": 1500,
        "columns": ["id", "name", "email"],
        "column_types": {
          "id": "INTEGER",
          "name": "TEXT",
          "email": "TEXT"
        }
      }
    ]
  }
  ```

**GET /api/csv/list**
- **Description:** List all uploaded CSVs for current session
- **Headers:** `Authorization: Bearer {token}`
- **Response:**
  ```json
  {
    "csv_files": [
      {
        "id": "csv_123",
        "filename": "customers.csv",
        "upload_timestamp": "2025-10-28T10:30:00Z",
        "row_count": 1500,
        "file_size": 45000,
        "status": "uploaded"
      }
    ]
  }
  ```

**GET /api/csv/{csv_id}**
- **Description:** Get CSV details with sample data
- **Response:**
  ```json
  {
    "id": "csv_123",
    "filename": "customers.csv",
    "columns": ["id", "name", "email"],
    "column_types": {...},
    "sample_data": [
      [1, "John Doe", "john@example.com"],
      [2, "Jane Smith", "jane@example.com"]
    ],
    "row_count": 1500
  }
  ```

**DELETE /api/csv/{csv_id}**
- **Description:** Delete uploaded CSV
- **Response:**
  ```json
  {
    "message": "CSV deleted successfully"
  }
  ```

### 9.3 Schema Generation Endpoints

**POST /api/schema/generate**
- **Description:** Generate schema using LLM
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "csv_ids": ["csv_123", "csv_456"]
  }
  ```
- **Response:**
  ```json
  {
    "schema_id": "schema_789",
    "tables": [
      {
        "name": "customers",
        "columns": [
          {
            "name": "customer_id",
            "type": "INTEGER",
            "constraints": ["PRIMARY KEY"],
            "references": null
          }
        ]
      }
    ],
    "relationships": [...],
    "reasoning": "LLM explanation...",
    "create_statements": ["CREATE TABLE ..."]
  }
  ```

**GET /api/schema/{schema_id}**
- **Description:** Get generated schema details
- **Response:** Same as generate response

**PUT /api/schema/{schema_id}**
- **Description:** Update schema (edit columns/types)
- **Request Body:**
  ```json
  {
    "tables": [...]  // Updated schema
  }
  ```

**POST /api/schema/{schema_id}/approve**
- **Description:** Approve schema and create database
- **Response:**
  ```json
  {
    "message": "Schema executed successfully",
    "database_path": "user_data/session_123.db",
    "import_stats": {
      "total_rows": 2000,
      "imported": 1998,
      "failed": 2
    }
  }
  ```

**DELETE /api/schema/{schema_id}**
- **Description:** Delete schema and associated database

### 9.4 Query Endpoints

**POST /api/chat**
- **Description:** Chat interface for querying data (Vercel AI SDK compatible)
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "messages": [
      {
        "role": "user",
        "content": "Show me top 5 customers by order value"
      }
    ],
    "schema_id": "schema_789"
  }
  ```
- **Response:** Server-Sent Events (SSE) stream
  ```
  data: {"type": "text", "text": "Let me query that for you..."}
  
  data: {"type": "tool_call", "tool": "execute_sql_query", "args": {...}}
  
  data: {"type": "tool_result", "result": [...]}
  
  data: {"type": "text", "text": "Here are the top 5 customers..."}
  ```

**POST /api/query/execute**
- **Description:** Direct SQL execution (for agent tools)
- **Request Body:**
  ```json
  {
    "schema_id": "schema_789",
    "query": "SELECT * FROM customers LIMIT 10"
  }
  ```
- **Response:**
  ```json
  {
    "columns": ["customer_id", "name", "email"],
    "rows": [[1, "John", "john@ex.com"]],
    "row_count": 10,
    "execution_time": 0.05
  }
  ```

**POST /api/query/insert**
- **Description:** Insert data (for agent tools)
- **Request Body:**
  ```json
  {
    "schema_id": "schema_789",
    "table": "customers",
    "data": {
      "name": "New Customer",
      "email": "new@example.com"
    }
  }
  ```

**GET /api/query/history**
- **Description:** Get query history
- **Query Params:** `schema_id`, `limit`, `offset`

---

## 10. User Interface Design

### 10.1 Page Hierarchy

```
/ (Home)
├── /auth/login
├── /auth/callback
│
└── /portal (Dashboard)
    ├── /portal/upload (CSV Upload)
    ├── /portal/schema
    │   ├── /portal/schema/generate
    │   └── /portal/schema/review
    └── /portal/query (Chat Interface)
```

### 10.2 Key UI Components

#### Login Page (`/auth/login`)
- Full-screen centered layout
- "Sign in with Google" button (shadcn Button + Google icon)
- Branding/logo
- Brief description of the platform

#### Data Portal Dashboard (`/portal`)
- **Header:**
  - Logo
  - User avatar (dropdown: profile, logout)
  - Navigation tabs: Upload, Schema, Query
  
- **Main Content:**
  - Welcome message
  - Quick stats cards:
    - Uploaded CSVs count
    - Generated schemas count
    - Query history count
  - Recent activity timeline
  - Quick action buttons:
    - "Upload New CSV"
    - "Generate Schema"
    - "Start Querying"

#### CSV Upload Page (`/portal/upload`)
- **File Uploader Component:**
  - Drag-and-drop zone (dashed border, hover effect)
  - File browser button
  - Multiple file selection
  - Progress bars for each upload
  
- **Uploaded Files List:**
  - Table with columns:
    - Filename
    - Size
    - Rows
    - Columns
    - Status
    - Actions (Preview, Delete)
  - Click filename to expand preview
  
- **File Preview Dialog:**
  - Table showing first 10 rows
  - Column headers with inferred types
  - Metadata panel (row count, file size)

- **Action Button:**
  - "Generate Schema" (enabled when 1-5 CSVs uploaded)

#### Schema Generation Page (`/portal/schema/generate`)
- **Progress Indicator:**
  - Multi-step progress bar:
    1. Analyzing CSVs
    2. Consulting LLM
    3. Generating Schema
    4. Validating
  - Current step highlighted
  - Estimated time remaining
  
- **Status Messages:**
  - Real-time updates (e.g., "Analyzing customers.csv...")
  - Success message on completion
  - Redirect to Review page

#### Schema Review Page (`/portal/schema/review`)
- **Layout:** Split view (60/40)

- **Left Panel - Schema Visualizer:**
  - Tabs: "Tables" | "Graph" | "SQL"
  
  - **Tables Tab:**
    - Accordion list of tables
    - Each table shows:
      - Table name (editable)
      - Columns list (editable):
        - Column name
        - Data type (dropdown)
        - Constraints (checkboxes: PK, NOT NULL, UNIQUE)
        - Foreign key reference (if any)
      - "Add Column" button
  
  - **Graph Tab:**
    - React Flow visualization
    - Table nodes (colored by table)
    - Relationship edges
    - Zoom/pan controls
    - Click node to highlight in Tables tab
  
  - **SQL Tab:**
    - Syntax-highlighted CREATE statements
    - Copy button
    - Download as .sql button

- **Right Panel - LLM Reasoning:**
  - Card with LLM explanation
  - Sections:
    - "Design Decisions"
    - "Identified Relationships"
    - "Normalization Notes"
    - "Suggested Indexes"

- **Action Bar (Bottom):**
  - "Edit Schema" button (toggles edit mode)
  - "Approve & Import" button (primary, green)
  - "Cancel" button (secondary)

#### Query Interface Page (`/portal/query`)
- **Layout:** Chat-like interface

- **Header:**
  - Schema selector dropdown (if multiple)
  - Database info badge (table count, row count)
  - "View Schema" button (opens modal)

- **Message List:**
  - User messages (right-aligned, blue)
  - Agent messages (left-aligned, gray)
  - Tool call indicators (collapsed, expandable)
  - Query results displayed as:
    - Data tables (sortable, paginated)
    - Charts (if numeric data)
    - JSON viewer (for complex objects)

- **Input Area:**
  - Textarea with placeholder: "Ask about your data..."
  - Example prompts below input:
    - "Show me top 10 customers"
    - "Insert a new order for customer ID 5"
    - "What is the total revenue by month?"
  - Send button
  - "New Chat" button (clears history)

- **Sidebar (Collapsible):**
  - Query history (last 20 queries)
  - Click to re-run query
  - Export results button (per query)

### 10.3 Component Library (shadcn/ui)

Components to be used:
- **Layout:** Sidebar, Navigation Menu, Tabs
- **Forms:** Input, Textarea, Select, Checkbox, Label
- **Feedback:** Toast, Alert, Progress, Spinner
- **Data Display:** Table, Card, Badge, Accordion
- **Overlay:** Dialog, Dropdown Menu, Popover
- **Actions:** Button, Icon Button
- **Visualizations:** Recharts (Bar, Line, Pie)

---

## 11. Security Requirements

### 11.1 Authentication Security

**Token Management:**
- Access tokens: JWT signed with RSA-256 private key
- Refresh tokens: 64-byte secure random string
- Token storage: HTTP-only, Secure, SameSite cookies
- Token rotation: New refresh token on every refresh

**OAuth Security:**
- Use state parameter for CSRF protection
- Validate redirect_uri against whitelist
- Verify ID token signature
- Check token expiry

### 11.2 Authorization

**Session Isolation:**
- Each user session has unique ID
- CSV files stored in user-specific directories
- SQLite databases isolated per session
- No cross-session data access

**API Authorization:**
- All protected endpoints require valid access token
- Token validation on every request
- User ID extracted from token, not request body
- Database queries filtered by user_session_id

### 11.3 Data Security

**File Upload:**
- Validate file MIME type (text/csv)
- Check file extension
- Limit file size (10 MB)
- Scan for malicious content
- Store files outside web root

**SQL Injection Prevention:**
- Use parameterized queries (SQLAlchemy)
- Whitelist SQL operations (SELECT, INSERT only)
- Parse and validate SQL before execution
- Deny dangerous keywords (DROP, DELETE, ALTER, etc.)
- Use read-only database connections where possible

**Input Validation:**
- Pydantic schemas for all API inputs
- Type checking (TypeScript + Python)
- Sanitize user inputs
- Escape special characters

### 11.4 Infrastructure Security

**HTTPS:**
- Enforce HTTPS in production
- HSTS headers
- Secure cookie flag

**CORS:**
- Whitelist frontend origin only
- Credentials: true
- Strict origin validation

**Rate Limiting:**
- LLM API calls: 10 per minute per user
- File uploads: 5 per minute per user
- Query execution: 30 per minute per user

**Environment Variables:**
- Store secrets in `.env` (never commit)
- Use different keys for dev/prod
- Rotate keys regularly

---

## 12. Migration Strategy

### 12.1 What to Migrate

From `wsp_rag_app/backend`:

**Authentication System:**
1. `services/auth_service.py` → `app/services/auth_service.py`
   - Adapt Google OAuth flow for FastAPI
   - Keep JWT signing logic
   
2. `services/jwt_service.py` → `app/services/jwt_service.py`
   - Keep RSA key loading
   - Keep token creation/validation
   
3. `models/user_session.py` → `app/models/user_session.py`
   - Adapt for SQLAlchemy 2.0 syntax
   
4. `private_key.pem`, `public_key.pem` → `backend/keys/`
   - Copy as-is

**Configuration:**
5. `config.py` → `app/config.py`
   - Adapt for Pydantic Settings
   - Add new config variables

**LLM Service (as reference):**
6. `services/llm_service.py` → Reference for new implementation
   - Adapt streaming for FastAPI
   - Add tool calling support

### 12.2 Migration Steps

**Phase 1: Setup New Project**
1. Create new directory: `data-query-agent/`
2. Initialize frontend: `pnpm create next-app@latest`
3. Initialize backend: `uv init`
4. Install dependencies

**Phase 2: Backend Migration**
1. Copy authentication files
2. Adapt for FastAPI (replace Flask blueprints with routers)
3. Update database connection (SQLAlchemy setup)
4. Test authentication flow

**Phase 3: Frontend Setup**
1. Setup Next.js with App Router
2. Install shadcn/ui
3. Create auth pages
4. Implement login flow

**Phase 4: New Features**
1. Build CSV upload backend
2. Build schema generation service
3. Build frontend components
4. Integrate Vercel AI SDK

**Phase 5: Testing & Deployment**
1. Unit tests
2. Integration tests
3. End-to-end tests
4. Deploy to production

### 12.3 Code Adaptation Examples

**Flask → FastAPI:**
```python
# OLD (Flask)
@api_bp.route('/documents', methods=['POST'])
def create_document():
    data = request.get_json()
    # ...
    return jsonify(result), 201

# NEW (FastAPI)
@router.post('/documents', status_code=201)
async def create_document(data: DocumentCreate, db: Session = Depends(get_db)):
    # ...
    return result
```

**React Hooks → Vercel AI SDK:**
```typescript
// OLD (Custom hook)
const { messages, sendMessage } = useChat();

// NEW (Vercel AI SDK)
const { messages, input, handleInputChange, handleSubmit } = useChat({
  api: '/api/chat',
  onError: (error) => toast.error(error.message)
});
```

---

## 13. Success Criteria

### 13.1 Functional Success

✅ **User can:**
- Login with Google OAuth
- Upload 4-5 CSV files
- Generate schema automatically with LLM
- View schema in interactive visualizer
- Edit schema before approval
- Approve and import data successfully
- Query data using natural language
- View query results in table/chart format
- Insert new data via chatbot

### 13.2 Technical Success

✅ **System achieves:**
- Schema generation accuracy > 90%
- API response time < 500ms
- Zero SQL injection vulnerabilities
- Test coverage > 70%
- Zero authentication bypasses
- Proper error handling (no crashes)

### 13.3 Performance Success

✅ **Benchmarks:**
- Supports 50 concurrent users
- LLM schema generation < 30 seconds
- CSV import (10K rows) < 10 seconds
- Query execution < 5 seconds
- Page load < 2 seconds

### 13.4 User Experience Success

✅ **UX Metrics:**
- Intuitive UI (user testing)
- Clear error messages
- Responsive design (mobile/desktop)
- Accessible (WCAG 2.1 AA)
- Consistent design language

---

## 14. Future Enhancements (Out of Scope)

### Phase 2 Features:
- Support for Excel, JSON file formats
- Data visualization dashboards
- Scheduled queries (cron jobs)
- Email reports
- Multi-user collaboration
- Real-time data updates (WebSocket)

### Phase 3 Features:
- PostgreSQL/MySQL support
- Cloud database integration (AWS RDS, Supabase)
- Advanced analytics (aggregations, pivots)
- Data export formats (PDF, Excel)
- API key generation for external access

### Phase 4 Features:
- Machine learning insights
- Anomaly detection
- Predictive analytics
- Data lineage tracking
- Audit logs

---

## 15. Glossary

- **LLM:** Large Language Model (Ollama with Qwen2.5:14b)
- **Ollama:** Local LLM runtime for running open-source models
- **Qwen2.5:14b:** 14 billion parameter model by Alibaba Cloud
- **RAG:** Retrieval-Augmented Generation
- **JWT:** JSON Web Token
- **OAuth:** Open Authorization
- **SQLite:** Embedded relational database
- **FastAPI:** Modern Python web framework
- **Next.js:** React framework for production
- **shadcn/ui:** Component library
- **Vercel AI SDK:** TypeScript toolkit for AI apps
- **UV:** Fast Python package manager
- **SSE:** Server-Sent Events (streaming)
- **Tool Calling:** LLM function invocation

---

## 16. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-28 | System | Initial SRS document |

---

**Document Status:** ✅ Approved for Implementation

**Next Steps:** See `STEPS.md` for detailed implementation plan.
