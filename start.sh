#!/bin/bash

# Start Schedule Sculptor with RAG Integration
# This script starts both the Flask backend and React frontend

echo "🎓 Starting Schedule Sculptor with AI Assistant..."

# Check if we're in the right directory
if [ ! -d "rag" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Start Flask backend in background
echo "🔧 Starting Flask backend on port 5000..."
cd rag/web
python app.py &
FLASK_PID=$!
cd ../..

# Wait a moment for Flask to start
sleep 3

# Start React frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm run dev &
VITE_PID=$!
cd ..

echo ""
echo "✅ Both servers are starting!"
echo "   - Flask API: http://localhost:5000"
echo "   - React App: http://localhost:5173"
echo ""
echo "📝 To stop both servers, press Ctrl+C"
echo ""

# Wait for user to stop
trap "kill $FLASK_PID $VITE_PID 2>/dev/null; echo '👋 Shutting down...'; exit" INT TERM

# Keep script running
wait
