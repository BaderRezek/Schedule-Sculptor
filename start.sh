#!/bin/bash

# Start Schedule Sculptor with RAG Integration
# This script starts both the Flask backend and React frontend

echo "🎓 Starting Schedule Sculptor with AI Assistant..."

# Usage: ./start.sh [PORT]
# Example: ./start.sh 5001

# Check if we're in the right directory
if [ ! -d "rag" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Default port (use 5001 to avoid macOS services that use 5000)
PORT=${1:-5001}
HOST=${2:-127.0.0.1}

echo "🔧 Will start backend on http://$HOST:$PORT and frontend will use that API URL"

# Ensure user has activated their Python env (we don't auto-activate conda envs)
echo "� Note: Please activate your Python environment (e.g. 'conda activate 422audit') before running this script if required."

# Export the Vite env so the frontend knows where to call
export VITE_API_URL="http://localhost:$PORT"

# Start Flask backend in background with RAG_API_PORT env
cd rag/web
RAG_API_PORT=$PORT RAG_API_HOST=$HOST python app.py &
FLASK_PID=$!
cd ../..

echo "⏳ Waiting for backend to become healthy (timeout 20s)..."
TRIES=0
MAX_TRIES=20
until curl -sSf "http://localhost:$PORT/" >/dev/null 2>&1; do
    TRIES=$((TRIES+1))
    if [ $TRIES -ge $MAX_TRIES ]; then
        echo "❌ Backend did not become healthy after $((MAX_TRIES*1)) seconds. Check logs (PID=$FLASK_PID)."
        echo "   To view logs: tail -n 200 rag/web/*.log || true"
        break
    fi
    sleep 1
done

if [ $TRIES -lt $MAX_TRIES ]; then
    echo "✅ Backend is up at http://localhost:$PORT"

    # Start React frontend
    echo "⚛️  Starting React frontend (Vite) with VITE_API_URL=$VITE_API_URL..."
    cd frontend
    npm run dev &
    VITE_PID=$!
    cd ..

    echo ""
    echo "✅ Both servers are starting!"
    echo "   - Flask API: http://localhost:$PORT"
    echo "   - React App: http://localhost:5173 (or the port Vite selects)"
    echo ""
    echo "📝 To stop both servers, press Ctrl+C"
    echo ""

    # Wait for user to stop
    trap "kill $FLASK_PID $VITE_PID 2>/dev/null; echo '👋 Shutting down...'; exit" INT TERM

    # Keep script running
    wait
else
    echo "⚠️  Frontend not started due to backend health check failure. See message above.";
    echo "If you want to view backend output, run: ps aux | grep app.py";
    trap "kill $FLASK_PID 2>/dev/null; echo '👋 Shutting down...'; exit" INT TERM
    wait $FLASK_PID
fi
