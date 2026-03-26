"""
AI Keyboard - Secure Multi-User FastAPI Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from sqlalchemy.orm import Session
from typing import List

from app.config import API_TITLE, API_VERSION, CORS_ORIGINS, ALLOWED_EXTENSIONS
from app.database.db import get_db, init_db
from app.database.models import User
from app.auth_middleware.auth_middleware import get_current_user
from app.auth.auth_routes import router as auth_router
from app.secure_rag_service import get_secure_rag_service
from app.logger import logger

# Pydantic models
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# API Models
class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    num_chunks: int
    num_pages: Optional[int] = None
    message: str


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, ge=1, le=50)
    similarity_threshold: float = Field(0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    content: str
    file_path: str
    chunk_index: int
    score: float
    metadata: dict = {}


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int


class ChatRequest(BaseModel):
    message: str
    context_chunks: int = Field(3, ge=1, le=10)
    model: str = "llama3.1:8b"


class ChatResponse(BaseModel):
    response: str
    sources: List[SearchResult]
    model: str
    used_rag: bool
    num_sources: int


class DocumentInfo(BaseModel):
    id: str
    file_name: str
    file_path: str
    num_chunks: int
    total_pages: Optional[int]
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_documents: int


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_size_bytes: int
    documents: List[DocumentInfo]


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    embedding_model: str
    user_id: Optional[int] = None


# Create FastAPI app
app = FastAPI(
    title=f"{API_TITLE} - Secure Multi-User",
    version=API_VERSION,
    description="""
AI Keyboard - Secure Multi-User RAG API with JWT Authentication

## Features
- 🔐 JWT-based authentication (Access + Refresh tokens)
- 👤 User registration and login
- 🔒 User-isolated data storage
- 📁 Secure file upload and management
- 🔍 User-scoped semantic search
- 💬 AI chat with user's documents
- 🛡️ Protected API endpoints

## Authentication
All endpoints (except /auth/*) require authentication.
Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```
"""
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting AI Keyboard Secure API...")
    try:
        init_db()
        get_secure_rag_service()
        logger.info("✅ AI Keyboard Secure API started successfully")
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        raise


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI Keyboard Secure Multi-User RAG API",
        "version": API_VERSION,
        "docs": "/docs",
        "authentication": "Required for all endpoints except /auth/*"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    🔓 Public endpoint (no authentication required)
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
        return HealthResponse(
            status="healthy",
            database_connected=True,
            embedding_model="all-MiniLM-L6-v2",
            user_id=None  # No user ID for public health check
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's statistics
    
    🔒 Requires authentication
    Returns only the current user's data
    """
    try:
        rag_service = get_secure_rag_service()
        stats = rag_service.get_user_stats(db, current_user)
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document
    
    🔒 Requires authentication
    File is stored in user's isolated directory
    
    Supported formats: PDF, TXT, MD
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        logger.info(f"User {current_user.id} uploading: {file.filename}")
        
        # Process document (user-isolated)
        rag_service = get_secure_rag_service()
        result = rag_service.process_document(
            db=db,
            user=current_user,
            file_path=file.filename,
            file_name=file.filename,
            file_content=file.file
        )
        
        return UploadResponse(
            document_id=result['document_id'],
            file_name=file.filename,
            num_chunks=result['num_chunks'],
            num_pages=result.get('num_pages'),
            message=f"Successfully processed {file.filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Semantic search across user's documents
    
    🔒 Requires authentication
    Returns only results from the current user's documents
    """
    try:
        rag_service = get_secure_rag_service()
        results = rag_service.search(
            db=db,
            user=current_user,
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        search_results = [SearchResult(**result) for result in results]
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with your documents using AI (with intelligent RAG decision-making)
    
    🔒 Requires authentication
    Uses only the current user's documents for context
    """
    try:
        rag_service = get_secure_rag_service()
        result = rag_service.chat(
            db=db,
            user=current_user,
            message=request.message,
            context_chunks=request.context_chunks,
            model=request.model
        )
        
        sources = [SearchResult(**s) for s in result['sources']]
        
        return ChatResponse(
            response=result['response'],
            sources=sources,
            model=result['model'],
            used_rag=result['used_rag'],
            num_sources=result['num_sources']
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/direct", response_model=ChatResponse, tags=["Chat"])
async def chat_direct(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Direct AI chat without RAG (no document context)
    
    🔒 Requires authentication
    Bypasses RAG decision-making and goes directly to AI
    """
    try:
        rag_service = get_secure_rag_service()
        result = rag_service.chat_direct(
            message=request.message,
            model=request.model
        )
        
        return ChatResponse(
            response=result['response'],
            sources=[],  # No sources for direct chat
            model=result['model'],
            used_rag=False,
            num_sources=0
        )
        
    except Exception as e:
        logger.error(f"Direct chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's uploaded documents
    
    🔒 Requires authentication
    Returns only the current user's documents
    """
    try:
        rag_service = get_secure_rag_service()
        documents = rag_service.get_user_documents(db, current_user)
        
        doc_list = [DocumentInfo(**doc) for doc in documents]
        
        return DocumentListResponse(
            documents=doc_list,
            total_documents=len(doc_list)
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{document_id}", tags=["Documents"])
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document
    
    🔒 Requires authentication
    Can only delete the current user's documents
    """
    try:
        rag_service = get_secure_rag_service()
        deleted = rag_service.delete_document(db, current_user, document_id)
        
        if deleted:
            return {
                "message": f"Document {document_id} deleted successfully",
                "document_id": document_id,
                "deleted": True
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
