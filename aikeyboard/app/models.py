"""
Pydantic models for AI Keyboard API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UploadResponse(BaseModel):
    """Response for file upload"""
    document_id: str
    file_name: str
    num_chunks: int
    num_pages: Optional[int] = None
    message: str


class SearchRequest(BaseModel):
    """Request for semantic search"""
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, description="Number of results to return", ge=1, le=50)
    similarity_threshold: float = Field(0.0, description="Minimum similarity score", ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Single search result"""
    content: str
    file_path: str
    chunk_index: int
    score: float
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    """Response for search"""
    query: str
    results: List[SearchResult]
    total_results: int


class ChatRequest(BaseModel):
    """Request for chat"""
    message: str = Field(..., description="User message")
    context_chunks: int = Field(3, description="Number of context chunks", ge=1, le=10)
    model: str = Field("llama3.1:8b", description="Ollama model to use")


class ChatResponse(BaseModel):
    """Response for chat"""
    response: str
    sources: List[SearchResult]
    model: str
    used_rag: bool
    num_sources: int


class DocumentInfo(BaseModel):
    """Document information"""
    id: str
    file_name: str
    file_path: str
    num_chunks: int
    total_pages: Optional[int] = 0
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    """Response for document list"""
    documents: List[DocumentInfo]
    total_documents: int


class StatsResponse(BaseModel):
    """System statistics"""
    total_documents: int
    total_chunks: int
    total_size_bytes: int
    documents: List[DocumentInfo]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    mongodb_connected: bool
    ollama_available: bool
    embedding_model: str
    total_documents: int
    total_chunks: int


class DeleteResponse(BaseModel):
    """Response for document deletion"""
    message: str
    document_id: str
    deleted: bool
