#!/bin/bash
# A robust script to stop, clean, and restart QuickScrub development servers.

# --- Configuration ---
# Use color codes for better readability
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helper Functions ---
prompt_yes_no() {
    # A robust prompt function that ensures clean input
    while true; do
        read -p "$(echo -e "${YELLOW}$1 [y/n]: ${NC}")" yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# This function will be called on script exit to clean up background processes
cleanup() {
    if [ -n "$BACKEND_PID" ]; then
        # Check if the process is still running before trying to kill it
        if ps -p $BACKEND_PID > /dev/null; then
            echo -e "\n${BLUE}--- Cleaning up background backend server (PID: $BACKEND_PID) ---${NC}"
            kill $BACKEND_PID
        fi
    fi
    # A final check to ensure all related processes are gone
    kill_processes >/dev/null 2>&1
    echo -e "${GREEN}Cleanup complete. Exiting.${NC}"
}

# Kills processes without printing errors if they don't exist
kill_processes() {
    # Find PIDs for uvicorn and vite, avoiding the grep process itself
    UVICORN_PIDS=$(ps aux | grep "uvicorn QuickScrub.main:app" | grep -v grep | awk '{print $2}')
    VITE_PIDS=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')

    if [ -n "$UVICORN_PIDS" ]; then
        kill $UVICORN_PIDS 2>/dev/null || true
    fi
    if [ -n "$VITE_PIDS" ]; then
        kill $VITE_PIDS 2>/dev/null || true
    fi
}


# --- Main Script Logic ---

# Set a trap to call the cleanup function on script exit (CTRL+C, etc.)
trap cleanup EXIT

# --- 1. Stop Existing Server Instances ---
echo -e "${BLUE}--- Step 1: Stopping existing server instances ---${NC}"
# Redirect command output to /dev/null to avoid UI clutter
kill_processes
# Wait a moment for ports to be released
sleep 1
echo -e "${GREEN}All known server processes stopped.${NC}\n"

# --- 2. Clean Project Artifacts ---
echo -e "${BLUE}--- Step 2: Cleaning project caches and build artifacts ---${NC}"
echo "Removing Python caches and build artifacts..."
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache .eggs *.egg-info build dist
echo "Removing frontend caches and build artifacts..."
rm -rf frontend/node_modules frontend/dist
echo -e "${GREEN}Project cleanup complete.${NC}\n"

# --- 3. Optional: Start Servers ---
echo -e "${BLUE}--- Step 3: Optional Server Restart ---${NC}"
if ! prompt_yes_no "Attempt to restart development servers?"; then
    # The trap will handle cleanup, so we can just exit
    exit 0
fi

# --- Validate Environment ---
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Error: Python virtual environment 'venv' not found.${NC}"
    echo "Please run 'python3 -m venv venv' and 'pip install -e .[dev]' first."
    exit 1
fi
source venv/bin/activate

# --- Start Backend (in background) ---
echo -e "\n${BLUE}Starting backend server (in background)...${NC}"
uvicorn QuickScrub.main:app --reload &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
# Wait for the server to be ready instead of using a fixed sleep
timeout 10s bash -c 'until curl -s "http://127.0.0.1:8000" &>/dev/null; do sleep 1; done' || {
    echo -e "${RED}❌ Backend server failed to start within 10 seconds.${NC}"
    exit 1
}
echo -e "${GREEN}Backend is up and running.${NC}"

# --- Start Frontend ---
if [ ! -d "frontend/node_modules" ]; then
    echo -e "\n${YELLOW}Warning: 'node_modules' not found in frontend.${NC}"
    if prompt_yes_no "Run 'npm install' first?"; then
        (cd frontend && npm install)
    else
        echo "Skipping frontend server start."
        exit 1
    fi
fi

echo -e "\n${BLUE}Starting frontend server (in foreground)...${NC}"
echo "You can press CTRL+C at any time to stop both servers."
(cd frontend && npm run dev)

# The script will end here when the user presses CTRL+C.
# The 'trap' at the beginning of the script will then automatically call the 'cleanup' function.