# 🎨 RightClick AI - Visual Documentation

> A comprehensive visual guide to the RightClick AI platform

---

## 🌐 System Overview

```
                    ┌─────────────────────────────────────────┐
                    │           RIGHTCLICK AI                 │
                    │           UNIFIED PLATFORM              │
                    └──────────────────┬──────────────────────┘
                                       │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
           ▼                          ▼                          ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   🤖 AI BACKEND      │  │   🌐 WEB CLIENT      │  │   📱 MOBILE CLIENT   │
│                      │  │                      │  │                      │
│  ┌────────────────┐  │  │  ┌────────────────┐  │  │  ┌────────────────┐  │
│  │  FastAPI       │  │  │  │  Chrome Ext    │  │  │  │  Android App   │  │
│  │  Python 3.11+  │  │  │  │  JavaScript    │  │  │  │  Kotlin        │  │
│  └────────────────┘  │  │  └────────────────┘  │  │  └────────────────┘  │
│                      │  │                      │  │                      │
│  • JWT Auth          │  │  • Right-click menu  │  │  • Custom keyboard   │
│  • MongoDB Storage   │  │  • Text selection    │  │  • Screenshot OCR    │
│  • RAG Processing    │  │  • Auto-replace      │  │  • Auto-insert       │
│  • Ollama AI         │  │  • Popup interface   │  │  • ML Kit Vision     │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   USER      │────►│   ACTION    │────►│   CLIENT    │
│             │     │             │     │             │
│ • Types text│     │ • Select    │     │ • Chrome    │
│ • Selects   │     │ • Right-click│    │ • Android   │
│ • Captures  │     │ • Screenshot│     │ • API Call  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   OUTPUT    │◄────│    AI       │◄────│   BACKEND   │
│             │     │  PROCESSING │     │             │
│ • Replaced  │     │             │     │ • Auth      │
│   text      │     │ • Ollama    │     │ • RAG       │
│ • Inserted  │     │   LLM       │     │ • Search    │
│   text      │     │ • Vector    │     │ • Response  │
└─────────────┘     │   DB        │     └─────────────┘
                    └─────────────┘
```

---

## 🏛️ Architecture Layers

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │   Chrome Extension  │  │    Android Keyboard   │  │   API Documentation │ │
│  │   ───────────────   │  │    ──────────────     │  │   ───────────────   │ │
│  │   popup.html        │  │    MainActivity       │  │   Swagger UI        │ │
│  │   content.js        │  │    AIKeyboardService  │  │   /docs             │ │
│  │   background.js     │  │    ScreenshotService  │  │   /redoc            │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────┤
│                           APPLICATION LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         FastAPI Application                             ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   ││
│  │  │ Auth Router  │ │ Upload API   │ │ Chat API     │ │ Search API   │   ││
│  │  │ ───────────  │ │ ──────────   │ │ ────────     │ │ ────────     │   ││
│  │  │ /auth/*      │ │ /upload      │ │ /chat        │ │ /search      │   ││
│  │  │ JWT tokens   │ │ /documents   │ │ /chat/direct │ │ /stats       │   ││
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
├────────────────────────────────────────────────────────────────────────────┤
│                           SERVICE LAYER                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      SecureRAGService                                    ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      ││
│  │  │  Document    │ │  Embedding   │ │  Vector      │ │  LLM         │      ││
│  │  │  Processor   │ │  Generator   │ │  Search      │ │  Client      │      ││
│  │  │  ─────────   │ │  ─────────   │ │  ───────     │ │  ───────     │      ││
│  │  │  PDF parsing │ │  Sentence    │ │  Similarity  │ │  Ollama      │      ││
│  │  │  Text chunks │ │  Transformers│ │  matching    │ │  API         │      ││
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
├────────────────────────────────────────────────────────────────────────────┤
│                           DATA LAYER                                        │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐   │
│  │   MongoDB           │  │   SQLite            │  │   File System       │   │
│  │   ───────           │  │   ──────            │  │   ─────────         │   │
│  │   • Documents       │  │   • Users           │  │   • Uploads         │   │
│  │   • Chunks          │  │   • Auth tokens     │  │   • Logs            │   │
│  │   • Embeddings      │  │   • Metadata        │  │   • Vector store    │   │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Feature Comparison Matrix

```
┌──────────────────────────────────┬──────────┬─────────────┬───────────┐
│           FEATURE                │  BACKEND │CHROME EXT   │  ANDROID  │
├──────────────────────────────────┼──────────┼─────────────┼───────────┤
│ 🔐 JWT Authentication            │    ✅    │     ✅      │    ✅     │
│ 📄 Document Upload (PDF/TXT)     │    ✅    │     ✅      │    ✅     │
│ 🔍 Semantic Search (RAG)           │    ✅    │     ✅      │    ✅     │
│ 💬 AI Chat with Context          │    ✅    │     ✅      │    ✅     │
│ 📝 Grammar Correction            │    ✅    │     ✅      │    ✅     │
│ 👔 Professional Tone Rewrite     │    ✅    │     ✅      │    ✅     │
│ 🎯 General AI Replies            │    ✅    │     ✅      │    ✅     │
│ 📖 Text Description              │    ✅    │     ✅      │    ✅     │
├──────────────────────────────────┼──────────┼─────────────┼───────────┤
│ 🖱️ Right-click Context Menu      │    ❌    │     ✅      │    ❌     │
│ 🔄 Auto-replace Web Text         │    ❌    │     ✅      │    ❌     │
│ 📋 Clipboard Copy                │    ❌    │     ✅      │    ✅     │
├──────────────────────────────────┼──────────┼─────────────┼───────────┤
│ ⌨️ Custom Keyboard Input         │    ❌    │     ❌      │    ✅     │
│ 📸 Screenshot Capture            │    ❌    │     ❌      │    ✅     │
│ 🔍 OCR (Text Recognition)        │    ❌    │     ❌      │    ✅     │
│ 🤖 Auto-insert Text              │    ❌    │     ❌      │    ✅     │
│ 📱 Floating AI Button            │    ❌    │     ❌      │    ✅     │
└──────────────────────────────────┴──────────┴─────────────┴───────────┘
```

---

## 🛠️ Technology Stack Visualization

```
Backend Stack                    Chrome Extension Stack          Android Stack
────────────────                 ─────────────────────           ─────────────
                                                                 
┌──────────────┐                 ┌──────────────┐               ┌──────────────┐
│   FastAPI    │                 │  Manifest V3 │               │    Kotlin    │
│   Python     │                 │  Chrome API  │               │   Android    │
└──────┬───────┘                 └──────┬───────┘               └──────┬───────┘
       │                              │                            │
┌──────▼───────┐                 ┌──────▼───────┐               ┌──────▼───────┐
│    JWT       │                 │   Vanilla    │               │    ML Kit    │
│    Auth      │                 │   JavaScript │               │    OCR       │
└──────┬───────┘                 └──────┬───────┘               └──────┬───────┘
       │                              │                            │
┌──────▼───────┐                 ┌──────▼───────┐               ┌──────▼───────┐
│  MongoDB     │                 │   HTML/CSS   │               │   Retrofit   │
│  SQLite      │                 │   Markdown   │               │   OkHttp     │
└──────┬───────┘                 └──────────────┘               └──────┬───────┘
       │                                                             │
┌──────▼───────┐                                               ┌──────▼───────┐
│  Sentence    │                                               │   Encrypted  │
│Transformers  │                                               │   Storage    │
└──────┬───────┘                                               └──────────────┘
       │
┌──────▼───────┐
│   Ollama     │
│   LLM API    │
└──────────────┘
```

---

## 🔄 User Workflow Diagrams

### Chrome Extension Workflow
```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐
│  Select │───►│  Right   │───►│   Send   │───►│ Receive  │───►│ Replace │
│  Text   │    │  Click   │    │  to API  │    │  Response│    │  Text   │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └─────────┘
                    │
                    ▼
            ┌──────────────┐
            │ AI Options:  │
            │ • Fix Grammar│
            │ • RAG Reply  │
            │ • General    │
            │ • Professional│
            │ • Describe   │
            └──────────────┘
```

### Android App Workflow
```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐
│  Open   │───►│  Capture │───►│   OCR    │───►│   Send   │───►│ Insert  │
│Keyboard │    │Screenshot│    │ Extract  │    │  to API  │    │  Text   │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └─────────┘
                                                    │
                    ┌───────────────────────────────┘
                    ▼
            ┌──────────────┐
            │ AI Options:  │
            │ • Reply      │
            │ • Grammar    │
            │ • Professional│
            └──────────────┘
```

---

## 📁 File Structure Tree

```
RightClick-AI/
│
├── 📁 aikeyboard/                           🤖 BACKEND (Python)
│   │
│   ├── 📁 app/                              Application code
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main_secure.py                🚀 FastAPI entry point (418 lines)
│   │   ├── 📄 secure_rag_service.py         🔍 RAG implementation (190 lines)
│   │   ├── 📄 config.py                     ⚙️ Configuration
│   │   ├── 📄 models.py                     📊 Pydantic models
│   │   ├── 📄 chunking.py                   ✂️ Text chunking
│   │   ├── 📄 embeddings.py                 🔢 Vector embeddings
│   │   ├── 📄 storage.py                    💾 File storage
│   │   ├── 📄 logger.py                     📝 Logging
│   │   │
│   │   ├── 📁 auth/                         🔐 Authentication
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 auth_routes.py            Login/Register API
│   │   │   └── 📄 auth_handler.py           JWT handler
│   │   │
│   │   ├── 📁 auth_middleware/              🛡️ Security
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 auth_middleware.py        Token validation
│   │   │
│   │   ├── 📁 database/                     💾 Database
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 db.py                     Connection
│   │   │   └── 📄 models.py                 SQLAlchemy models
│   │   │
│   │   └── 📁 files/                        📁 File handling
│   │       ├── 📄 __init__.py
│   │       └── 📄 file_handler.py
│   │
│   ├── 📄 requirements.txt                  📦 Python deps
│   ├── 📄 docker-compose.yml                🐳 Docker services
│   ├── 📄 Dockerfile                        📋 Container config
│   ├── 📄 .env.example                      📝 Env template
│   └── 📄 README.md                         📖 Backend docs
│
├── 📁 chrome-extension/                     🌐 CHROME EXTENSION
│   │
│   ├── 📄 manifest.json                     📋 Ext config (v3)
│   ├── 📄 background.js                     ⚙️ Service worker
│   ├── 📄 content.js                        📄 Page script (18K)
│   ├── 📄 popup.html                        🎨 Popup UI
│   ├── 📄 popup.js                          ⚡ Popup logic (17K)
│   ├── 📄 popup.css                         🎨 Popup styles
│   ├── 📄 content.css                       🎨 Page styles
│   ├── 📄 test.html                         🧪 Test page
│   ├── 📄 install.sh                        📦 Install script
│   ├── 📄 README.md                         📖 Ext docs
│   └── 📄 INSTALL_GUIDE.md                  📋 Setup guide
│
└── 📁 AIKeyboardAPP/                        📱 ANDROID APP (Kotlin)
    │
    ├── 📁 app/src/main/
    │   │
    │   ├── 📁 java/com/example/aikeyboard/
    │   │   │
    │   │   ├── 📄 MainActivity.kt            🏠 Main UI (371 lines)
    │   │   │
    │   │   ├── 📁 keyboard/                  ⌨️ Keyboard
    │   │   │   ├── 📄 AIKeyboardService.kt   🎹 IME service (555 lines)
    │   │   │   ├── 📄 HistoryAdapter.kt      📜 History list
    │   │   │   └── 📄 HistoryItem.kt         📄 History model
    │   │   │
    │   │   ├── 📁 data/                      💾 Data layer
    │   │   │   ├── 📁 local/
    │   │   │   │   └── 📄 EncryptedPrefsManager.kt  🔐 Secure storage
    │   │   │   ├── 📁 model/
    │   │   │   │   └── 📄 ResumeProfile.kt   👤 User profile
    │   │   │   └── 📁 remote/
    │   │   │       ├── 📄 ApiService.kt      🌐 API interface
    │   │   │       └── 📄 *.kt               📦 API models
    │   │   │
    │   │   ├── 📁 service/                   📸 Screenshot
    │   │   │   └── 📄 ScreenshotService.kt
    │   │   │
    │   │   └── 📁 ui/                        🎨 UI components
    │   │       └── 📁 adapter/
    │   │           └── 📄 DocumentAdapter.kt
    │   │
│   │   └── 📁 res/                         🎨 Resources
│   │       ├── 📁 layout/                  📱 XML layouts
│   │       ├── 📁 values/                  🎨 Themes & strings
│   │       └── 📁 xml/                     ⚙️ Config files
│   │
│   └── 📁 gradle/                          🔧 Gradle config
│
└── 📄 README.md                            📖 THIS FILE
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────┐ │
│  │  User    │─────►│  Login   │─────►│  Verify  │─────►│ JWT  │ │
│  │  Login   │      │  API     │      │Password  │      │Token │ │
│  └──────────┘      └──────────┘      └──────────┘      └──┬───┘ │
│                                                         │      │
│                              ┌──────────────────────────┘      │
│                              ▼                                  │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐              │
│  │  Access  │◄─────│  Bearer  │◄─────│  Send    │              │
│  │  API     │      │  Token   │      │  Token   │              │
│  └──────────┘      └──────────┘      └──────────┘              │
│                                                                 │
│  User Data Isolation:                                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  User A: /uploads/user_a/*  User B: /uploads/user_b/*  │    │
│  │  DB: user_id filtering on all queries                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 API Endpoint Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      API ENDPOINTS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔓 PUBLIC (No Auth Required)                                   │
│  ─────────────────────────────                                  │
│  GET    /                → API Info                             │
│  GET    /health          → Health check                       │
│  POST   /auth/register   → Create account                       │
│  POST   /auth/login      → Get tokens                           │
│  POST   /auth/refresh    → Refresh token                        │
│                                                                 │
│  🔒 PROTECTED (JWT Required)                                    │
│  ───────────────────────────                                    │
│                                                                 │
│  📄 DOCUMENTS                                                   │
│  POST   /upload          → Upload PDF/TXT                       │
│  GET    /documents       → List my documents                    │
│  DELETE /documents/{id}  → Delete document                      │
│                                                                 │
│  🔍 SEARCH & CHAT                                               │
│  POST   /search          → Semantic search                      │
│  POST   /chat            → RAG chat with context                  │
│  POST   /chat/direct     → Direct AI (no RAG)                   │
│                                                                 │
│  📊 STATS                                                       │
│  GET    /stats           → User statistics                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🐳 Docker Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE SERVICES                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Network: ragserver-network (bridge)                      │  │
│  │                                                           │  │
│  │  ┌─────────────┐      ┌─────────────┐      ┌───────────┐ │  │
│  │  │  ragserver  │◄────►│   mongodb   │      │mongo-express│ │  │
│  │  │  ─────────  │      │  ─────────  │      │ ────────── │ │  │
│  │  │  Port: 8000 │      │ Port: 27017 │      │Port: 8081  │ │  │
│  │  │  FastAPI    │      │  Document   │      │  Web UI    │ │  │
│  │  │  + RAG      │      │  Storage    │      │  (Debug)   │ │  │
│  │  └─────────────┘      └─────────────┘      └───────────┘ │  │
│  │         │                                                   │  │
│  │         │  Volumes:                                         │  │
│  │         ├── ./uploads:/app/uploads (user files)             │  │
│  │         ├── ./data:/app/data (vector store)               │  │
│  │         └── ./logs:/app/logs (application logs)           │  │
│  │                                                             │  │
│  │  External: host.docker.internal:11434 (Ollama)              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Use Case Examples

### 1️⃣ Grammar Correction
```
┌─────────────────────────────────────────────────────────────────┐
│ Input:  "i has went to the store yesterday"                      │
│         ▼                                                        │
│ Processing: AI analyzes grammar, spelling, punctuation           │
│         ▼                                                        │
│ Output: "I went to the store yesterday."                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2️⃣ Professional Rewriting
```
┌─────────────────────────────────────────────────────────────────┐
│ Input:  "hey can u help me with this asap??"                    │
│         ▼                                                        │
│ Processing: Formal tone conversion, expand abbreviations         │
│         ▼                                                        │
│ Output: "Hello, could you please assist me with this            │
│          as soon as possible?"                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3️⃣ RAG Reply (with Resume)
```
┌─────────────────────────────────────────────────────────────────┐
│ User uploads: resume.pdf                                          │
│         ▼                                                        │
│ Document stored, chunked, embedded                              │
│         ▼                                                        │
│ Input:  "What projects have you worked on?"                     │
│         ▼                                                        │
│ RAG retrieves relevant chunks from resume                        │
│         ▼                                                        │
│ Output: "I have worked on [projects from resume with context]"  │
└─────────────────────────────────────────────────────────────────┘
```

### 4️⃣ Screenshot OCR (Android)
```
┌─────────────────────────────────────────────────────────────────┐
│ User sees text on another app                                   │
│         ▼                                                        │
│ Tap capture button → Screenshot taken                           │
│         ▼                                                        │
│ ML Kit OCR extracts text                                        │
│         ▼                                                        │
│ AI processes text based on selected mode                       │
│         ▼                                                        │
│ Result inserted at cursor position                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Performance & Scaling

```
┌─────────────────────────────────────────────────────────────────┐
│                   PERFORMANCE CHARACTERISTICS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Backend:                                                       │
│  • Max file size: 10MB                                         │
│  • Chunk size: 1000 chars (200 overlap)                        │
│  • Default top_k: 5 chunks retrieved                           │
│  • Embedding model: all-MiniLM-L6-v2                           │
│  • LLM: llama3.1:8b (grammar), deepseek-coder (general)       │
│                                                                 │
│  Android:                                                       │
│  • Min SDK: 26 (Android 8.0)                                   │
│  • Target SDK: 35                                              │
│  • Network timeout: 300s+ (configurable)                        │
│  • OCR: Google ML Kit (on-device)                              │
│                                                                 │
│  Chrome:                                                        │
│  • Manifest V3 compliant                                        │
│  • Storage: Chrome Storage API                                  │
│  • CORS: Configurable origins                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Checklist

```
□ Backend Deployment
  └── □ Configure .env file
  └── □ Start Docker: docker compose up -d
  └── □ Verify MongoDB connection
  └── □ Test API: curl http://localhost:8000/health
  └── □ Verify Ollama is running locally

□ Chrome Extension
  └── □ Open chrome://extensions/
  └── □ Enable Developer Mode
  └── □ Click "Load unpacked"
  └── □ Select chrome-extension folder
  └── □ Configure server URL in popup
  └── □ Test connection

□ Android App
  └── □ Open in Android Studio
  └── □ Configure server URL in AppConfig
  └── □ Build: ./gradlew assembleDebug
  └── □ Install on device
  └── □ Enable keyboard in Settings
  └── □ Grant screenshot permission
```

---

**📚 For detailed documentation, see:**
- `aikeyboard/README.md` - Backend API docs
- `chrome-extension/README.md` - Extension docs  
- `chrome-extension/INSTALL_GUIDE.md` - Installation guide

**🎨 Visual Documentation v1.0 | RightClick AI Platform**
