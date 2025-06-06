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

# Create log file for classify server
echo "=== Starting MCP servers ==="
LOG_FILE="/tmp/mcp-classify-server.log"
> $LOG_FILE  # Clear log file if it exists

# Start classify server with output redirected to log file
python mcp-classify-conv-server.py > $LOG_FILE 2>&1 &
MCP_CLASSIFY_PID=$!
echo "Started mcp-classify-conv-server.py (PID: $MCP_CLASSIFY_PID)"

# Start other MCP servers
python mcp-identify-defect_area-tool.py &
MCP_IDENTIFY_PID=$!
echo "Started mcp-identify-defect_area-tool.py (PID: $MCP_IDENTIFY_PID)"

python mcp-image-cropping-tool.py &
MCP_CROPPING_PID=$!
echo "Started mcp-image-cropping-tool.py (PID: $MCP_CROPPING_PID)"

# Wait for the facebook/convnext-tiny-224 model to be loaded
echo "Waiting for MCP servers to initialize..."
echo "Waiting for facebook/convnext-tiny-224 model to load..."

MAX_WAIT=120  # Maximum wait time in seconds
WAITED=0
while ! grep -q "successfully" $LOG_FILE && [ $WAITED -lt $MAX_WAIT ]; do
    echo -n "."
    sleep 2
    WAITED=$((WAITED + 2))
    if [ $((WAITED % 10)) -eq 0 ]; then
        echo " $WAITED seconds"
    fi
done

if grep -q "successfully" $LOG_FILE; then
    echo -e "\n✅ Model facebook/convnext-tiny-224 loaded successfully!"
else
    echo -e "\n⚠️ Timeout waiting for model to load, continuing anyway..."
fi

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
