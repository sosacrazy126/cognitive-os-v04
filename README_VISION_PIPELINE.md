# Vision Pipeline - Core Real-time Vision for CLI Agents

A streamlined, browser-free vision pipeline extracted from Cognitive OS v0.4, focused on enabling CLI agents (like Claude Code) to process real-time screen content.

## Core Components

### 1. **core_vision_stream.py** - Screen Capture Engine
- Direct screen capture using `mss` (no browser needed)
- 5 FPS streaming with <1s latency
- WebSocket server for real-time frame distribution
- Pluggable frame processors (brightness, edge detection)
- JPEG compression for efficient streaming

### 2. **vision_tool_interface.py** - Tool-calling Interface
- Structured tool-calling system for CLI agents
- Three tool categories:
  - **Vision**: get_frame, analyze_frame, capture_region
  - **System**: execute, read_file, write_file, list_directory
  - **Terminal**: spawn, send_keys, read_output
- Async/await pattern for all operations
- Simple CLIAgent class for perception-action loops

### 3. **gemini_vision_integration.py** - AI Vision Processing
- Integration with Google Gemini Vision API
- Prepared for Multimodal Live API (when available)
- Frame-by-frame analysis with custom prompts
- Future WebRTC streaming support

### 4. **claude_vision_adapter.py** - Claude Code Bridge
- Converts visual data to structured text
- Scene descriptions and change detection
- Actionable item extraction
- Tool suggestions based on screen content

## Quick Start

### 1. One-time Setup
```bash
python setup_vision_pipeline.py
```

This will:
- Check Python 3.8+ compatibility
- Install dependencies (websockets, mss, pillow, numpy)
- Create configuration file
- Generate launcher script

### 2. Configuration
Edit `vision_config.json`:
```json
{
  "vision": {
    "fps": 5,
    "quality": 85,
    "max_width": 1280,
    "websocket_port": 8765
  },
  "gemini": {
    "api_key": "YOUR_API_KEY_HERE"
  }
}
```

### 3. Launch Vision Pipeline
```bash
python launch_vision.py
```

## Usage Examples

### Basic CLI Agent
```python
from vision_tool_interface import CLIAgent

agent = CLIAgent(name="my_agent")
await agent.initialize()

# Get current screen
result = await agent.act('vision.get_frame', metadata_only=True)

# Execute command based on vision
result = await agent.act('system.execute', command='ls -la')
```

### Direct Tool Calls
```python
from vision_tool_interface import VisionToolInterface, ToolCall

interface = VisionToolInterface()
await interface.connect_vision()

# Capture specific region
call = ToolCall(
    tool='vision',
    action='capture_region',
    parameters={'x': 100, 'y': 100, 'width': 500, 'height': 300}
)
result = await interface.call_tool(call)
```

### Claude Vision Adapter
```python
from claude_vision_adapter import ClaudeVisionBridge

bridge = ClaudeVisionBridge()
await bridge.connect()

# Get vision context as text
context = await bridge.get_vision_context()
print(context)  # Human-readable scene description
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Screen Capture │────▶│ WebSocket Server │────▶│   CLI Agent     │
│   (mss, 5fps)   │     │   (port 8765)    │     │ (Tool Calling)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                                 │
         ▼                                                 ▼
┌─────────────────┐                              ┌─────────────────┐
│ Frame Processor │                              │ Vision Analysis │
│  (PIL, numpy)   │                              │ (Local/Gemini)  │
└─────────────────┘                              └─────────────────┘
```

## Key Features

1. **No Browser Dependencies**: Pure Python screen capture using `mss`
2. **Minimal Setup**: Single setup script configures everything
3. **Tool-based Interface**: Structured tool-calling for easy integration
4. **Real-time Performance**: 5 FPS with <1s latency
5. **Claude Compatible**: Text-based vision descriptions for non-visual agents
6. **Extensible**: Easy to add new processors and tools

## Performance

- Frame capture: ~0.1s per frame
- WebSocket latency: <10ms local
- Compression: 25% size reduction
- Memory usage: ~50MB base + frame buffers

## Future Enhancements

1. **Gemini Live API**: Real-time video streaming when available
2. **OCR Integration**: Extract actual text from screens
3. **Object Detection**: Identify UI elements and objects
4. **Multi-monitor**: Support for multiple displays
5. **Camera Input**: Direct camera feed processing

## Troubleshooting

### "No module named 'mss'"
Run: `pip install mss websockets pillow numpy`

### "Connection refused" on WebSocket
Ensure vision stream is running: `python launch_vision.py`

### High CPU usage
Reduce FPS in config: `"fps": 3`

### Terminal automation not working
Install xdotool: `sudo apt-get install xdotool`

## Integration with Claude Code

Since Claude doesn't have native vision, use the adapter:

```python
# In your Claude Code session
from claude_vision_adapter import ClaudeVisionBridge

bridge = ClaudeVisionBridge()
await bridge.connect()

# Get text description of screen
context = await bridge.get_vision_context()
# Now Claude can "see" through text descriptions
```

## License

Extracted and simplified from Cognitive OS v0.4 for educational and development purposes.