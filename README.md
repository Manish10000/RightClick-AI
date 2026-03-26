# 🚀 RightClick AI - Project Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RIGHTCLICK AI PLATFORM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │   🤖 AI Backend   │◄──►│  🌐 Chrome Ext   │    │  📱 Android App  │  │
│  │   (Python/FastAPI)│    │   (JavaScript)   │    │    (Kotlin)      │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│           │                       │                       │            │
│           ▼                       ▼                       ▼            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    🔐 SHARED FEATURES                             │  │
│  │  • Multi-user Authentication (JWT)  • Document RAG Processing     │  │
│  │  • AI Text Processing               • Secure Data Isolation       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
RightClick-AI/
│
├── 📂 aikeyboard/                    # 🤖 Python Backend (RAG Server)
│   ├── app/
│   │   ├── main_secure.py            # FastAPI main application
│   │   ├── secure_rag_service.py     # RAG service implementation
│   │   ├── auth/                     # JWT authentication
│   │   ├── database/                 # SQLAlchemy models & connection
│   │   └── files/                    # File upload handling
│   ├── docker-compose.yml            # MongoDB + API services
│   ├── Dockerfile                    # Container configuration
│   └── requirements.txt              # Python dependencies
│
├── 📂 chrome-extension/              # 🌐 Chrome Browser Extension
│   ├── manifest.json                 # Extension manifest (v3)
│   ├── background.js                 # Service worker
│   ├── content.js                    # Page content script
│   ├── popup.html/js/css             # Extension popup UI
│   └── icons/                        # Extension icons
│
└── 📂 AIKeyboardAPP/                 # 📱 Android Keyboard Application
    ├── app/src/main/
    │   ├── java/com/example/aikeyboard/
    │   │   ├── MainActivity.kt       # Main app interface
    │   │   ├── keyboard/             # Custom keyboard service
    │   │   │   └── AIKeyboardService.kt
    │   │   ├── data/                 # Data models & API
    │   │   └── service/              # Screenshot service
    │   └── res/                      # Android resources
    └── build.gradle.kts              # Gradle configuration
```

## 🎯 Core Features

| Feature | Backend | Chrome Ext | Android |
|---------|:-------:|:----------:|:-------:|
| 🔐 JWT Authentication | ✅ | ✅ | ✅ |
| 📄 Document Upload | ✅ | ✅ | ✅ |
| 🔍 RAG Search | ✅ | ✅ | ✅ |
| 💬 AI Chat | ✅ | ✅ | ✅ |
| 📝 Grammar Fix | ✅ | ✅ | ✅ |
| 👔 Professional Rewrite | ✅ | ✅ | ✅ |
| 🖱️ Right-click Menu | ❌ | ✅ | ❌ |
| ⌨️ Keyboard Input | ❌ | ❌ | ✅ |
| 📸 Screenshot OCR | ❌ | ❌ | ✅ |

## 🏗️ Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Chrome Extension                    Android App               │
│  ─────────────────                   ───────────               │
│  1. Select text on page              1. Type in any app         │
│  2. Right-click → AI options         2. Tap keyboard AI button   │
│  3. Text sent to API                 3. Screenshot captured    │
│  4. Auto-replace on page             4. OCR extracts text       │
│                                      5. AI processes & inserts   │
│                                                                 │
│                          ┌─────────┐                            │
│                          │  API    │                            │
│                          │  Layer  │                            │
│                          └───┬─────┘                            │
│                              │                                  │
│          ┌───────────────────┼───────────────────┐              │
│          ▼                   ▼                   ▼              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│   │  Document   │    │   RAG/AI    │    │    Auth     │       │
│   │   Store     │───►│  Processing │◄───│   (JWT)     │       │
│   └─────────────┘    └──────┬──────┘    └─────────────┘       │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                         │
│                    │  Ollama LLM     │                         │
│                    │  (Local AI)     │                         │
│                    └─────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend (`aikeyboard/`)
- **Framework**: FastAPI (Python)
- **Database**: MongoDB + SQLite
- **AI/ML**: Sentence Transformers, Ollama
- **Auth**: JWT with password hashing
- **Deployment**: Docker & Docker Compose

### Chrome Extension (`chrome-extension/`)
- **Manifest**: V3
- **Scripts**: Vanilla JavaScript
- **UI**: HTML/CSS with markdown rendering
- **Storage**: Chrome Storage API

### Android App (`AIKeyboardAPP/`)
- **Language**: Kotlin
- **SDK**: Android API 26+ (Android 8.0+)
- **ML**: Google ML Kit (OCR)
- **Networking**: Retrofit + OkHttp
- **Security**: Encrypted SharedPreferences

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local dev)
- Chrome Browser
- Android Studio (for mobile app)
- Local Ollama server

### 1. Start Backend
```bash
cd aikeyboard
cp .env.example .env
docker compose up -d
```

### 2. Install Chrome Extension
```bash
# Open chrome://extensions/
# Enable Developer Mode
# Click "Load unpacked"
# Select chrome-extension folder
```

### 3. Build Android App
```bash
cd AIKeyboardAPP
./gradlew assembleDebug
# Or open in Android Studio
```

## 📡 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/auth/register` | POST | No | User registration |
| `/auth/login` | POST | No | User login |
| `/upload` | POST | Yes | Document upload |
| `/documents` | GET | Yes | List documents |
| `/chat` | POST | Yes | RAG chat |
| `/chat/direct` | POST | Yes | Direct AI chat |

## 🔒 Security Features

- ✅ JWT-based authentication (Access + Refresh tokens)
- ✅ User-isolated data storage
- ✅ Encrypted credentials (Android)
- ✅ Secure file upload validation
- ✅ CORS protection
- ✅ Password hashing with bcrypt

## 📝 Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./data/app.db
MONGO_URI=mongodb://admin:pass@mongodb:27017/

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,txt,md,docx
```

## 🌟 Key Capabilities

### 1. Grammar Correction
```
Input:  "i want some good food"
Output: "I want some good food."
```

### 2. Professional Rewriting
```
Input:  "hey can u help me"
Output: "Hello, could you please assist me?"
```

### 3. RAG Replies
```
Input:  "What have you worked on?"
Output: Personalized response based on uploaded resume
```

### 4. Screenshot OCR (Android)
```
Action: Capture screen → OCR extract → AI process → Auto-insert
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `ragserver` | 8000 | FastAPI application |
| `mongodb` | 27017 | Document & vector storage |
| `mongo-express` | 8081 | MongoDB web UI (debug) |

## 📱 Android Keyboard Features

- 🤖 AI reply generation with screenshot context
- 📄 Document upload & management
- 📸 Screen capture with OCR
- 🔄 Multiple AI modes (Grammar, Professional, RAG)
- ⌨️ Full QWERTY keyboard layout
- 📋 Clipboard integration

## 🌐 Chrome Extension Features

- 🖱️ Right-click context menu integration
- 📝 5 AI actions: Grammar, RAG Reply, General Reply, Professional, Describe
- 🔄 Auto-replace selected text
- 📋 Clipboard copy
- 🔐 Secure login with JWT
- 📄 Document upload popup

## 📊 Project Statistics

| Component | Files | Lines of Code | Language |
|-----------|-------|---------------|----------|
| Backend | 15+ | 5000+ | Python |
| Chrome Ext | 9 | 3000+ | JavaScript |
| Android | 20+ | 8000+ | Kotlin |

---

**Built with ❤️ for AI-powered productivity**

- Backend: FastAPI + MongoDB + Ollama
- Frontend: Chrome Extension + Android Keyboard
- License: Private Project
