"""
AI Keyboard - FastAPI Main Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
from typing import List

from app.config import (
    API_TITLE, API_VERSION, API_DESCRIPTION,
    CORS_ORIGINS, UPLOAD_DIR, ALLOWED_EXTENSIONS
)
from app.models import (
    UploadResponse, SearchRequest, SearchResponse, SearchResult,
    ChatRequest, ChatResponse, DocumentListResponse, DocumentInfo,
    StatsResponse, HealthResponse, DeleteResponse
)
from app.rag_service import get_rag_service
from app.middleware import RequestLoggingMiddleware
from app.logger import logger

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Initialize RAG service on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting AI Keyboard API...")
    try:
        get_rag_service()
        logger.info("✅ AI Keyboard API started successfully")
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        raise


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI Keyboard RAG API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        rag_service = get_rag_service()
        health_data = rag_service.health_check()
        return health_data
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats():
    """Get system statistics"""
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a single document
    
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
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {file.filename}")
        
        # Process document
        rag_service = get_rag_service()
        result = rag_service.process_document(str(file_path), file.filename)
        
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


@app.post("/upload/batch", response_model=List[UploadResponse], tags=["Documents"])
async def upload_batch(files: List[UploadFile] = File(...)):
    """
    Upload and process multiple documents
    
    Supported formats: PDF, TXT, MD
    """
    results = []
    
    for file in files:
        try:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue
            
            # Save uploaded file
            file_id = str(uuid.uuid4())
            file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File uploaded: {file.filename}")
            
            # Process document
            rag_service = get_rag_service()
            result = rag_service.process_document(str(file_path), file.filename)
            
            results.append(UploadResponse(
                document_id=result['document_id'],
                file_name=file.filename,
                num_chunks=result['num_chunks'],
                num_pages=result.get('num_pages'),
                message=f"Successfully processed {file.filename}"
            ))
            
        except Exception as e:
            logger.error(f"Failed to process {file.filename}: {e}")
            results.append(UploadResponse(
                document_id="",
                file_name=file.filename,
                num_chunks=0,
                num_pages=0,
                message=f"Failed: {str(e)}"
            ))
    
    return results


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search(request: SearchRequest):
    """
    Semantic search across all documents
    
    Returns the most similar chunks based on embedding similarity
    """
    try:
        rag_service = get_rag_service()
        results = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        search_results = [
            SearchResult(**result) for result in results
        ]
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat with your documents using AI
    
    Uses Ollama for intelligent responses with automatic RAG decision-making
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.chat(
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


@app.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
async def list_documents():
    """
    List all uploaded documents
    """
    try:
        rag_service = get_rag_service()
        documents = rag_service.get_documents()
        
        doc_list = [DocumentInfo(**doc) for doc in documents]
        
        return DocumentListResponse(
            documents=doc_list,
            total_documents=len(doc_list)
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{document_id}", response_model=DeleteResponse, tags=["Documents"])
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks
    """
    try:
        rag_service = get_rag_service()
        deleted = rag_service.delete_document(document_id)
        
        if deleted:
            return DeleteResponse(
                message=f"Document {document_id} deleted successfully",
                document_id=document_id,
                deleted=True
            )
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
