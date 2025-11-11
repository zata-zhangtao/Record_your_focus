#!/bin/bash
# Native host launcher script for Linux/macOS

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go to project root (two levels up: native_host -> browser_extension -> project_root)
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to project directory
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the native host with Python
exec python3 native_host.py 2>> "$SCRIPT_DIR/native_host_error.log"
