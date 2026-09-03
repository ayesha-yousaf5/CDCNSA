#!/bin/bash
echo "============================================"
echo "  CDCNSA - Starting Server"
echo "============================================"
echo ""

cd "$(dirname "$0")"

echo "Checking port 8000..."
if netstat -ano 2>/dev/null | grep -q ":8000.*LISTENING"; then
    echo ""
    echo "Server is already running on port 8000."
    echo "Opening browser..."
    start http://127.0.0.1:8000 2>/dev/null || xdg-open http://127.0.0.1:8000 2>/dev/null &
    echo ""
    echo "If you want to restart, kill the existing Python process first."
    exit 0
fi

echo "Starting server on http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server."
echo ""

sleep 2
start http://127.0.0.1:8000 2>/dev/null || xdg-open http://127.0.0.1:8000 2>/dev/null &

python server.py
