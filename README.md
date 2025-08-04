# 🧬 Cognitive Operating System v0.4

**A revolutionary human-AI collaboration platform featuring MCP-based real-time vision processing, intelligent terminal control, and autonomous agent management.**

## 🌟 Overview

The Cognitive Operating System (CogOS) v0.4 represents a breakthrough in human-AI collaborative computing, built on a clean, production-ready architecture. The system provides:

- 👁️ **Real-time screen vision** through MCP (Model Context Protocol) vision server
- 🧠 **Intelligent analysis** via unified vision processing pipeline  
- ⚡ **Terminal control** through cross-platform command execution
- 🤖 **Autonomous agents** with session cloning and management
- 🔄 **Persistent state** with SQLite-based session recovery

## 🏗️ Architecture

### MCP-Based Vision Pipeline
```
Browser Screen Capture → Unified Vision Server → MCP Vision Server → CLI Agent Tools
  (getDisplayMedia)       (WebSocket:8766)      (stdio/MCP)         (see, analyze, watch)
```

### Layered System Design
```
┌─────────────────────────────────────────────────────────┐
│                 AGENT LAYER                             │
│  🤖 Autonomous Agents + Session Cloning + Dashboards  │
├─────────────────────────────────────────────────────────┤
│                 VISION LAYER                            │
│  👁️ MCP Vision Server + Unified Analysis Pipeline     │
├─────────────────────────────────────────────────────────┤
│                 CONTROL LAYER                           │
│  🖥️ Terminal Management + Process Control             │
├─────────────────────────────────────────────────────────┤
│                FOUNDATION LAYER                         │
│  🔧 Cross-platform Interface + Session Persistence    │
└─────────────────────────────────────────────────────────┘
```

### Core Components

1. **MCP Vision System** - Real-time screen analysis via Model Context Protocol
2. **Unified Vision Server** - WebSocket-based vision processing hub
3. **Terminal Control** - Cross-platform command execution and management
4. **Autonomous Agents** - Self-managing agent systems with session persistence
5. **Dashboard Interfaces** - Web-based control and monitoring interfaces

## 🚀 Quick Start

### Method 1: Complete Vision System
```bash
# Start the complete MCP-based vision system
./start_vision_system.sh

# Open browser interface
firefox enhanced_screen_capture.html

# Test MCP vision server
python -c "import mcp_vision_server; print('MCP Vision Server ready')"
```

### Method 2: Individual Components
```bash
# Start unified vision server
python unified_vision_server.py

# Start MCP vision server (in another terminal)
python mcp_vision_server.py

# Test terminal control
python -c "import tools; tools.spawn_terminal(title='Test', command='echo Hello')"
```

### Method 3: Autonomous Agents
```bash
# Start autonomous agent system
python autonomous_agent_loops.py

# Launch agent control dashboard
python -c "import webbrowser; webbrowser.open('agent_control_dashboard.html')"

# Test session cloning
python session_cloner.py
```

## 📁 Project Organization

The project is organized into logical directories for easy navigation and development:

```
cognitive-os-v04/
├── 📁 vision-system/          # MCP-based real-time vision processing
├── 📁 agent-system/           # Autonomous agent management
├── 📁 dashboards/             # Web-based control interfaces
├── 📁 core-system/            # Foundation system components
├── 📁 session-management/     # Session persistence and management
├── 📁 docs/                   # Comprehensive documentation
└── 📁 fabric_pattern_studio_refactored/ # Pattern studio implementation
```

### Key Components by Directory

**🔍 Vision System** (`vision-system/`)
- MCP vision server for CLI agents
- WebSocket vision processing hub  
- Browser-based screen capture interface
- Complete vision system startup script

**🤖 Agent System** (`agent-system/`)
- Self-managing autonomous agent loops
- Agent session cloning and management
- Mission control and callback infrastructure

**📊 Dashboards** (`dashboards/`)
- Agent control and management interfaces
- Consciousness monitoring dashboards
- Terminal and AI-centric control panels

**⚙️ Core System** (`core-system/`)
- Terminal control and cognitive orchestration
- Advanced cognitive processing daemon
- Tool and workflow integration frameworks

**For complete project structure details, see [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)**

## ⚡ Key Features

### 👁️ MCP Vision System
- **Real-time screen analysis** through Model Context Protocol
- **Persistent background service** eliminates blocking loops
- **Unified vision processing** with brightness, contrast, and UI detection
- **WebSocket architecture** on port 8766 for efficient communication
- **Browser integration** via getDisplayMedia() API

### 🤖 Autonomous Agent Management
- **Self-managing agent loops** with automatic restart capabilities
- **Session cloning** for agent state preservation and recovery
- **Multi-agent orchestration** with callback systems
- **Agent dashboards** for monitoring and control
- **Mission control interfaces** for high-level coordination

### 🖥️ Terminal Control
- **Cross-platform compatibility** (gnome-terminal, konsole, xterm)
- **Real-time command execution** with output capture
- **Process lifecycle management** with cleanup on exit
- **Window management** and focus control
- **SQLite-based persistence** for session recovery

### 🧬 Cognitive Integration
- **Workflow integration** with cognitive processing
- **Tool integration framework** for extensible functionality
- **Real-time debugging** and monitoring capabilities
- **Consciousness dashboard** for system awareness
- **AI vision integration** with Gemini and other models

## 📊 Performance Metrics

| Component | Performance | Status |
|-----------|-------------|---------|
| MCP Vision Server | Real-time analysis | ✅ Production Ready |
| WebSocket Communication | Port 8766, JSON protocol | ✅ Stable |
| Screen Capture | getDisplayMedia() API | ✅ Browser Native |
| Agent Session Cloning | Full state preservation | ✅ Reliable |
| Terminal Control | Cross-platform spawning | ✅ Universal |
| Session Persistence | SQLite-based recovery | ✅ Robust |
| Autonomous Agents | Self-managing loops | ✅ Autonomous |
| Command Execution | Sub-second response | ✅ Responsive |

## 🛠️ API Reference

### Vision System API
```python
# Start complete vision system
import subprocess
subprocess.run(["./start_vision_system.sh"])

# MCP Vision Server functions (available to CLI agents)
# - see_screen(): Get current screen analysis
# - describe_screen(): Get detailed screen description
# - watch_screen(): Monitor screen changes

# Unified Vision Server (WebSocket client)
import websockets
import asyncio

async def connect_to_vision():
    uri = "ws://localhost:8766"
    async with websockets.connect(uri) as websocket:
        data = await websocket.recv()
        return json.loads(data)
```

### Terminal Control API
```python
import tools

# Terminal operations
terminal = tools.spawn_terminal(title="My Terminal", command="echo Hello")
result = tools.execute_command("ls -la", capture_output=True)

# Window management
windows = tools.list_windows()
tools.focus_window(window_id)

# Cognitive functions
tools.enter_cognitive_prompt("analyze this error")
status = tools.cognitive_status()
```

### Autonomous Agent API
```python
# Agent management
from autonomous_agent_loops import *
from session_cloner import SessionCloner

# Create and manage agents
cloner = SessionCloner()
cloned_session = cloner.clone_session("main_session")

# Agent callbacks
from agent_callback_system import *
register_agent_callback("vision_analysis", callback_function)
```

## 🔧 System Requirements

### Software Dependencies
```bash
# Core Python dependencies
pip install websockets pillow psutil blessed asyncio numpy

# MCP (Model Context Protocol) support
pip install mcp fastmcp

# Optional AI integrations
pip install google-generativeai  # For Gemini vision
```

### Platform Support
- ✅ **Linux (Ubuntu/Debian)** - Primary platform with full support
- ✅ **Linux (GNOME/KDE/XFCE)** - All major window managers
- ⚠️ **macOS** - Core functionality supported
- ⚠️ **Windows** - Basic terminal control available

### Browser Requirements
- **Firefox** (recommended) - Full getDisplayMedia() support
- **Chrome/Chromium** - Complete WebSocket and screen sharing
- **Safari** - Basic support (may require permissions)
- **Edge** - WebSocket support available

### Network Requirements
- **Port 8766** - Unified Vision Server (WebSocket)
- **Localhost access** - Browser to vision server communication
- **Screen sharing permissions** - Browser access to display capture

## 🎯 Use Cases

### AI Agent Development
- **Autonomous agent creation** with session cloning and persistence
- **Real-time screen analysis** for agent decision making
- **Multi-agent coordination** through callback systems
- **Agent debugging** with comprehensive monitoring dashboards

### Development & Operations
- **AI-assisted debugging** with visual context understanding
- **Terminal automation** with cross-platform command execution
- **System monitoring** through consciousness dashboards
- **Workflow integration** with cognitive processing pipelines

### Research & Experimentation
- **Human-AI collaboration studies** with shared visual context
- **Vision processing research** using MCP-based architecture
- **Cognitive system development** with modular component testing
- **AI training** with real-time screen interaction data

## 🚧 Development Status

### Phase 1: Core Foundation ✅ COMPLETE
- [x] Terminal control implementation
- [x] Cross-platform compatibility
- [x] Session persistence with SQLite
- [x] WebSocket communication protocol

### Phase 2: Vision System ✅ COMPLETE
- [x] MCP-based vision architecture
- [x] Unified vision server implementation
- [x] Browser screen capture integration
- [x] Real-time frame analysis pipeline

### Phase 3: Autonomous Agents ✅ COMPLETE
- [x] Agent loop management system
- [x] Session cloning functionality
- [x] Agent callback infrastructure
- [x] Dashboard interfaces for monitoring

### Phase 4: Integration & Polish 🚧 IN PROGRESS
- [x] Gemini AI vision integration
- [x] Cognitive workflow integration
- [x] Tool integration framework
- [ ] Enhanced security measures
- [ ] Performance optimization
- [ ] Extended documentation

## 🐛 Troubleshooting

### Vision System Issues

**MCP Vision Server Not Starting**
```bash
# Check if unified vision server is running
ps aux | grep unified_vision_server

# Restart complete vision system
./start_vision_system.sh

# Check logs
tail -f unified_vision.log
tail -f mcp_vision.log
```

**WebSocket Connection Fails (Port 8766)**
```bash
# Check if port is available
netstat -tlnp | grep 8766

# Start unified vision server manually
python unified_vision_server.py

# Test WebSocket connection
python -c "import websockets, asyncio; asyncio.run(websockets.connect('ws://localhost:8766'))"
```

**Screen Capture Not Working**
- Ensure browser supports `getDisplayMedia()` API
- Grant screen sharing permissions when prompted
- Try Firefox if Chrome/Safari fails
- Check browser console for errors

**Agent System Issues**
```bash
# Debug autonomous agents
python cognitive_debug.py

# Test session cloning
python session_persistence_test.py

# Monitor agent callbacks
python -c "from agent_callback_system import debug_callbacks; debug_callbacks()"
```

**Terminal Control Issues**
- Check if terminal emulator is installed: `which gnome-terminal`
- Try alternative: `export TERMINAL=xterm` or `export TERMINAL=konsole`
- Verify psutil permissions for process management

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## 📧 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the comprehensive test results

---

**🧬 Cognitive Operating System v0.4 - Ready for exponential human-AI collaboration!**

*Built with ❤️ and 🧠 for the future of human-AI interaction*