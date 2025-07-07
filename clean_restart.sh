#!/bin/bash
# A script to stop running servers, clean all caches and build artifacts,
# and optionally restart the development servers for QuickScrub.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Function for User Prompts ---
prompt_yes_no() {
    while true; do
        read -p "$1 [y/n]: " yn
        case $yn in
            [Yy]* ) return 0;;  # Success (yes)
            [Nn]* ) return 1;;  # Failure (no)
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# --- 1. Stop Existing Server Instances ---
echo "--- Step 1: Stopping existing server instances ---"
pkill -f "uvicorn QuickScrub.main:app" || echo "No running Uvicorn backend server found."
pkill -f "vite" || echo "No running Vite frontend server found."
echo "All known server processes stopped."
echo ""

# --- 2. Clean Project Artifacts ---
echo "--- Step 2: Cleaning project caches and build artifacts ---"
echo "Removing Python caches and build artifacts..."
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache .eggs *.egg-info build dist
echo "Removing frontend caches and build artifacts..."
rm -rf frontend/node_modules frontend/dist
echo "Project cleanup complete."
echo ""

# --- 3. Optional: Start Servers ---
echo "--- Step 3: Optional Server Restart ---"
if ! prompt_yes_no "Attempt to restart development servers?"; then
    echo "--- Process finished ---"
    exit 0
fi

# --- Helper function for opening a new terminal ---
# Tries common terminal emulators on Linux and provides instructions for others.
open_in_new_terminal() {
    local command_to_run="$1"
    local failed=0

    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "${command_to_run}; exec bash" &
    elif command -v konsole &> /dev/null; then
        konsole -e bash -c "${command_to_run}; exec bash" &
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal -e "bash -c '${command_to_run}; exec bash'" &
    elif [[ "$OSTYPE" == "darwin"* ]]; then # macOS
        osascript -e "tell app \"Terminal\" to do script \"${command_to_run}\""
    else
        failed=1
    fi
    
    if [ $failed -eq 1 ]; then
        echo ""
        echo "--------------------------------------------------------"
        echo "⚠️  Could not automatically open a new terminal."
        echo "Please open a new terminal manually and run:"
        echo "   ${command_to_run}"
        echo "--------------------------------------------------------"
    fi
}

# --- Start Backend ---
if [ ! -d "venv" ]; then
    echo "❌ Error: Python virtual environment 'venv' not found."
    echo "Please run 'python3 -m venv venv' and 'pip install -e .[dev]' first."
    exit 1
fi
backend_cmd="source venv/bin/activate; uvicorn QuickScrub.main:app --reload"
echo "Starting backend server..."
open_in_new_terminal "$backend_cmd"
sleep 2 # Give it a moment to start

# --- Start Frontend ---
if [ ! -d "frontend/node_modules" ]; then
    echo "Warning: 'node_modules' not found in frontend."
    if prompt_yes_no "Run 'npm install' first?"; then
        (pushd frontend && npm install && popd)
    else
        echo "Skipping frontend server start."
        exit 1
    fi
fi
frontend_cmd="cd frontend; npm run dev"
echo "Starting frontend server..."
open_in_new_terminal "$frontend_cmd"

echo ""
echo "--- Process finished ---"