#!/bin/bash

# Exit on error
set -e

# Change to the defect-detection-agentic-flow directory
cd "$(dirname "$0")"
echo "=== Working directory: $(pwd) ==="

echo "=== Setting up Python virtual environment ==="
# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "=== Installing requirements ==="
pip install -r requirements.txt

# Change to the react-agent directory to run the MCP servers
cd react-agent

# Start MCP servers in background
echo "=== Starting MCP servers ==="
python mcp-classify-conv-server.py &
MCP_CLASSIFY_PID=$!
echo "Started mcp-classify-conv-server.py (PID: $MCP_CLASSIFY_PID)"

python mcp-identify-defect_area-tool.py &
MCP_IDENTIFY_PID=$!
echo "Started mcp-identify-defect_area-tool.py (PID: $MCP_IDENTIFY_PID)"

python mcp-image-cropping-tool.py &
MCP_CROPPING_PID=$!
echo "Started mcp-image-cropping-tool.py (PID: $MCP_CROPPING_PID)"

# Give the MCP servers a moment to start up
echo "Waiting for MCP servers to initialize..."
sleep 5

# Run fault detection agent
echo "=== Starting fault detection agent ==="
python fault-detection-react-agent.py &
FAULT_DETECTION_PID=$!
echo "Started fault-detection-react-agent.py (PID: $FAULT_DETECTION_PID)"

# Change back to the parent directory to run the UI
cd ..

# Run Streamlit UI
echo "=== Starting Streamlit UI ==="
streamlit run ui.py

# Cleanup function to kill background processes when script exits
cleanup() {
    echo "Cleaning up background processes..."
    kill $MCP_CLASSIFY_PID $MCP_IDENTIFY_PID $MCP_CROPPING_PID $FAULT_DETECTION_PID 2>/dev/null || true
    deactivate
}

# Register the cleanup function to be called on exit
trap cleanup EXIT

# Wait for Streamlit to exit
wait
