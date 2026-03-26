#!/bin/bash

# Docker Compose Stop Script for RAG Server

echo "🛑 Stopping RAG Server..."
echo "========================="
echo ""

# Stop services
docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💡 To remove volumes (delete all data):"
echo "   docker-compose down -v"
echo ""
