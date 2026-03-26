"""
Configuration for AI Keyboard RAG Server
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = DATA_DIR / "vectordb"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)

# MongoDB Configuration (legacy - for backward compatibility)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "aikeyboard")
COLLECTION_NAME = "nodes"

# SQL Database Configuration (for multi-user auth)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./aikeyboard.db"  # SQLite for development
    # For production PostgreSQL: "postgresql://user:password@localhost/aikeyboard"
    # For production MySQL: "mysql+pymysql://user:password@localhost/aikeyboard"
)

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384

# Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval Configuration
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.0"))

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# API Configuration
API_TITLE = "AI Keyboard RAG API"
API_VERSION = "2.0.0"  # Updated for multi-user support
API_DESCRIPTION = """
AI Keyboard - Portable RAG (Retrieval-Augmented Generation) API Server with Multi-User Support.

Features:
- 🔐 JWT-based authentication (Access + Refresh tokens)
- 👤 User registration and login
- 🔒 User-isolated data storage
- 📁 Upload and process PDF/text documents
- 🔍 Semantic search with embeddings (user-scoped)
- 💬 AI-powered chat with documents using Ollama (user-scoped)
- 📊 Document management (user-scoped)
- 🛡️ Secure multi-user architecture
- 🚀 Fully portable - works on any laptop with Docker
"""

# File Upload Configuration
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Security
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
