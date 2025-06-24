#!/bin/bash

# AI Tutoring System - Chatbot Startup Script
echo "🚀 Starting AI Tutoring System Chatbot..."

# Kill any existing servers
echo "📋 Stopping any existing servers..."
pkill -f "uvicorn.*api_server" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
sleep 2

# Start backend API server
echo "🔧 Starting backend API server on port 8000..."
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API server running successfully"
else
    echo "❌ Backend failed to start. Check backend.log"
    exit 1
fi

# Start frontend React server
echo "🎨 Starting frontend React server on port 3000..."
cd frontend
HOST=0.0.0.0 PORT=3000 npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

echo "🎉 Chatbot system started successfully!"
echo ""
echo "📍 Access Methods:"
echo "  1. Local SSH Tunnel (Recommended):"
echo "     ssh -L 3000:localhost:3000 -L 8000:localhost:8000 jain1012@10.165.77.250"
echo "     Then open: http://localhost:3000"
echo ""
echo "  2. Direct Remote Access:"
echo "     Frontend: http://10.165.77.250:3000"
echo "     Backend:  http://10.165.77.250:8000"
echo ""
echo "📊 Server Status:"
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "📋 Useful Commands:"
echo "  - View backend logs: tail -f backend.log"
echo "  - View frontend logs: tail -f frontend.log"
echo "  - Stop servers: pkill -f 'uvicorn\|react-scripts'"
echo "  - Original CLI: python main.py"
echo ""
echo "🎓 Ready to learn! The AI tutor is waiting for you." 