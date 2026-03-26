#!/bin/bash

# Log Viewer Script for RAG Server

show_help() {
    echo "RAG Server Log Viewer"
    echo "===================="
    echo ""
    echo "Usage: ./view_logs.sh [option]"
    echo ""
    echo "Options:"
    echo "  requests    - View all requests (human readable)"
    echo "  errors      - View all errors"
    echo "  detailed    - View detailed JSON logs"
    echo "  live        - Live tail all logs"
    echo "  stats       - Show log statistics"
    echo "  search      - Search logs (requires query)"
    echo "  last        - Show last N requests (default: 10)"
    echo ""
    echo "Examples:"
    echo "  ./view_logs.sh requests"
    echo "  ./view_logs.sh errors"
    echo "  ./view_logs.sh live"
    echo "  ./view_logs.sh last 20"
    echo "  ./view_logs.sh search 'vacation policy'"
}

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo "Error: logs directory not found"
    echo "Make sure the server has been started at least once"
    exit 1
fi

case "$1" in
    requests)
        echo "=== Request Logs ==="
        if [ -f "logs/requests.log" ]; then
            cat logs/requests.log
        else
            echo "No request logs found"
        fi
        ;;
    
    errors)
        echo "=== Error Logs ==="
        if [ -f "logs/errors.log" ]; then
            cat logs/errors.log
        else
            echo "No error logs found"
        fi
        ;;
    
    detailed)
        echo "=== Detailed JSON Logs ==="
        if [ -f "logs/detailed.jsonl" ]; then
            cat logs/detailed.jsonl | python3 -m json.tool 2>/dev/null || cat logs/detailed.jsonl
        else
            echo "No detailed logs found"
        fi
        ;;
    
    live)
        echo "=== Live Logs (Ctrl+C to stop) ==="
        tail -f logs/*.log 2>/dev/null || echo "No logs to tail"
        ;;
    
    stats)
        echo "=== Log Statistics ==="
        echo ""
        
        if [ -f "logs/requests.log" ]; then
            total_requests=$(grep -c "REQUEST" logs/requests.log 2>/dev/null || echo "0")
            echo "Total Requests: $total_requests"
        fi
        
        if [ -f "logs/errors.log" ]; then
            total_errors=$(grep -c "ERROR" logs/errors.log 2>/dev/null || echo "0")
            echo "Total Errors: $total_errors"
        fi
        
        if [ -f "logs/detailed.jsonl" ]; then
            total_lines=$(wc -l < logs/detailed.jsonl 2>/dev/null || echo "0")
            echo "Total Log Entries: $total_lines"
            
            echo ""
            echo "Request Types:"
            grep '"type"' logs/detailed.jsonl | sort | uniq -c | sort -rn
            
            echo ""
            echo "Endpoints:"
            grep '"path"' logs/detailed.jsonl | grep -o '"/[^"]*"' | sort | uniq -c | sort -rn
        fi
        ;;
    
    search)
        if [ -z "$2" ]; then
            echo "Error: Please provide a search query"
            echo "Usage: ./view_logs.sh search 'your query'"
            exit 1
        fi
        
        echo "=== Searching for: $2 ==="
        echo ""
        grep -i "$2" logs/*.log 2>/dev/null || echo "No matches found"
        ;;
    
    last)
        num=${2:-10}
        echo "=== Last $num Requests ==="
        if [ -f "logs/requests.log" ]; then
            grep -A 10 "REQUEST" logs/requests.log | tail -n $((num * 12))
        else
            echo "No request logs found"
        fi
        ;;
    
    *)
        show_help
        ;;
esac
