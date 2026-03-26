#!/bin/bash

echo "🔐 Starting AI Keyboard Secure Multi-User Server..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Dependencies installed"
echo ""

# Set environment variables
export DATABASE_URL="sqlite:///./aikeyboard.db"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"
export REFRESH_TOKEN_EXPIRE_DAYS="7"

echo "🚀 Starting server..."
echo ""
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the secure server
uvicorn app.main_secure:app --reload --host 0.0.0.0 --port 8000
