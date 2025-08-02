# 🧬 Cognitive OS v0.4 - Complete API Reference

## 📋 Table of Contents

1. [Quick Start API](#quick-start-api)
2. [Core System Functions](#core-system-functions)
3. [Terminal Management](#terminal-management)
4. [Cognitive OS Operations](#cognitive-os-operations)
5. [Window Management](#window-management)
6. [Testing & Debugging](#testing--debugging)
7. [Configuration & Status](#configuration--status)
8. [Error Handling](#error-handling)

---

## 🚀 Quick Start API

### One-Line System Start
```python
# Method 1: Automatic Full Test (Recommended)
python -c "from quick_screen_test import start_full_screen_test; start_full_screen_test()"

# Method 2: Start Cognitive OS with browser
python -c "import tools; tools.start_cognitive_os(auto_start_browser=True)"

# Method 3: Quick connection test
python -c "from quick_screen_test import test_connection; test_connection()"
```

### Essential Functions
```python
import tools

# Start the full cognitive system
result = tools.start_cognitive_os()

# Check if system is running
status = tools.cognitive_status()

# Stop everything cleanly
tools.stop_cognitive_os()
```

---

## 🔧 Core System Functions

### Command Execution
```python
def execute_command(command: str, 
                   cwd: Optional[str] = None,
                   timeout: Optional[float] = None,
                   capture_output: bool = True) -> Dict[str, Any]
```

**Purpose**: Execute shell commands with comprehensive error handling and logging.

**Parameters**:
- `command`: Shell command to execute
- `cwd`: Working directory (default: current directory)
- `timeout`: Timeout in seconds (default: no timeout)
- `capture_output`: Whether to capture stdout/stderr (default: True)

**Returns**: Dictionary with execution results
```python
{
    'command': 'ls -la',
    'returncode': 0,
    'stdout': 'file listing...',
    'stderr': '',
    'execution_time': 0.025,
    'cwd': '/home/user',
    'success': True
}
```

**Examples**:
```python
# Basic command execution
result = tools.execute_command('ls -la')
print(f"Success: {result['success']}")
print(f"Output: {result['stdout']}")

# Command with timeout and specific directory
result = tools.execute_command(
    'npm install', 
    cwd='/path/to/project',
    timeout=300  # 5 minutes
)

# Command without capturing output (for interactive commands)
result = tools.execute_command('vim file.txt', capture_output=False)
```

### Process Management
```python
def get_processes(name_filter: Optional[str] = None) -> List[Dict[str, Any]]
```

**Purpose**: Get list of running processes with optional filtering.

**Examples**:
```python
# Get all processes
all_processes = tools.get_processes()

# Filter by name
python_processes = tools.get_processes('python')

# Process information structure
for proc in python_processes[:5]:
    print(f"PID {proc['pid']}: {proc['command']}")
```

---

## 🖥️ Terminal Management

### Terminal Information
```python
def get_terminal_info() -> Dict[str, Any]
def clear_terminal() -> bool
def set_terminal_title(title: str) -> bool
```

**Examples**:
```python
# Get terminal capabilities and size
info = tools.get_terminal_info()
print(f"Terminal size: {info['size']['width']}x{info['size']['height']}")
print(f"Platform: {info['platform']}")

# Clear screen
tools.clear_terminal()

# Set window title
tools.set_terminal_title("Cognitive OS Terminal")
```

### Terminal Session Management
```python
def create_terminal_session(terminal_type: str = "bash",
                          working_dir: Optional[str] = None) -> Optional[str]

def list_terminal_sessions() -> List[Dict[str, Any]]
```

**Examples**:
```python
# Create new session
session_id = tools.create_terminal_session(
    terminal_type="bash",
    working_dir="/home/user/project"
)
print(f"Created session: {session_id}")

# List all active sessions
sessions = tools.list_terminal_sessions()
for session in sessions:
    print(f"Session {session['session_id']}: {session['terminal_type']}")
```

### Terminal Spawning
```python
def spawn_terminal(terminal_type: Optional[str] = None,
                  working_dir: Optional[str] = None,
                  title: Optional[str] = None,
                  command: Optional[str] = None,
                  geometry: Optional[str] = None) -> Optional[Dict[str, Any]]
```

**Purpose**: Spawn a new terminal window with comprehensive options.

**Parameters**:
- `terminal_type`: Type of terminal ('gnome-terminal', 'konsole', 'xterm', etc.)
- `working_dir`: Working directory for the terminal
- `title`: Window title
- `command`: Command to execute in terminal
- `geometry`: Window geometry (e.g., "80x24+100+100")

**Examples**:
```python
# Basic terminal spawn
terminal = tools.spawn_terminal(
    title="Development Terminal",
    working_dir="/home/user/project"
)

# Terminal with specific command
terminal = tools.spawn_terminal(
    title="Server Monitor",
    command="htop",
    geometry="100x30+50+50"
)

# Auto-detect best terminal
terminal = tools.spawn_terminal()  # Uses system's preferred terminal
```

### Multiple Terminal Layouts
```python
def spawn_multiple_terminals(count: int = 2,
                            terminal_type: Optional[str] = None,
                            layout: str = "grid",
                            base_title: str = "Terminal") -> List[Dict[str, Any]]
```

**Parameters**:
- `count`: Number of terminals to spawn
- `layout`: Layout pattern ("grid", "horizontal", "vertical", "none")
- `base_title`: Base title for terminals

**Examples**:
```python
# Grid layout of 4 terminals
terminals = tools.spawn_multiple_terminals(
    count=4, 
    layout="grid",
    base_title="Dev Terminal"
)

# Horizontal row of terminals
terminals = tools.spawn_multiple_terminals(
    count=3,
    layout="horizontal",
    base_title="Monitor"
)
```

### Available Terminals
```python
def get_available_terminals() -> Dict[str, Any]
```

**Returns**: Information about available terminal emulators
```python
{
    'available_terminals': ['gnome-terminal', 'konsole', 'xterm'],
    'preferred_terminal': 'gnome-terminal',
    'window_manager': 'GNOME',
    'terminal_details': {
        'gnome-terminal': {
            'supports_tabs': True,
            'supports_geometry': True,
            'command': 'gnome-terminal'
        }
    }
}
```

---

## 🧬 Cognitive OS Operations

### System Lifecycle
```python
def start_cognitive_os(auto_start_browser: bool = True, 
                      websocket_port: int = 8080) -> Dict[str, Any]

def cognitive_status(session_id: str = None) -> Dict[str, Any]

def stop_cognitive_os(session_id: str = None) -> Dict[str, Any]
```

**Examples**:
```python
# Start full system with browser
result = tools.start_cognitive_os(auto_start_browser=True, websocket_port=8084)
print(f"Session ID: {result['session_id']}")
print(f"Daemon PID: {result['daemon_pid']}")
print(f"WebSocket: ws://localhost:{result['websocket_port']}/ws")

# Check status of all sessions
status = tools.cognitive_status()
print(f"Active sessions: {status['active_sessions']}")

# Check specific session
session_status = tools.cognitive_status("session_abc123")
print(f"Status: {session_status['status']}")

# Stop specific session
tools.stop_cognitive_os("session_abc123")

# Stop all sessions
tools.stop_cognitive_os()
```

### Cognitive Prompt System
```python
def enter_cognitive_prompt(prompt_text: str = None, 
                          sleep_seconds: int = 5) -> Dict[str, Any]

def start_interactive_session() -> Dict[str, Any]
```

**Examples**:
```python
# Send cognitive prompt with sleep mode
result = tools.enter_cognitive_prompt(
    "analyze this error for debugging", 
    sleep_seconds=3
)

# Start interactive session
tools.start_interactive_session()
```

---

## 🪟 Window Management

### Window Operations
```python
def list_windows(filter_title: Optional[str] = None) -> List[Dict[str, Any]]

def focus_window(window_id: str) -> bool

def move_window(window_id: str, x: int, y: int) -> bool

def resize_window(window_id: str, width: int, height: int) -> bool
```

**Examples**:
```python
# List all windows
windows = tools.list_windows()
for window in windows:
    print(f"Window {window['window_id']}: {window['title']}")

# Find terminals
terminals = tools.list_windows(filter_title="Terminal")

# Focus specific window
tools.focus_window("0x12345678")

# Position window
tools.move_window("0x12345678", x=100, y=100)

# Resize window
tools.resize_window("0x12345678", width=800, height=600)
```

---

## 🧪 Testing & Debugging

### Quick Test Functions
```python
from quick_screen_test import *

# Complete automated test
start_full_screen_test()

# Monitor existing screen sharing
quick_monitor()

# Test daemon connectivity
test_connection()
```

### Test Function Details

#### `start_full_screen_test()`
**Purpose**: Complete automated test of the entire system
- Cleans up existing processes
- Starts enhanced daemon
- Opens browser interface
- Provides live monitoring

**Usage**:
```python
from quick_screen_test import start_full_screen_test
start_full_screen_test()
```

#### `quick_monitor()`
**Purpose**: Monitor existing screen sharing session
- Connects to active WebSocket
- Displays real-time frame analysis
- Shows AI vision feedback

**Example Output**:
```
📺 FRAME 1: 1920x1080 - Brightness: 127.34
🎉 AI VISION ACTIVE - I can see your screen!
📺 FRAME 2: 1920x1080 - Brightness: 145.67
⏰ 15 frames received (5.2 FPS)
```

#### `test_connection()`
**Purpose**: Verify WebSocket daemon connectivity
- Tests connection to ws://localhost:8084/ws
- Retrieves daemon statistics
- Validates message handling

**Example Output**:
```
✅ Enhanced Cognitive Daemon is running
🧬 Session: enhanced-cognitive-session
📊 Frames processed: 847
👥 Clients connected: 1
💾 Data received: 38.2 MB
```

---

## ⚙️ Configuration & Status

### System Information
```python
# Get comprehensive system info
info = tools.get_terminal_info()

# Available terminals and capabilities
terminals = tools.get_available_terminals()

# Cognitive OS status
status = tools.cognitive_status()
```

### Configuration Files
```json
// cognitive_config.json
{
  "websocket_port": 8084,
  "frame_rate": 5,
  "jpeg_quality": 0.8,
  "preferred_terminals": ["gnome-terminal", "konsole"],
  "logging_level": "INFO"
}
```

---

## ❌ Error Handling

### Common Error Patterns
```python
try:
    result = tools.spawn_terminal()
    if result is None:
        print("❌ Failed to spawn terminal")
    else:
        print(f"✅ Terminal spawned with PID: {result['pid']}")
        
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

### Status Checking
```python
# Always check success status
result = tools.execute_command("ls -la")
if result['success']:
    print("Command succeeded")
    process_output(result['stdout'])
else:
    print(f"Command failed: {result['stderr']}")
```

### Cognitive OS Health Checks
```python
# Check if daemon is running
status = tools.cognitive_status()
if 'error' in status:
    print("Cognitive OS not running")
    # Start it
    tools.start_cognitive_os()
else:
    print(f"Active sessions: {status['active_sessions']}")
```

---

## 🔧 Advanced Usage Patterns

### Complete Workflow Example
```python
import tools
from quick_screen_test import test_connection

def setup_development_environment():
    """Set up a complete development environment with cognitive OS"""
    
    # 1. Start cognitive OS
    print("🧬 Starting Cognitive OS...")
    cognitive_result = tools.start_cognitive_os(auto_start_browser=True)
    
    if not cognitive_result['success']:
        print("❌ Failed to start Cognitive OS")
        return False
    
    print(f"✅ Cognitive OS running - Session: {cognitive_result['session_id']}")
    
    # 2. Test connection
    print("🔗 Testing connection...")
    if not test_connection():
        print("❌ Connection test failed")
        return False
    
    # 3. Spawn development terminals
    print("🖥️ Setting up development terminals...")
    terminals = tools.spawn_multiple_terminals(
        count=3,
        layout="grid",
        base_title="Dev Terminal"
    )
    
    # 4. Create specific terminals for different tasks
    code_terminal = tools.spawn_terminal(
        title="Code Editor",
        command="code .",
        working_dir="/home/user/project"
    )
    
    server_terminal = tools.spawn_terminal(
        title="Dev Server",
        command="npm run dev",
        working_dir="/home/user/project"
    )
    
    monitor_terminal = tools.spawn_terminal(
        title="System Monitor",
        command="htop"
    )
    
    print("🎉 Development environment ready!")
    print("📋 Available terminals:")
    for i, term in enumerate(terminals + [code_terminal, server_terminal, monitor_terminal]):
        if term:
            print(f"   {i+1}. {term.get('title', 'Terminal')} (PID: {term['pid']})")
    
    return True

# Usage
if __name__ == "__main__":
    setup_development_environment()
```

### Error Recovery Pattern
```python
def robust_cognitive_start():
    """Start cognitive OS with automatic error recovery"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Try to start
            result = tools.start_cognitive_os()
            
            if result['success']:
                # Verify connection
                if test_connection():
                    print(f"✅ Cognitive OS started successfully (attempt {attempt + 1})")
                    return result
                else:
                    print(f"⚠️ Started but connection failed (attempt {attempt + 1})")
            else:
                print(f"❌ Start failed (attempt {attempt + 1}): {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception on attempt {attempt + 1}: {e}")
        
        if attempt < max_retries - 1:
            print("🔄 Retrying in 5 seconds...")
            time.sleep(5)
            
            # Clean up before retry
            tools.stop_cognitive_os()
            time.sleep(2)
    
    print("❌ Failed to start Cognitive OS after all retries")
    return None
```

---

**🧬 This API reference provides complete coverage of the Cognitive OS v0.4 functionality, enabling developers to build sophisticated human-AI collaborative applications.**
