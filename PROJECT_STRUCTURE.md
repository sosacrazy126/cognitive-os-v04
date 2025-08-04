# 🗂️ Cognitive OS v0.4 - Project Organization

## Directory Structure

```
cognitive-os-v04/
├── 📁 vision-system/          # MCP-based real-time vision processing
│   ├── mcp_vision_server.py   # MCP vision server for CLI agents
│   ├── unified_vision_server.py # WebSocket vision processing hub
│   ├── enhanced_screen_capture.html # Browser screen capture interface
│   ├── start_vision_system.sh # Complete vision system startup
│   ├── gemini_vision_integration.py # Gemini AI vision integration
│   └── live_screen_monitor.py # Real-time screen monitoring
│
├── 📁 agent-system/           # Autonomous agent management
│   ├── autonomous_agent_loops.py # Self-managing agent systems
│   ├── agent_callback_system.py # Agent callback infrastructure
│   ├── enhanced_mission_control.py # Mission control interface
│   ├── session_cloner.py      # Agent session cloning
│   ├── restore_session_cognitive_os_main_session.py # Session restoration
│   └── session_prompt_handler.py # Session prompt management
│
├── 📁 dashboards/             # Web-based control interfaces
│   ├── agent_control_dashboard.html # Agent management interface
│   ├── integrated_consciousness_dashboard.html # Consciousness monitoring
│   ├── ai_centric_dashboard.py # AI-focused control panel
│   └── terminal_dashboard.py  # Terminal management interface
│
├── 📁 core-system/            # Foundation system components
│   ├── tools.py               # Terminal control and cognitive orchestration
│   ├── enhanced_cognitive_daemon.py # Advanced cognitive processing
│   ├── cognitive_tool_integration.py # Tool integration framework
│   ├── cognitive_workflow_integration.py # Workflow management
│   ├── cognitive_prompt.py    # Prompt processing system
│   ├── cognitive_debug.py     # Comprehensive debugging tools
│   ├── enhanced_terminal_orchestrator.py # Terminal orchestration
│   ├── inline_cognitive_assistant.py # Inline cognitive assistance
│   ├── complete_agent_system_demo.py # Agent system demonstration
│   ├── integration_summary.py # System integration overview
│   ├── live_consciousness_demo.py # Consciousness demonstration
│   ├── realtime_cognitive_mirror.py # Real-time cognitive mirroring
│   ├── start_cognitive_background.py # Background cognitive startup
│   ├── start_cognitive_silent.py # Silent cognitive startup
│   └── stop_cognitive_silent.py # Silent cognitive shutdown
│
├── 📁 session-management/     # Session persistence and management
│   ├── session_persistence_test.py # Session persistence testing
│   ├── terminal_sessions.db   # SQLite session database
│   ├── terminal_sessions/     # Session storage directory
│   ├── session_clone_cognitive_os_main_session.json # Session clone data
│   └── cognitive_session_20250801_181240.json # Cognitive session backup
│
├── 📁 docs/                   # Comprehensive documentation
│   ├── AGENT_SYSTEM_OVERVIEW.md # Agent system documentation
│   ├── API_REFERENCE.md       # API documentation
│   ├── ARCHITECTURE.md        # System architecture details
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   ├── INNOVATION_ANALYSIS.md # Innovation analysis
│   ├── INSTALL.md             # Installation guide
│   ├── README_VISION_PIPELINE.md # Vision pipeline documentation
│   ├── REFACTORING.md         # Refactoring notes
│   ├── screen_capture_research_report.md # Screen capture research
│   ├── SESSION_CLONE_SUMMARY.md # Session cloning documentation
│   └── VISION_ARCHITECTURE.md # Vision architecture details
│
├── 📁 fabric_pattern_studio_refactored/ # Pattern studio implementation
│   └── app.py                 # Pattern studio application
│
├── README.md                  # Main project documentation
├── LICENSE                    # MIT License
├── CLAUDE.md                  # Claude-specific instructions
├── PROJECT_STRUCTURE.md       # This file - project organization
└── cognitive_config.json      # System configuration
```

## Quick Navigation

### 🚀 Getting Started
- **Main Documentation**: `README.md`
- **Installation Guide**: `docs/INSTALL.md`
- **Architecture Overview**: `docs/ARCHITECTURE.md`

### 👁️ Vision System
- **Start Vision System**: `vision-system/start_vision_system.sh`
- **Screen Capture Interface**: `vision-system/enhanced_screen_capture.html`
- **MCP Vision Server**: `vision-system/mcp_vision_server.py`

### 🤖 Agent Management
- **Agent Control Dashboard**: `dashboards/agent_control_dashboard.html`
- **Autonomous Agent Loops**: `agent-system/autonomous_agent_loops.py`
- **Session Cloning**: `agent-system/session_cloner.py`

### 🖥️ Terminal Control
- **Core Tools**: `core-system/tools.py`
- **Terminal Dashboard**: `dashboards/terminal_dashboard.py`
- **Enhanced Orchestrator**: `core-system/enhanced_terminal_orchestrator.py`

### 📊 Monitoring & Debug
- **Consciousness Dashboard**: `dashboards/integrated_consciousness_dashboard.html`
- **Cognitive Debug Tools**: `core-system/cognitive_debug.py`
- **Live Screen Monitor**: `vision-system/live_screen_monitor.py`

## Development Workflow

1. **Vision System**: Start with `vision-system/start_vision_system.sh`
2. **Core Functions**: Access through `core-system/tools.py`
3. **Agent Management**: Use `agent-system/` components
4. **Monitoring**: Open dashboard files in `dashboards/`
5. **Documentation**: Reference files in `docs/` directory

## File Organization Principles

- **Functional Grouping**: Files grouped by primary function
- **Clear Separation**: Vision, agents, core, and UI clearly separated
- **Documentation**: Comprehensive docs in dedicated directory
- **Session Data**: Persistent data isolated in session-management
- **Easy Navigation**: Logical structure for quick access

---

**🧬 Cognitive Operating System v0.4 - Organized for Maximum Productivity!**