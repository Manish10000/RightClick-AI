#!/bin/bash

# Docker Compose Startup Script for RAG Server

echo "🐳 Starting RAG Server with Docker Compose"
echo "==========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.docker..."
    cp .env.docker .env
    echo "✅ .env file created"
else
    echo "✅ .env file exists"
fi

echo ""
echo "🚀 Starting services..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

# Wait for services
sleep 10

# Check service status
echo "📊 Service Status:"
echo ""
docker-compose ps

echo ""
echo "🔍 Health Checks:"
echo ""

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB is healthy"
else
    echo "⚠️  MongoDB is starting..."
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is healthy"
else
    echo "⚠️  Ollama is starting..."
fi

# Check RAG Server
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ RAG Server is healthy"
else
    echo "⚠️  RAG Server is starting..."
fi

echo ""
echo "==========================================="
echo "🎉 RAG Server is starting!"
echo "==========================================="
echo ""
echo "📡 Access Points:"
echo "   - API Server:    http://localhost:8000"
echo "   - API Docs:      http://localhost:8000/docs"
echo "   - Health Check:  http://localhost:8000/health"
echo "   - MongoDB:       mongodb://localhost:27017"
echo "   - Ollama:        http://localhost:11434"
echo ""
echo "🔧 Management Commands:"
echo "   - View logs:     docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart:       docker-compose restart"
echo ""
echo "⏳ Note: Services may take 1-2 minutes to fully initialize"
echo "   Check status: docker-compose ps"
echo ""
