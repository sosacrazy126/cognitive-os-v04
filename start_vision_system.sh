#!/bin/bash
# Start the complete vision system

echo "🧬 Starting Cognitive OS Vision System"
echo "===================================="

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "python.*unified_vision_server" 2>/dev/null
pkill -f "python.*mcp_vision_server" 2>/dev/null
sleep 1

# Start unified vision server (WebSocket source)
echo "1. Starting Unified Vision Server (WebSocket source)..."
python unified_vision_server.py > unified_vision.log 2>&1 &
UNIFIED_PID=$!
echo "   PID: $UNIFIED_PID"
sleep 2

# Start MCP vision server
echo "2. Starting MCP Vision Server..."
python mcp_vision_server.py > mcp_vision.log 2>&1 &
MCP_PID=$!
echo "   PID: $MCP_PID"
sleep 2

# Check if servers are running
if ps -p $UNIFIED_PID > /dev/null && ps -p $MCP_PID > /dev/null; then
    echo ""
    echo "✅ Vision System Running!"
    echo ""
    echo "Components:"
    echo "- Unified Vision Server: ws://localhost:8766"
    echo "- MCP Vision Server: stdio (background service)"
    echo ""
    echo "To test:"
    echo "1. Open enhanced_screen_capture.html in browser"
    echo "2. Start screen capture and connect"
    echo "3. Run: python test_mcp_vision.py"
    echo ""
    echo "To stop: kill $UNIFIED_PID $MCP_PID"
else
    echo "❌ Failed to start vision system"
    echo "Check logs: unified_vision.log and mcp_vision.log"
fi