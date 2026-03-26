# AI Keyboard RAG Assistant

A secure, multi-user RAG (Retrieval-Augmented Generation) system with Chrome extension frontend for intelligent document-based conversations.

## Features

- **Multi-user Authentication**: Secure user registration and JWT-based authentication
- **Document Upload & Processing**: Support for PDF and text files with automatic chunking
- **RAG System**: Intelligent document retrieval with vector embeddings
- **Chrome Extension**: Context menu integration for text processing
- **AI Text Processing**: Grammar correction, professional rewriting, and intelligent replies
- **Personalized Responses**: First-person responses based on uploaded documents

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Local Ollama server running (for AI models)
- Chrome browser (for extension)

### 1. Environment Setup

Copy the environment file:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Database
DATABASE_URL=sqlite:///./data/app.db

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,txt,md,docx
```

### 2. Start the Server

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f ragserver
```

The API will be available at `http://localhost:8000`

### 3. Install Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `chrome-extension` folder
4. The extension icon should appear in your toolbar

## API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Document Management

#### Upload Document
```http
POST /upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <file_data>
```

#### List Documents
```http
GET /documents
Authorization: Bearer <access_token>
```

#### Delete Document
```http
DELETE /documents/{document_id}
Authorization: Bearer <access_token>
```

### Chat & RAG

#### RAG Chat (with document context)
```http
POST /chat
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "What have you worked on with Python?",
  "context_chunks": 3,
  "model": "llama3.1:8b"
}
```

#### Direct Chat (no document context)
```http
POST /chat/direct
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "Fix the grammar: 'I are going to store'",
  "model": "deepseek-coder-v2:latest"
}
```

Response format:
```json
{
  "response": "I am going to the store.",
  "sources": [],
  "model": "deepseek-coder-v2:latest",
  "used_rag": false,
  "num_sources": 0
}
```

### Health Check

```http
GET /health
```

## Chrome Extension Usage

### Setup
1. Click the extension icon in Chrome toolbar
2. Configure the base URL (default: `http://localhost:8000`)
3. Register/Login with your credentials
4. Upload documents (PDF, TXT) for RAG functionality

### Text Processing
1. Select any text on a webpage
2. Right-click to open context menu
3. Choose from AI options:
   - **Fix Grammar**: Corrects grammar and spelling
   - **RAG Reply**: Uses your documents to provide contextual responses
   - **General Reply**: Provides general AI responses
   - **Make Professional**: Rewrites text professionally
   - **Describe**: Explains the selected text in detail

### Features
- **Auto-replace**: Selected text is automatically replaced with AI response
- **Clipboard copy**: Results are copied to clipboard
- **Loading indicators**: Visual feedback during processing
- **Popup results**: Describe action shows results in a popup window
- **Markdown rendering**: Properly formatted responses
- **Text selection**: Select and copy parts of AI responses

## Docker Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Rebuild and start
docker compose up -d --build

# View logs
docker compose logs -f ragserver

# Check container status
docker compose ps

# Access container shell
docker compose exec ragserver bash

# Remove all data (reset)
docker compose down -v
```

## Development

### Project Structure
```
aikeyboard/
├── app/                    # FastAPI application
│   ├── auth/              # Authentication modules
│   ├── database/          # Database models and connection
│   ├── files/             # File storage management
│   ├── auth_middleware/   # Authentication middleware
│   ├── main_secure.py     # Main application entry point
│   ├── secure_rag_service.py  # RAG service implementation
│   └── ...
├── chrome-extension/      # Chrome extension files
├── data/                  # SQLite database and vector storage
├── logs/                  # Application logs
├── uploads/               # User uploaded files
├── docker-compose.yml     # Docker services configuration
├── Dockerfile            # Container build instructions
└── requirements.txt      # Python dependencies
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main_secure:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Models
- **Grammar/Professional**: `deepseek-coder-v2:latest`
- **RAG/General**: `llama3.1:8b`

### File Limits
- Max file size: 10MB
- Supported formats: PDF, TXT, MD, DOCX
- Chunk size: 1000 characters
- Chunk overlap: 200 characters

### Security
- JWT-based authentication
- User-isolated data storage
- Secure file upload validation
- CORS protection

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker compose logs ragserver
   ```

2. **Ollama connection failed**
   - Ensure Ollama is running locally
   - Check `OLLAMA_BASE_URL` in `.env`

3. **Extension not working**
   - Reload extension in `chrome://extensions/`
   - Check browser console for errors
   - Verify API server is running

4. **Authentication errors**
   - Check JWT secret key configuration
   - Verify user credentials

5. **File upload fails**
   - Check file size limits
   - Verify file format is supported
   - Check server logs for errors

### Reset Everything
```bash
# Stop and remove all data
docker compose down -v

# Remove images
docker compose down --rmi all

# Start fresh
docker compose up -d --build
```

## Support

For issues and questions:
1. Check the logs: `docker compose logs -f ragserver`
2. Verify configuration in `.env`
3. Test API endpoints with curl or Postman
4. Check Chrome extension console for frontend errors