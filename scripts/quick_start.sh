#!/bin/bash

# Quick Start Script for Activity Recorder
# This script starts both the backend API server and frontend web interface

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required commands are available
check_dependencies() {
    local missing_deps=()

    if ! command -v uv &> /dev/null; then
        missing_deps+=("uv")
    fi

    if ! command -v node &> /dev/null; then
        missing_deps+=("node (required for React frontend)")
    fi

    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm (required for React frontend)")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Please install the missing dependencies and try again."
        exit 1
    fi
}

# Install backend dependencies if needed
install_backend_deps() {
    print_info "Checking backend dependencies..."

    if [ ! -f "$BACKEND_DIR/.deps_installed" ]; then
        print_info "Installing backend dependencies using uv..."
        cd "$BACKEND_DIR"

        if uv sync; then
            print_success "Backend dependencies installed successfully"
        else
            print_error "Failed to install backend dependencies"
            exit 1
        fi

        cd "$PROJECT_ROOT"
    else
        print_info "Backend dependencies already installed"
    fi
}

# Install frontend dependencies if needed
install_frontend_deps() {
    print_info "Checking frontend dependencies..."

    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        print_info "Installing frontend dependencies using npm..."
        cd "$FRONTEND_DIR"

        if npm install; then
            print_success "Frontend dependencies installed successfully"
        else
            print_error "Failed to install frontend dependencies"
            exit 1
        fi

        cd "$PROJECT_ROOT"
    else
        print_info "Frontend dependencies already installed"
    fi
}

# Start backend server
start_backend() {
    print_info "Starting backend server..."
    cd "$BACKEND_DIR"

    # Check if backend is already running
    if curl -s http://localhost:8000/ > /dev/null; then
        print_warning "Backend server is already running on port 8000"
        return 0
    fi

    # Start backend in background using uv
    uv run python -m app.main &
    BACKEND_PID=$!

    # Wait for backend to start
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/ > /dev/null; then
            print_success "Backend server started successfully (PID: $BACKEND_PID)"
            echo $BACKEND_PID > /tmp/activity_recorder_backend.pid
            return 0
        fi

        print_info "Waiting for backend to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    print_error "Backend server failed to start within 60 seconds"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
}

# Start frontend server
start_frontend() {
    print_info "Starting frontend development server..."
    cd "$FRONTEND_DIR"

    # Start React development server using npm run dev
    npm run dev &
    FRONTEND_PID=$!
    FRONTEND_PORT=3000  # Configured in vite.config.js

    # Wait for frontend to start
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$FRONTEND_PORT/ > /dev/null; then
            print_success "Frontend development server started successfully (PID: $FRONTEND_PID)"
            echo $FRONTEND_PID > /tmp/activity_recorder_frontend.pid
            return 0
        fi

        print_info "Waiting for frontend to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    print_error "Frontend server failed to start within 60 seconds"
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
}

# Cleanup function
cleanup() {
    print_info "Cleaning up..."

    if [ -f /tmp/activity_recorder_backend.pid ]; then
        local backend_pid=$(cat /tmp/activity_recorder_backend.pid)
        if kill -0 $backend_pid 2>/dev/null; then
            print_info "Stopping backend server (PID: $backend_pid)"
            kill $backend_pid
        fi
        rm -f /tmp/activity_recorder_backend.pid
    fi

    if [ -f /tmp/activity_recorder_frontend.pid ]; then
        local frontend_pid=$(cat /tmp/activity_recorder_frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            print_info "Stopping frontend server (PID: $frontend_pid)"
            kill $frontend_pid
        fi
        rm -f /tmp/activity_recorder_frontend.pid
    fi
}

# Trap signals for cleanup
trap cleanup EXIT INT TERM

# Main execution
main() {
    print_info "Starting Activity Recorder Quick Start..."
    print_info "Project Root: $PROJECT_ROOT"

    # Check dependencies
    check_dependencies

    # Install backend dependencies if needed
    install_backend_deps

    # Start services
    start_backend
    start_frontend

    print_success "========================================"
    print_success "Activity Recorder is now running!"
    print_success "========================================"
    print_info "Backend API: http://localhost:8000"
    print_info "Frontend UI: http://localhost:3000"
    print_info ""
    print_info "To stop the servers, press Ctrl+C"
    print_info ""

    # Wait for user interrupt
    print_info "Servers are running. Press Ctrl+C to stop..."
    wait
}

# Run main function
main