#!/bin/bash

# Confluence Finder - Service Management Script
# Purpose: Start, stop, or restart backend and frontend services in Linux environment

echo "==================================="
echo "Confluence Finder Service Management Script"
echo "==================================="

# Check Python and Node.js environments
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found. Please install Python 3.8+ first"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Please install Node.js 16+ first"
    exit 1
fi

# Ensure we're in the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check environment variable file
if [ ! -f "backend/.env" ]; then
    echo "Warning: backend/.env file not found. Creating default configuration..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "Created .env file from .env.example"
        echo "Please ensure correct API keys are configured in the .env file, including KIMI_API_KEY"
    else
        echo "Error: backend/.env.example file not found"
        exit 1
    fi
fi

# Check if Kimi API Key is set
if ! grep -q "KIMI_API_KEY=" backend/.env; then
    echo "Note: KIMI_API_KEY setting not found"
    echo "Please edit the backend/.env file and add the following lines:"
    echo "KIMI_API_KEY=your_kimi_api_key_here"
    echo "LLM_TYPE=kimi"
    echo ""
    read -p "Would you like to set Kimi API Key now? (y/n): " SET_KIMI
    if [ "$SET_KIMI" = "y" ] || [ "$SET_KIMI" = "Y" ]; then
        read -p "Please enter Kimi API Key: " KIMI_KEY
        echo "KIMI_API_KEY=$KIMI_KEY" >> backend/.env
        echo "LLM_TYPE=kimi" >> backend/.env
        echo "Kimi API Key has been set"
    fi
fi

# Define backend startup function
start_backend() {
    echo "==================================="
    echo "Starting backend service..."
    echo "==================================="
    
    cd "$SCRIPT_DIR/backend"
    
    # Check virtual environment
    if [ ! -d "venv" ]; then
        echo "Warning: Virtual environment not found. Using system Python..."
        PYTHON_CMD="python3"
    else
        echo "Using virtual environment..."
        source venv/bin/activate
        PYTHON_CMD="python"
    fi
    
    # Check if app.py exists
    if [ ! -f "app.py" ]; then
        echo "Error: app.py file not found"
        return 1
    fi
    
    # Start backend service (background process)
    echo "Starting backend service..."
    nohup $PYTHON_CMD app.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    
    echo "Backend service PID: $BACKEND_PID"
    echo "Log file: ../backend.log"
    
    # Wait for backend to start
    echo "Waiting for backend service to start..."
    sleep 5
    
    # Check if backend is running
    if ps -p $BACKEND_PID > /dev/null; then
        echo "✅ Backend service started successfully!"
        return 0
    else
        echo "❌ Backend service failed to start!"
        echo "Please check log file: ../backend.log"
        return 1
    fi
}

# Define frontend startup function
start_frontend() {
    echo "==================================="
    echo "Starting frontend service..."
    echo "==================================="
    
    cd "$SCRIPT_DIR/frontend"
    
    # Check package.json
    if [ ! -f "package.json" ]; then
        echo "Error: package.json file not found"
        return 1
    fi
    
    # Start frontend service (background process)
    echo "Starting frontend service..."
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    echo "Frontend service PID: $FRONTEND_PID"
    echo "Log file: ../frontend.log"
    
    # Wait for frontend to start
    echo "Waiting for frontend service to start..."
    sleep 5
    
    # Check if frontend is running
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "✅ Frontend service started successfully!"
        return 0
    else
        echo "❌ Frontend service failed to start!"
        echo "Please check log file: ../frontend.log"
        return 1
    fi
}

# Define stop function
stop_services() {
    echo "==================================="
    echo "Stopping all services..."
    echo "==================================="
    
    # Find and kill backend process
    BACKEND_PID=$(ps aux | grep '[a]pp.py' | awk '{print $2}')
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend service (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        wait $BACKEND_PID 2>/dev/null || true
        echo "✅ Backend service stopped"
    else
        echo "❌ Backend service not found"
    fi
    
    # Find and kill frontend process
    FRONTEND_PID=$(ps aux | grep 'npm run dev' | grep -v grep | awk '{print $2}')
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend service (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        wait $FRONTEND_PID 2>/dev/null || true
        echo "✅ Frontend service stopped"
    else
        echo "❌ Frontend service not found"
    fi
    
    echo "==================================="
    echo "Service stopping completed!"
    echo "==================================="
}

# Define restart function
restart_services() {
    echo "==================================="
    echo "Restarting all services..."
    echo "==================================="
    
    # Stop services first
    stop_services
    
    # Start services after a short delay
    echo "Waiting 2 seconds before restarting..."
    sleep 2
    
    # Start services
    start_all_services
}

# Define start all services function
start_all_services() {
    echo "Starting all services..."
    
    # Create logs directory
    mkdir -p logs
    
    # Start backend
    start_backend
    BACKEND_RESULT=$?
    
    # Start frontend
    start_frontend
    FRONTEND_RESULT=$?
    
    # Display final status
    echo "==================================="
    echo "Service startup completed!"
    echo "==================================="
    
    if [ $BACKEND_RESULT -eq 0 ]; then
        echo "📡 Backend service running at: http://0.0.0.0:5000"
    else
        echo "❌ Backend service failed to start"
    fi
    
    if [ $FRONTEND_RESULT -eq 0 ]; then
        echo "🌐 Frontend service running at: http://localhost:3000"
    else
        echo "❌ Frontend service failed to start"
    fi
    
    echo "==================================="
    echo "Service status checks:"
    echo "- Backend logs: cat backend.log"
    echo "- Frontend logs: cat frontend.log"
    echo "- Stop services: kill <PID>"
    echo "- Restart services: $0 restart"
    echo "==================================="
}

# Main script logic based on argument
case "$1" in
    start)
        start_all_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        echo ""
        echo "Options:"
        echo "  start   - Start backend and frontend services"
        echo "  stop    - Stop all running services"
        echo "  restart - Restart all services"
        echo ""
        # Default to start if no argument provided
        echo "No argument provided, defaulting to 'start'..."
        echo ""
        start_all_services
        ;;
esac