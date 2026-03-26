#!/bin/bash

# AI Keyboard RAG Assistant - Chrome Extension Installation Helper

echo "🚀 AI Keyboard RAG Assistant - Chrome Extension Setup"
echo "=================================================="

# Check if icons exist
if [ ! -f "icons/icon16.png" ] || [ ! -f "icons/icon48.png" ] || [ ! -f "icons/icon128.png" ]; then
    echo "⚠️  WARNING: Icon files are missing!"
    echo "Please add the following files to the icons/ directory:"
    echo "  - icon16.png (16x16 pixels)"
    echo "  - icon48.png (48x48 pixels)" 
    echo "  - icon128.png (128x128 pixels)"
    echo ""
    echo "You can create simple icons or use any PNG images."
    echo "The extension will not load without these files."
    echo ""
fi

echo "📋 Installation Steps:"
echo "1. Open Chrome and go to chrome://extensions/"
echo "2. Enable 'Developer mode' (toggle in top right)"
echo "3. Click 'Load unpacked'"
echo "4. Select this folder: $(pwd)"
echo ""

echo "🔧 Start RAG Server First:"
echo "cd ../aikeyboard"
echo "python -m uvicorn app.main_secure:app --reload --host 0.0.0.0 --port 8000"
echo ""

echo "⚙️  Configuration Steps:"
echo "1. Click the extension icon in Chrome toolbar"
echo "2. Go to 'Settings' tab"
echo "3. Set Base URL (default: http://localhost:8000)"
echo "4. Click 'Test Connection' to verify server"
echo ""

echo "🔐 Authentication (Required for secure mode):"
echo "1. Go to 'Account' tab in extension popup"
echo "2. Register new account or login"
echo "3. This enables user-isolated document storage"
echo ""

echo "📄 Upload Documents:"
echo "1. Go to 'Upload PDF' tab"
echo "2. Upload PDF, TXT, or MD files (max 50MB each)"
echo "3. Documents will be available for RAG replies"
echo ""

echo "✨ Usage:"
echo "1. Select any text on any webpage"
echo "2. Right-click to open context menu"
echo "3. Choose from 'AI Keyboard Assistant' options:"
echo "   - Fix Grammar (corrects spelling/grammar)"
echo "   - RAG Reply (uses your uploaded documents)"
echo "   - General Reply (general AI response)"
echo "   - Make Professional & Polite (rewrites professionally)"
echo ""

echo "🧪 Testing:"
echo "Open test.html in your browser to test all features"
echo ""

echo "🚨 Troubleshooting:"
echo "- Context menu not appearing: Refresh webpage and try again"
echo "- No AI response: Check if RAG server is running"
echo "- Authentication errors: Login through extension popup"
echo "- RAG replies not working: Upload documents first"
echo ""

echo "✅ Setup complete! Follow the installation steps above."
echo "📖 See README.md for detailed documentation."