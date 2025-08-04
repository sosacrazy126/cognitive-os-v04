# Vision System Architecture

## Overview

The Cognitive OS Vision System provides real-time screen analysis for CLI agents through a persistent MCP (Model Context Protocol) server. This eliminates the blocking loop problem of Python scripts by running vision as a background service.

## Architecture

```
Browser Screen Sharing → Unified Vision Server → MCP Vision Server → CLI Agent Tools
    (getDisplayMedia)       (WebSocket:8766)      (stdio/MCP)         (see, describe, watch)
```

### Components

1. **Browser Screen Capture** (`enhanced_screen_capture.html`)
   - Uses `navigator.mediaDevices.getDisplayMedia()` for real screen sharing
   - Converts frames to Base64 JPEG
   - Sends to Unified Vision Server via WebSocket

2. **Unified Vision Server** (`unified_vision_server.py`)
   - Single WebSocket server on port 8766
   - Receives frames from browser
   - Performs real-time analysis (UI detection, brightness, insights)
   - Broadcasts analysis to connected clients

3. **MCP Vision Server** (`mcp_vision_server.py`)
   - Persistent background service using MCP protocol
   - Connects to Unified Vision Server as a client
   - Maintains vision state without blocking
   - Provides tools for CLI agents:
     - `see()` - Get current screen analysis
     - `describe()` - Natural language description
     - `watch_for_changes()` - Monitor changes over time
     - `is_terminal()`, `is_browser()`, `is_dark_mode()` - Quick checks
     - `get_vision_status()` - System status
     - `get_recent_insights()` - Recent actionable insights

## Why MCP?

Traditional Python scripts with vision loops block CLI agent execution:

❌ **Problem with Scripts:**
```python
# This blocks the CLI agent!
while True:
    frame = get_frame()
    analyze(frame)
    time.sleep(1)
```

✅ **Solution with MCP:**
```python
# Non-blocking tool calls
result = await session.call_tool("see", {})
# Agent continues execution immediately
```

MCP servers provide:
- **Persistent background processing** - Vision runs continuously
- **Tool-based interface** - Simple function calls, no process management
- **Async operation** - Non-blocking for CLI agents
- **Clean lifecycle** - Proper startup/shutdown
- **State management** - Maintains context between calls

## Usage

### 1. Start the Vision System

```bash
./start_vision_system.sh
```

This starts both servers and shows their PIDs.

### 2. Open Browser Interface

Open `enhanced_screen_capture.html` in a browser:
1. Click "Start Screen Capture"
2. Select screen/window to share
3. Click "Connect to Cognitive OS"
4. Click "Start Frame Streaming"

### 3. Use Vision Tools in CLI Agent

```python
# In your CLI agent (like Claude Code)
result = await session.call_tool("see", {})
# Returns: {"ui_type": "terminal", "description": "Dark-themed terminal", ...}

result = await session.call_tool("watch_for_changes", {"duration": 5})
# Returns: [{"type": "ui_change", "from": "terminal", "to": "browser", ...}]
```

### 4. Install in Claude Desktop

```bash
uv run mcp install mcp_vision_server.py --name "Vision Server"
```

## Testing

Run the test script to verify the system:

```bash
python test_mcp_vision.py
```

## Architecture Benefits

1. **Non-blocking**: CLI agents can call vision tools without waiting
2. **Real-time**: Continuous background frame processing
3. **Stateful**: Maintains history and context
4. **Efficient**: Single WebSocket connection, multiple consumers
5. **Flexible**: Easy to add new analysis tools
6. **Standard**: Uses MCP protocol for compatibility

## Future Enhancements

- OCR integration for text extraction
- Object detection
- Multi-monitor support
- Recording and playback
- Integration with other MCP servers
- Cloud deployment options

## Troubleshooting

1. **No vision data**: Ensure browser screen sharing is active
2. **Connection failed**: Check if ports 8766 is available
3. **MCP errors**: Verify MCP SDK is installed (`pip install "mcp[cli]"`)

## Summary

This architecture solves the real-time vision problem by:
- Running vision processing as a persistent background service
- Providing simple, non-blocking tools through MCP
- Maintaining state between tool calls
- Supporting multiple concurrent consumers

The result is a clean, efficient vision system that CLI agents can use without getting stuck in blocking loops.