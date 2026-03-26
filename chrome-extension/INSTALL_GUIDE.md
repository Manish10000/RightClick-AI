# 🚀 Chrome Extension Installation Guide

## ✅ Prerequisites Complete
- ✅ Icon files created (16x16, 48x48, 128x128)
- ✅ JavaScript syntax errors fixed
- ✅ All extension files ready

## 📋 Installation Steps

### 1. Open Chrome Extensions Page
- Open Google Chrome
- Go to `chrome://extensions/`
- Or click: Menu (⋮) → More Tools → Extensions

### 2. Enable Developer Mode
- Toggle "Developer mode" switch in the top right corner
- This enables the "Load unpacked" button

### 3. Load the Extension
- Click "Load unpacked" button
- Navigate to and select the `chrome-extension` folder
- The extension should load successfully

### 4. Verify Installation
- Look for "AI Keyboard RAG Assistant" in your extensions list
- You should see a green icon in the Chrome toolbar
- Status should show "Enabled"

## ⚙️ Configuration

### 1. Click Extension Icon
- Click the green AI Keyboard icon in Chrome toolbar
- The popup window will open

### 2. Configure Server Settings
- Go to "Settings" tab
- Set Base URL: `http://localhost:8000` (default)
- Click "Test Connection" to verify

### 3. Create Account (Optional but Recommended)
- Go to "Account" tab
- Click "Register" to create new account
- Or "Login" if you already have one
- This enables document upload and RAG features

### 4. Upload Documents (Optional)
- Go to "Upload PDF" tab
- Upload PDF, TXT, or MD files
- These will be used for RAG replies

## 🧪 Test the Extension

### 1. Open Test Page
- Open `chrome-extension/test.html` in Chrome
- This page has sample text for testing

### 2. Test Context Menu
- Select any text on the test page
- Right-click to open context menu
- Look for "AI Keyboard Assistant" submenu
- Try all 4 options:
  - Fix Grammar
  - RAG Reply
  - General Reply
  - Make Professional & Polite

### 3. Test on Any Website
- Go to any website (news, blog, etc.)
- Select text and right-click
- Use the AI Keyboard Assistant options

## 🎯 Expected Behavior

### ✅ Working Correctly:
- Context menu appears when text is selected
- AI responses appear in floating windows
- Can copy or replace text with AI suggestions
- Extension popup shows server connection status
- Document upload works (if logged in)

### ❌ Troubleshooting:
- **No context menu**: Refresh the webpage and try again
- **No AI response**: Check if RAG server is running on localhost:8000
- **Upload fails**: Make sure you're logged in first
- **Connection error**: Verify server URL in extension settings

## 🔧 Server Requirements

Make sure your RAG server is running:
```bash
cd aikeyboard
./start-with-local-ollama.sh
```

Or manually:
```bash
# Start Ollama
ollama serve

# Start RAG server
cd aikeyboard
docker compose up -d
```

## 🎉 Success!

If everything works correctly, you now have:
- ✅ AI-powered text assistance on any webpage
- ✅ 4 different AI processing modes
- ✅ Document upload for RAG functionality
- ✅ Secure user authentication
- ✅ Copy/replace text functionality

**Enjoy your AI-powered browsing experience!** 🚀