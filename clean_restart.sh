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
pkill -f "vite"            || echo "No running Vite frontend server found."
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

# --- Start Backend (in background) ---
if [ ! -d "venv" ]; then
    echo "❌ Error: Python virtual environment 'venv' not found."
    echo "Please run 'python3 -m venv venv' and 'pip install -e .[dev]' first."
    exit 1
fi

echo "Starting backend server (in background)..."
# activate venv in this shell
source venv/bin/activate
# launch uvicorn in the background
uvicorn QuickScrub.main:app --reload &
BACKEND_PID=$!
sleep 2  # give it a moment to come up

# --- Start Frontend ---
if [ ! -d "frontend/node_modules" ]; then
    echo "Warning: 'node_modules' not found in frontend."
    if prompt_yes_no "Run 'npm install' first?"; then
        (cd frontend && npm install)
    else
        echo "Skipping frontend server start."
        # optional: kill backend if you want
        # kill $BACKEND_PID
        exit 1
    fi
fi

echo "Starting frontend server..."
cd frontend
npm run dev

# When npm run dev exits (e.g. you Ctrl+C), forward the signal to the backend
trap "echo; echo 'Stopping backend...'; kill $BACKEND_PID; exit" INT TERM

# wait on backend if npm dev ever exits cleanly
wait $BACKEND_PID
