# Implementation Steps: Data Query Agent Platform

**Project:** Intelligent Data Query Agent with LLM-Powered Schema Generation  
**Framework:** Next.js 15 + FastAPI  
**Timeline:** ~2-3 weeks (for MVP)

---

## Phase 0: Project Setup & Environment Configuration

### Step 0.1: Create Project Structure ⏱️ 30 minutes

```bash
# Create new project directory
mkdir data-query-agent
cd data-query-agent

# Create main directories
mkdir frontend backend docs

# Initialize git
git init
echo "# Data Query Agent Platform" > README.md
```

**Create `.gitignore`:**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env
*.db
*.sqlite3

# Node
node_modules/
.next/
out/
dist/
.pnpm-store/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
backend/data/uploads/
backend/data/databases/user_data/
backend/keys/private_key.pem
backend/keys/public_key.pem
```

### Step 0.2: Backend Initialization with UV ⏱️ 30 minutes

```bash
cd backend

# Initialize UV project
uv init

# Create project structure
mkdir -p app/{models,schemas,services,routers,dependencies,middleware,tools}
mkdir -p data/{databases,uploads/csvs}
mkdir -p keys
mkdir -p tests

# Create __init__.py files
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/routers/__init__.py
touch app/dependencies/__init__.py
touch app/middleware/__init__.py
touch app/tools/__init__.py
touch tests/__init__.py

# Create main entry point
touch main.py
```

**Install Ollama (if not already installed):**
```bash
# For Linux
curl -fsSL https://ollama.com/install.sh | sh

# For macOS
brew install ollama

# For Windows
# Download from https://ollama.com/download

# Start Ollama service
ollama serve &

# Pull Qwen2.5:14b model
ollama pull qwen2.5:14b

# Test Ollama
ollama run qwen2.5:14b "Hello, test message"
```

**Add dependencies:**
```bash
# Core framework
uv add fastapi uvicorn[standard]

# Database
uv add sqlalchemy alembic

# Authentication
uv add python-jose[cryptography] passlib[bcrypt] google-auth google-auth-oauthlib

# Data processing
uv add pandas python-multipart

# LLM
uv add ollama

# Validation
uv add pydantic pydantic-settings

# Utilities
uv add python-dotenv

# Development
uv add --dev pytest pytest-asyncio httpx
```

**Create `backend/.env.example`:**
```env
# Application
APP_NAME=Data Query Agent
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b

# Database
DATABASE_URL=sqlite:///./data/databases/app.db

# JWT
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10 MB in bytes
MAX_CSV_FILES=5
```

### Step 0.3: Frontend Initialization with Next.js & pnpm ⏱️ 45 minutes

```bash
cd ../frontend

# Create Next.js app with TypeScript
pnpm create next-app@latest . --typescript --tailwind --app --use-pnpm

# Install shadcn/ui
pnpm dlx shadcn@latest init

# Select options:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes

# Install shadcn components
pnpm dlx shadcn@latest add button card input label textarea select checkbox table tabs dialog alert toast dropdown-menu command badge progress separator

# Install additional dependencies
pnpm add @vercel/ai ai
pnpm add react-hook-form zod @hookform/resolvers
pnpm add recharts
pnpm add reactflow
pnpm add lucide-react
pnpm add date-fns
pnpm add @tanstack/react-query

# Install dev dependencies
pnpm add -D @types/node @types/react @types/react-dom
```

**Create frontend directory structure:**
```bash
mkdir -p app/{auth/{login,callback},portal/{upload,schema/{generate,review},query}}
mkdir -p app/api/{auth,chat}
mkdir -p components/{auth,portal,chat,ui}
mkdir -p lib
mkdir -p hooks
mkdir -p types
```

**Create `frontend/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id_here
```

### Step 0.4: Copy Authentication Assets from Old Project ⏱️ 15 minutes

```bash
# Copy RSA keys
cp ../wsp_rag_app/backend/private_key.pem backend/keys/
cp ../wsp_rag_app/backend/public_key.pem backend/keys/

# Copy Google OAuth credentials (if needed)
cp ../wsp_rag_app/backend/client_secret.json backend/
```

---

## Phase 1: Backend - Authentication System Migration

### Step 1.1: Database Configuration ⏱️ 30 minutes

**Create `backend/app/database.py`:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 1.2: Configuration Management ⏱️ 30 minutes

**Create `backend/app/config.py`:**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Data Query Agent"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID: str
    GOOGLE_OAUTH_CLIENT_SECRET: str
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:14b"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/databases/app.db"
    
    # JWT
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10 MB
    MAX_CSV_FILES: int = 5
    
    # Paths
    UPLOAD_DIR: str = "./data/uploads/csvs"
    USER_DB_DIR: str = "./data/databases/user_data"
    KEYS_DIR: str = "./keys"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

### Step 1.3: User Session Model ⏱️ 30 minutes

**Create `backend/app/models/user_session.py`:**
```python
from sqlalchemy import Column, String, DateTime, Boolean, func
from app.database import Base
import uuid

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # User ID from Google
    refresh_token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active
        }
```

### Step 1.4: JWT Service (Migrate & Adapt) ⏱️ 1 hour

**Create `backend/app/services/jwt_service.py`:**
- Copy from `wsp_rag_app/backend/src/services/jwt_service.py`
- Adapt imports for new structure
- Update key path loading to use `settings.KEYS_DIR`
- Keep RSA signing logic as-is
- Test token creation and validation

### Step 1.5: Auth Service (Migrate & Adapt) ⏱️ 1.5 hours

**Create `backend/app/services/auth_service.py`:**
- Copy from `wsp_rag_app/backend/src/services/auth_service.py`
- Adapt for FastAPI (async where needed)
- Update Google OAuth flow
- Integrate with new database session
- Add type hints (Pydantic models)

### Step 1.6: Auth Router (FastAPI Endpoints) ⏱️ 2 hours

**Create `backend/app/routers/auth.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import GoogleCallbackRequest, TokenResponse, AuthStatusResponse
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(
    request: GoogleCallbackRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    auth_service = AuthService(db)
    
    # Authenticate with Google
    user_id, success, error = auth_service.authenticate_with_google(
        request.code,
        request.redirect_uri,
        settings.GOOGLE_OAUTH_CLIENT_ID
    )
    
    if not success:
        raise HTTPException(status_code=401, detail=error)
    
    # Create tokens
    access_token, refresh_token, expires_at = auth_service.create_auth_tokens(user_id)
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax"
    )
    
    return TokenResponse(access_token=access_token, expires_in=300)

# Add other endpoints: /refresh, /status, /logout
```

### Step 1.7: Auth Dependency (Protected Routes) ⏱️ 30 minutes

**Create `backend/app/dependencies/auth.py`:**
```python
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.services.auth_service import AuthService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """Validate token and return user ID"""
    auth_service = AuthService(db)
    token = credentials.credentials
    
    user_id, is_valid = auth_service.validate_access_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return user_id
```

### Step 1.8: Main FastAPI Application ⏱️ 30 minutes

**Create `backend/main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Data Query Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
```

### Step 1.9: Test Authentication Backend ⏱️ 30 minutes

```bash
cd backend

# Run the application
uv run main.py

# Test endpoints
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Test with Postman or similar:
# - POST /api/auth/google/callback
# - GET /api/auth/status
# - POST /api/auth/refresh
# - POST /api/auth/logout
```

---

## Phase 2: Frontend - Authentication UI

### Step 2.1: API Client Configuration ⏱️ 30 minutes

**Create `frontend/lib/api.ts`:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  baseURL: API_URL,
  
  async fetch(endpoint: string, options: RequestInit = {}) {
    const url = `${API_URL}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      credentials: 'include', // Include cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'API request failed');
    }
    
    return response.json();
  },
  
  // Auth endpoints
  auth: {
    googleCallback: (code: string, redirectUri: string) =>
      api.fetch('/api/auth/google/callback', {
        method: 'POST',
        body: JSON.stringify({ code, redirect_uri: redirectUri }),
      }),
    
    status: () => api.fetch('/api/auth/status'),
    
    refresh: () => api.fetch('/api/auth/refresh', { method: 'POST' }),
    
    logout: () => api.fetch('/api/auth/logout', { method: 'POST' }),
  },
};
```

### Step 2.2: Auth Context & Hook ⏱️ 1 hour

**Create `frontend/hooks/useAuth.ts`:**
```typescript
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  userId: string | null;
  login: (code: string, redirectUri: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const router = useRouter();
  
  // Check auth status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);
  
  const checkAuthStatus = async () => {
    try {
      const data = await api.auth.status();
      setIsAuthenticated(data.is_authenticated);
      setUserId(data.user_id || null);
    } catch (error) {
      setIsAuthenticated(false);
      setUserId(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  const login = async (code: string, redirectUri: string) => {
    try {
      await api.auth.googleCallback(code, redirectUri);
      await checkAuthStatus();
      router.push('/portal');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };
  
  const logout = async () => {
    try {
      await api.auth.logout();
      setIsAuthenticated(false);
      setUserId(null);
      router.push('/auth/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };
  
  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, userId, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Step 2.3: Login Page ⏱️ 1 hour

**Create `frontend/app/auth/login/page.tsx`:**
```typescript
'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function LoginPage() {
  const handleGoogleLogin = () => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    const redirectUri = `${window.location.origin}/auth/callback`;
    const scope = 'openid email profile';
    
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${clientId}&` +
      `redirect_uri=${redirectUri}&` +
      `response_type=code&` +
      `scope=${scope}&` +
      `access_type=offline&` +
      `prompt=consent`;
    
    window.location.href = authUrl;
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Data Query Agent</h1>
          <p className="text-slate-600">
            Upload CSVs, generate schemas, query with AI
          </p>
        </div>
        
        <Button 
          onClick={handleGoogleLogin} 
          className="w-full"
          size="lg"
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            {/* Google icon SVG */}
          </svg>
          Sign in with Google
        </Button>
      </Card>
    </div>
  );
}
```

### Step 2.4: OAuth Callback Page ⏱️ 45 minutes

**Create `frontend/app/auth/callback/page.tsx`:**
```typescript
'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'sonner';

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  
  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');
    
    if (error) {
      toast.error('Authentication failed');
      router.push('/auth/login');
      return;
    }
    
    if (code) {
      const redirectUri = `${window.location.origin}/auth/callback`;
      login(code, redirectUri).catch(() => {
        toast.error('Login failed');
        router.push('/auth/login');
      });
    }
  }, [searchParams, login, router]);
  
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900 mx-auto"></div>
        <p className="mt-4 text-slate-600">Authenticating...</p>
      </div>
    </div>
  );
}
```

### Step 2.5: Protected Route Component ⏱️ 30 minutes

**Create `frontend/components/auth/ProtectedRoute.tsx`:**
```typescript
'use client';

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return null;
  }
  
  return <>{children}</>;
}
```

### Step 2.6: Root Layout with Auth Provider ⏱️ 15 minutes

**Update `frontend/app/layout.tsx`:**
```typescript
import { AuthProvider } from '@/hooks/useAuth';
import { Toaster } from '@/components/ui/sonner';
import './globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  );
}
```

### Step 2.7: Test Authentication Flow ⏱️ 30 minutes

```bash
cd frontend
pnpm dev

# Test:
# 1. Navigate to http://localhost:3000/auth/login
# 2. Click "Sign in with Google"
# 3. Complete OAuth flow
# 4. Verify redirect to /portal
# 5. Test logout
```

---

## Phase 3: Backend - CSV Upload & Management

### Step 3.1: CSV Upload Model ⏱️ 30 minutes

**Create `backend/app/models/csv_upload.py`:**
```python
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, func
from app.database import Base
import uuid

class CSVUpload(Base):
    __tablename__ = "csv_uploads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_session_id = Column(String, ForeignKey("user_sessions.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, server_default=func.now())
    file_path = Column(String, nullable=False)
    columns = Column(JSON, nullable=False)  # List of column names
    column_types = Column(JSON, nullable=False)  # Dict mapping col -> type
    sample_data = Column(JSON, nullable=False)  # First 5 rows
    row_count = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, default="uploaded")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_session_id": self.user_session_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "upload_timestamp": self.upload_timestamp.isoformat(),
            "columns": self.columns,
            "column_types": self.column_types,
            "sample_data": self.sample_data,
            "row_count": self.row_count,
            "file_size": self.file_size,
            "status": self.status
        }
```

### Step 3.2: CSV Service ⏱️ 2 hours

**Create `backend/app/services/csv_service.py`:**
```python
import pandas as pd
import os
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.csv_upload import CSVUpload
from app.config import settings

class CSVService:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.upload_dir = Path(settings.UPLOAD_DIR) / user_id
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_csv(self, file, filename: str) -> CSVUpload:
        """Upload and parse CSV file"""
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise ValueError("File too large")
        
        # Check CSV count limit
        existing_count = self.db.query(CSVUpload).filter(
            CSVUpload.user_session_id == self.user_id,
            CSVUpload.status == "uploaded"
        ).count()
        
        if existing_count >= settings.MAX_CSV_FILES:
            raise ValueError(f"Maximum {settings.MAX_CSV_FILES} files allowed")
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}_{filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse CSV
        df = pd.read_csv(file_path)
        
        # Extract metadata
        columns = df.columns.tolist()
        column_types = self._infer_types(df)
        sample_data = df.head(5).values.tolist()
        row_count = len(df)
        
        # Create database record
        csv_upload = CSVUpload(
            id=file_id,
            user_session_id=self.user_id,
            filename=f"{file_id}_{filename}",
            original_filename=filename,
            file_path=str(file_path),
            columns=columns,
            column_types=column_types,
            sample_data=sample_data,
            row_count=row_count,
            file_size=file_size
        )
        
        self.db.add(csv_upload)
        self.db.commit()
        self.db.refresh(csv_upload)
        
        return csv_upload
    
    def _infer_types(self, df: pd.DataFrame) -> dict:
        """Infer SQLite-compatible types from pandas dtypes"""
        type_map = {
            'int64': 'INTEGER',
            'float64': 'REAL',
            'object': 'TEXT',
            'bool': 'INTEGER',
            'datetime64': 'DATETIME'
        }
        
        return {
            col: type_map.get(str(df[col].dtype), 'TEXT')
            for col in df.columns
        }
    
    def list_uploads(self) -> list[CSVUpload]:
        """List all CSV uploads for user"""
        return self.db.query(CSVUpload).filter(
            CSVUpload.user_session_id == self.user_id
        ).all()
    
    def get_upload(self, csv_id: str) -> CSVUpload:
        """Get specific CSV upload"""
        return self.db.query(CSVUpload).filter(
            CSVUpload.id == csv_id,
            CSVUpload.user_session_id == self.user_id
        ).first()
    
    def delete_upload(self, csv_id: str) -> bool:
        """Delete CSV upload"""
        csv_upload = self.get_upload(csv_id)
        if not csv_upload:
            return False
        
        # Delete file
        if os.path.exists(csv_upload.file_path):
            os.remove(csv_upload.file_path)
        
        # Delete DB record
        self.db.delete(csv_upload)
        self.db.commit()
        
        return True
```

### Step 3.3: CSV Router ⏱️ 1 hour

**Create `backend/app/routers/csv.py`:**
```python
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.services.csv_service import CSVService
from app.schemas.csv import CSVUploadResponse, CSVListResponse

router = APIRouter(prefix="/api/csv", tags=["CSV Management"])

@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    csv_service = CSVService(db, user_id)
    
    try:
        csv_upload = await csv_service.upload_csv(file, file.filename)
        return csv_upload.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list", response_model=CSVListResponse)
async def list_csvs(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all uploaded CSVs"""
    csv_service = CSVService(db, user_id)
    uploads = csv_service.list_uploads()
    return {"csv_files": [u.to_dict() for u in uploads]}

@router.get("/{csv_id}")
async def get_csv(
    csv_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CSV details"""
    csv_service = CSVService(db, user_id)
    csv_upload = csv_service.get_upload(csv_id)
    
    if not csv_upload:
        raise HTTPException(status_code=404, detail="CSV not found")
    
    return csv_upload.to_dict()

@router.delete("/{csv_id}")
async def delete_csv(
    csv_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete CSV"""
    csv_service = CSVService(db, user_id)
    success = csv_service.delete_upload(csv_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="CSV not found")
    
    return {"message": "CSV deleted successfully"}
```

**Add router to `main.py`:**
```python
from app.routers import auth, csv

app.include_router(auth.router)
app.include_router(csv.router)
```

---

## Phase 4: Frontend - CSV Upload UI

### Step 4.1: CSV Upload Hook ⏱️ 45 minutes

**Create `frontend/hooks/useCSVUpload.ts`:**
```typescript
import { useState } from 'react';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export function useCSVUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const uploadCSV = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${api.baseURL}/api/csv/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      const data = await response.json();
      toast.success(`Uploaded ${file.name}`);
      return data;
    } catch (error) {
      toast.error(`Failed to upload ${file.name}`);
      throw error;
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };
  
  const uploadMultiple = async (files: File[]) => {
    const results = [];
    for (const file of files) {
      try {
        const result = await uploadCSV(file);
        results.push(result);
      } catch (error) {
        // Continue with other files
      }
    }
    return results;
  };
  
  return { uploadCSV, uploadMultiple, isUploading, uploadProgress };
}
```

### Step 4.2: CSV Uploader Component ⏱️ 2 hours

**Create `frontend/components/portal/CSVUploader.tsx`:**
```typescript
'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, File, X } from 'lucide-react';
import { useCSVUpload } from '@/hooks/useCSVUpload';

export function CSVUploader({ onUploadComplete }: { onUploadComplete?: () => void }) {
  const [files, setFiles] = useState<File[]>([]);
  const { uploadMultiple, isUploading } = useCSVUpload();
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Filter CSV files only
    const csvFiles = acceptedFiles.filter(f => f.name.endsWith('.csv'));
    
    // Limit to 5 files
    if (files.length + csvFiles.length > 5) {
      toast.error('Maximum 5 files allowed');
      return;
    }
    
    setFiles(prev => [...prev, ...csvFiles]);
  }, [files]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 5,
  });
  
  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };
  
  const handleUpload = async () => {
    await uploadMultiple(files);
    setFiles([]);
    onUploadComplete?.();
  };
  
  return (
    <Card className="p-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-slate-400'}
        `}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
        <p className="text-lg font-medium mb-2">
          {isDragActive ? 'Drop CSV files here' : 'Drag & drop CSV files here'}
        </p>
        <p className="text-sm text-slate-500 mb-4">
          or click to browse (max 5 files, 10MB each)
        </p>
        <Button type="button" variant="secondary">
          Browse Files
        </Button>
      </div>
      
      {files.length > 0 && (
        <div className="mt-6 space-y-2">
          <h3 className="font-medium">Selected Files ({files.length}/5)</h3>
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded">
              <div className="flex items-center gap-3">
                <File className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-slate-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFile(index)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          ))}
          
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            className="w-full mt-4"
          >
            {isUploading ? 'Uploading...' : 'Upload Files'}
          </Button>
        </div>
      )}
    </Card>
  );
}
```

### Step 4.3: Upload Page ⏱️ 1 hour

**Create `frontend/app/portal/upload/page.tsx`:**
```typescript
'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { CSVUploader } from '@/components/portal/CSVUploader';
import { FileList } from '@/components/portal/FileList';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function UploadPage() {
  const router = useRouter();
  const [refreshKey, setRefreshKey] = useState(0);
  
  const handleUploadComplete = () => {
    setRefreshKey(prev => prev + 1);
  };
  
  const handleGenerateSchema = () => {
    router.push('/portal/schema/generate');
  };
  
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Upload CSV Files</h1>
        
        <CSVUploader onUploadComplete={handleUploadComplete} />
        
        <div className="mt-8">
          <FileList key={refreshKey} />
        </div>
        
        <div className="mt-8 flex justify-end">
          <Button onClick={handleGenerateSchema} size="lg">
            Generate Schema →
          </Button>
        </div>
      </div>
    </ProtectedRoute>
  );
}
```

---

## Phase 5: Backend - Schema Generation with LLM

### Step 5.1: Generated Schema Model ⏱️ 30 minutes

**Create `backend/app/models/generated_schema.py`:**
```python
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text, func
from app.database import Base
import uuid

class GeneratedSchema(Base):
    __tablename__ = "generated_schemas"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_session_id = Column(String, ForeignKey("user_sessions.id", ondelete="CASCADE"))
    csv_upload_ids = Column(JSON, nullable=False)
    schema_json = Column(JSON, nullable=False)
    create_statements = Column(JSON, nullable=False)
    llm_reasoning = Column(Text)
    llm_model = Column(String)
    status = Column(String, default="generated")
    created_at = Column(DateTime, server_default=func.now())
    executed_at = Column(DateTime)
    database_path = Column(String)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_session_id": self.user_session_id,
            "csv_upload_ids": self.csv_upload_ids,
            "schema_json": self.schema_json,
            "create_statements": self.create_statements,
            "llm_reasoning": self.llm_reasoning,
            "llm_model": self.llm_model,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "database_path": self.database_path
        }
```

### Step 5.2: LLM Service ⏱️ 1.5 hours

**Create `backend/app/services/llm_service.py`:**
```python
import ollama
from app.config import settings
import json

class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL
    
    async def generate_schema(self, csv_metadata: list[dict]) -> dict:
        """Generate database schema from CSV metadata"""
        prompt = self._build_schema_prompt(csv_metadata)
        
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a database architect. You must respond ONLY with valid JSON, no additional text.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            format='json',
            options={
                'temperature': 0.2,
            }
        )
        
        schema = json.loads(response['message']['content'])
        return schema
    
    def _build_schema_prompt(self, csv_metadata: list[dict]) -> str:
        csv_info = "\n\n".join([
            f"CSV File: {csv['filename']}\n" +
            f"Columns: {', '.join(csv['columns'])}\n" +
            f"Inferred Types: {json.dumps(csv['column_types'], indent=2)}\n" +
            f"Sample Data (first 3 rows):\n{json.dumps(csv['sample_data'][:3], indent=2)}\n" +
            f"Total Rows: {csv['row_count']}"
            for csv in csv_metadata
        ])
        
        return f"""You are a database architect. Generate an optimal SQLite schema based on the following CSV files.

{csv_info}

Your task:
1. Analyze the CSV structures and identify:
   - Optimal primary keys
   - Potential foreign key relationships between tables
   - Appropriate SQLite data types (INTEGER, TEXT, REAL, DATETIME)
   - Necessary constraints (NOT NULL, UNIQUE)

2. Design Principles:
   - Normalize data appropriately (aim for 3NF where beneficial)
   - Create meaningful relationships between tables
   - Use appropriate indexes for common queries
   - Follow SQLite best practices

3. Output Format (JSON):
{{
  "tables": [
    {{
      "name": "table_name",
      "columns": [
        {{
          "name": "column_name",
          "type": "INTEGER|TEXT|REAL|DATETIME",
          "constraints": ["PRIMARY KEY", "NOT NULL", "UNIQUE"],
          "references": {{"table": "other_table", "column": "id"}} or null
        }}
      ]
    }}
  ],
  "relationships": [
    {{
      "from_table": "orders",
      "from_column": "customer_id",
      "to_table": "customers",
      "to_column": "id"
    }}
  ],
  "indexes": [
    {{
      "table": "table_name",
      "columns": ["col1", "col2"],
      "name": "idx_name"
    }}
  ],
  "reasoning": "Detailed explanation of design decisions..."
}}

Generate the schema now:"""
```

### Step 5.3: Schema Generation Service ⏱️ 2 hours

**Create `backend/app/services/schema_generation_service.py`:**
```python
from sqlalchemy.orm import Session
from app.models.csv_upload import CSVUpload
from app.models.generated_schema import GeneratedSchema
from app.services.llm_service import LLMService

class SchemaGenerationService:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.llm_service = LLMService()
    
    async def generate_schema(self, csv_ids: list[str]) -> GeneratedSchema:
        """Generate schema from multiple CSVs"""
        # Fetch CSV metadata
        csv_uploads = self.db.query(CSVUpload).filter(
            CSVUpload.id.in_(csv_ids),
            CSVUpload.user_session_id == self.user_id
        ).all()
        
        if len(csv_uploads) != len(csv_ids):
            raise ValueError("Some CSV IDs not found")
        
        # Prepare metadata for LLM
        csv_metadata = [self._prepare_csv_metadata(csv) for csv in csv_uploads]
        
        # Generate schema with LLM
        schema_data = await self.llm_service.generate_schema(csv_metadata)
        
        # Generate SQL CREATE statements
        create_statements = self._generate_sql_statements(schema_data)
        
        # Save to database
        generated_schema = GeneratedSchema(
            user_session_id=self.user_id,
            csv_upload_ids=csv_ids,
            schema_json=schema_data,
            create_statements=create_statements,
            llm_reasoning=schema_data.get("reasoning", ""),
            llm_model=settings.OLLAMA_MODEL
        )
        
        self.db.add(generated_schema)
        self.db.commit()
        self.db.refresh(generated_schema)
        
        return generated_schema
    
    def _prepare_csv_metadata(self, csv: CSVUpload) -> dict:
        return {
            "filename": csv.original_filename,
            "columns": csv.columns,
            "column_types": csv.column_types,
            "sample_data": csv.sample_data,
            "row_count": csv.row_count
        }
    
    def _generate_sql_statements(self, schema_data: dict) -> list[str]:
        """Convert JSON schema to SQL CREATE statements"""
        statements = []
        
        for table in schema_data.get("tables", []):
            cols = []
            for col in table["columns"]:
                col_def = f"{col['name']} {col['type']}"
                if col.get("constraints"):
                    col_def += " " + " ".join(col["constraints"])
                if col.get("references"):
                    ref = col["references"]
                    col_def += f" REFERENCES {ref['table']}({ref['column']})"
                cols.append(col_def)
            
            create_stmt = f"CREATE TABLE {table['name']} (\n  " + ",\n  ".join(cols) + "\n);"
            statements.append(create_stmt)
        
        # Add index statements
        for idx in schema_data.get("indexes", []):
            idx_stmt = f"CREATE INDEX {idx['name']} ON {idx['table']}({', '.join(idx['columns'])});"
            statements.append(idx_stmt)
        
        return statements
```

### Step 5.4: Schema Router ⏱️ 1 hour

**Create `backend/app/routers/schema.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.services.schema_generation_service import SchemaGenerationService
from app.schemas.schema import GenerateSchemaRequest, SchemaResponse

router = APIRouter(prefix="/api/schema", tags=["Schema Generation"])

@router.post("/generate", response_model=SchemaResponse)
async def generate_schema(
    request: GenerateSchemaRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate schema from CSV files using LLM"""
    service = SchemaGenerationService(db, user_id)
    
    try:
        schema = await service.generate_schema(request.csv_ids)
        return schema.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{schema_id}", response_model=SchemaResponse)
async def get_schema(
    schema_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get generated schema details"""
    # Implementation similar to above
    pass
```

---

## Phase 6: Frontend - Schema Visualization

### Step 6.1: Schema Visualizer Component ⏱️ 3 hours

**Create `frontend/components/portal/SchemaVisualizer.tsx`:**
- Display tables in accordion/card format
- Show columns with types and constraints
- Color-code primary keys and foreign keys
- Editable mode (contentEditable or form fields)
- Highlight relationships

### Step 6.2: Schema Graph Component ⏱️ 2 hours

**Create `frontend/components/portal/SchemaGraph.tsx`:**
- Use React Flow for graph visualization
- Nodes for tables
- Edges for foreign keys
- Interactive (zoom, pan, click)

### Step 6.3: Schema Review Page ⏱️ 2 hours

**Create `frontend/app/portal/schema/review/page.tsx`:**
- Split layout (60/40)
- Tabs for Tables/Graph/SQL views
- LLM reasoning panel
- Approve & Import button

---

## Phase 7: Backend - Database Execution & Data Import

### Step 7.1: Data Service ⏱️ 2 hours

**Create `backend/app/services/data_service.py`:**
- Execute CREATE TABLE statements
- Import CSV data into tables
- Handle transactions
- Validate data integrity

### Step 7.2: Schema Approval Endpoint ⏱️ 1 hour

**Add to `backend/app/routers/schema.py`:**
```python
@router.post("/{schema_id}/approve")
async def approve_schema(
    schema_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve schema and create database"""
    # Execute CREATE statements
    # Import CSV data
    # Update schema status to 'executed'
    pass
```

---

## Phase 8: Backend - Query Agent with Tool Calling

### Step 8.1: Tool Registry ⏱️ 2 hours

**Create `backend/app/tools/sql_executor.py`:**
```python
async def execute_sql_query(
    schema_id: str,
    query: str,
    user_id: str,
    db: Session
) -> dict:
    """Tool for executing SELECT queries"""
    # Validate query (SELECT only)
    # Execute against user database
    # Return results as JSON
    pass
```

**Create `backend/app/tools/data_insert.py`:**
```python
async def insert_data(
    schema_id: str,
    table: str,
    data: dict,
    user_id: str,
    db: Session
) -> dict:
    """Tool for inserting data"""
    # Validate table exists
    # Validate data against schema
    # Execute INSERT
    pass
```

### Step 8.2: Query Agent Service ⏱️ 2 hours

**Create `backend/app/services/query_agent_service.py`:**
```python
import ollama
from app.config import settings
import json

class QueryAgentService:
    def __init__(self, db, user_id: str, schema_id: str):
        self.db = db
        self.user_id = user_id
        self.schema_id = schema_id
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL
        
        # Define available tools
        self.tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'execute_sql_query',
                    'description': 'Execute a SELECT SQL query on the user database and return results',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'The SQL SELECT query to execute'
                            }
                        },
                        'required': ['query']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'insert_data',
                    'description': 'Insert a new row into a table',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'table': {
                                'type': 'string',
                                'description': 'The table name to insert into'
                            },
                            'data': {
                                'type': 'object',
                                'description': 'Key-value pairs representing column names and values'
                            }
                        },
                        'required': ['table', 'data']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'read_schema',
                    'description': 'Get the database schema showing all tables and columns',
                    'parameters': {
                        'type': 'object',
                        'properties': {}
                    }
                }
            }
        ]
    
    async def stream_response(self, messages: list[dict]):
        """Stream responses with tool calling support"""
        # Convert messages to Ollama format
        ollama_messages = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in messages
        ]
        
        # First call with tools
        response = self.client.chat(
            model=self.model,
            messages=ollama_messages,
            tools=self.tools,
            stream=False
        )
        
        # Check if tool calls are needed
        if response.get('message', {}).get('tool_calls'):
            for tool_call in response['message']['tool_calls']:
                function_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                
                # Execute the tool
                tool_result = await self._execute_tool(function_name, arguments)
                
                # Yield tool call info
                yield {
                    'type': 'tool_call',
                    'tool': function_name,
                    'args': arguments
                }
                
                # Add tool result to messages
                ollama_messages.append(response['message'])
                ollama_messages.append({
                    'role': 'tool',
                    'content': json.dumps(tool_result)
                })
            
            # Get final response with tool results
            final_response = self.client.chat(
                model=self.model,
                messages=ollama_messages,
                stream=True
            )
            
            for chunk in final_response:
                if chunk.get('message', {}).get('content'):
                    yield {
                        'type': 'text',
                        'text': chunk['message']['content']
                    }
        else:
            # No tool calls, just stream the response
            yield {
                'type': 'text',
                'text': response['message']['content']
            }
    
    async def _execute_tool(self, tool_name: str, arguments: dict):
        """Execute a tool and return result"""
        from app.tools.sql_executor import execute_sql_query
        from app.tools.data_insert import insert_data
        from app.tools.schema_reader import read_schema
        
        if tool_name == 'execute_sql_query':
            return await execute_sql_query(
                self.schema_id,
                arguments['query'],
                self.user_id,
                self.db
            )
        elif tool_name == 'insert_data':
            return await insert_data(
                self.schema_id,
                arguments['table'],
                arguments['data'],
                self.user_id,
                self.db
            )
        elif tool_name == 'read_schema':
            return await read_schema(
                self.schema_id,
                self.user_id,
                self.db
            )
        else:
            return {'error': f'Unknown tool: {tool_name}'}
```

### Step 8.3: Chat Router ⏱️ 1.5 hours

**Create `backend/app/routers/chat.py`:**
```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat endpoint for querying data"""
    agent = QueryAgentService(db, user_id, request.schema_id)
    
    async def generate():
        async for chunk in agent.stream_response(request.messages):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## Phase 9: Frontend - Query Interface with Vercel AI SDK

### Step 9.1: Chat Interface Component ⏱️ 2 hours

**Create `frontend/components/chat/ChatInterface.tsx`:**
```typescript
'use client';

import { useChat } from 'ai/react';
import { MessageList } from './MessageList';
import { QueryInput } from './QueryInput';

export function ChatInterface({ schemaId }: { schemaId: string }) {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: { schema_id: schemaId },
    onError: (error) => toast.error(error.message)
  });
  
  return (
    <div className="flex flex-col h-screen">
      <MessageList messages={messages} isLoading={isLoading} />
      <QueryInput
        input={input}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  );
}
```

### Step 9.2: Query Page ⏱️ 1 hour

**Create `frontend/app/portal/query/page.tsx`:**
- Layout with header (schema selector)
- ChatInterface component
- Sidebar with query history

---

## Phase 10: Testing & Refinement

### Step 10.1: Backend Unit Tests ⏱️ 3 hours

**Create tests in `backend/tests/`:**
- `test_auth.py`: Authentication flow
- `test_csv.py`: CSV upload and parsing
- `test_schema.py`: Schema generation
- `test_query.py`: Query execution and tools

### Step 10.2: Frontend Testing ⏱️ 2 hours

- Test authentication flow end-to-end
- Test CSV upload with various file sizes
- Test schema generation UI
- Test chat interface

### Step 10.3: Integration Testing ⏱️ 2 hours

- Full user journey (login → upload → schema → query)
- Test error handling
- Test edge cases

### Step 10.4: Documentation ⏱️ 2 hours

**Create:**
- `README.md`: Setup instructions
- `docs/API.md`: API documentation
- `docs/ARCHITECTURE.md`: System architecture
- `docs/DEPLOYMENT.md`: Deployment guide

---

## Phase 11: Deployment Preparation

### Step 11.1: Environment Configuration ⏱️ 1 hour

**Production considerations:**
- Set `DEBUG=False` in production `.env`
- Configure proper CORS origins
- Use strong JWT secret keys
- Ensure Ollama is running and accessible
- Consider Ollama performance (GPU recommended for better response times)
- Set up proper database backups
- Configure rate limiting
- Set up logging and monitoring

**Ollama Deployment Notes:**
- For production, ensure Ollama service is running as a daemon
- Consider using GPU for faster inference (CUDA/ROCm)
- Monitor Ollama memory usage (14B model requires ~8-10GB RAM)
- Can use Ollama API on a separate server if needed
- No API keys or rate limits to worry about

### Step 11.2: Docker Setup (Optional) ⏱️ 2 hours

**Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/databases/app.db
    volumes:
      - ./backend/data:/app/data
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

---

## Timeline Summary

| Phase | Description | Estimated Time |
|-------|-------------|----------------|
| 0 | Project Setup | 2 hours |
| 1 | Backend Auth Migration | 6 hours |
| 2 | Frontend Auth UI | 5 hours |
| 3 | Backend CSV Upload | 4 hours |
| 4 | Frontend CSV UI | 4 hours |
| 5 | Backend Schema Generation | 6 hours |
| 6 | Frontend Schema Visualization | 7 hours |
| 7 | Backend DB Execution | 3 hours |
| 8 | Backend Query Agent | 5.5 hours |
| 9 | Frontend Query Interface | 3 hours |
| 10 | Testing & Refinement | 7 hours |
| 11 | Deployment Prep | 3 hours |
| **Total** | | **~55 hours** |

---

## Milestones

✅ **Milestone 1** (End of Phase 2): Authentication working  
✅ **Milestone 2** (End of Phase 4): CSV upload complete  
✅ **Milestone 3** (End of Phase 6): Schema generation & visualization  
✅ **Milestone 4** (End of Phase 9): Full query interface  
✅ **Milestone 5** (End of Phase 11): Production-ready  

---

## Daily Development Plan (2-3 Weeks)

**Week 1:**
- Day 1: Phase 0-1 (Setup + Backend Auth)
- Day 2: Phase 2 (Frontend Auth)
- Day 3: Phase 3 (Backend CSV)
- Day 4: Phase 4 (Frontend CSV)
- Day 5: Phase 5 (Schema Generation Backend)

**Week 2:**
- Day 6-7: Phase 6 (Schema Visualization)
- Day 8: Phase 7 (DB Execution)
- Day 9-10: Phase 8 (Query Agent)

**Week 3:**
- Day 11: Phase 9 (Query Interface)
- Day 12-13: Phase 10 (Testing)
- Day 14: Phase 11 (Deployment)
- Day 15: Buffer for fixes/polish

---

## Next Steps

1. Review this plan and adjust estimates as needed
2. Set up development environment (Phase 0)
3. Start with Phase 1 (Backend Auth Migration)
4. Test each phase before moving to the next
5. Keep daily progress log
6. Adjust timeline based on actual progress

---

**Ready to start? Begin with Step 0.1!** 🚀
