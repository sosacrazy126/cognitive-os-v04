"""
tools.py - Cognitive Operating System v0.4
Terminal Control + Screen Sharing + AI Integration

Layered Architecture:
- Foundation: Cross-platform system interface
- Control: Terminal and window management  
- Cognitive: Screen sharing + AI processing integration

Each function designed for terminal execution via: python -c "from tools import func; func(args)"
"""

import sys
import os
import json
import sqlite3
import subprocess
import signal
import time
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading
import queue
import asyncio
import uuid
from datetime import datetime

# Cross-platform imports with graceful fallbacks
try:
    import psutil
except ImportError:
    psutil = None

try:
    from blessed import Terminal
except ImportError:
    Terminal = None

# Platform-specific imports
if sys.platform.startswith('win'):
    try:
        import msvcrt
        import win32gui
        import win32process
        import win32con
    except ImportError:
        win32gui = win32process = win32con = msvcrt = None
elif sys.platform.startswith('darwin'):
    try:
        import AppKit
        from Foundation import NSAppleScript
    except ImportError:
        AppKit = NSAppleScript = None
else:  # Linux/Unix
    try:
        import termios
        import fcntl
    except ImportError:
        termios = fcntl = None


# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('tools.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# === DATA STRUCTURES ===
@dataclass
class ProcessInfo:
    """Information about a managed process"""
    pid: int
    command: str
    cwd: str
    created_at: float
    status: str = "running"
    terminal_id: Optional[str] = None
    

@dataclass
class TerminalSession:
    """Information about a terminal session"""
    session_id: str
    terminal_type: str
    pid: int
    working_dir: str
    environment: Dict[str, str]
    created_at: float
    last_active: float
    status: str = "active"


@dataclass
class CognitiveSession:
    """Information about a cognitive OS session"""
    session_id: str
    daemon_pid: Optional[int]
    websocket_port: int
    screen_context: Dict[str, Any]
    ai_conversation: List[Dict[str, Any]]
    active_terminals: List[str]
    cognitive_state: Dict[str, Any]
    created_at: float
    last_activity: float
    status: str = "active"


# === FOUNDATION LAYER ===
class SystemInterface:
    """
    Cross-platform system interaction using battle-tested libraries.
    Provides unified interface for process and window management.
    """
    
    def __init__(self):
        self.platform = sys.platform
        self.capabilities = self._detect_capabilities()
        logger.info(f"SystemInterface initialized for {self.platform}")
        logger.debug(f"Capabilities: {self.capabilities}")
    
    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detect available system capabilities"""
        caps = {
            'psutil': psutil is not None,
            'terminal_control': Terminal is not None,
            'process_control': True,  # subprocess always available
        }
        
        if self.platform.startswith('win'):
            caps.update({
                'win32_api': win32gui is not None,
                'windows_terminal': True,
            })
        elif self.platform.startswith('darwin'):
            caps.update({
                'applescript': NSAppleScript is not None,
                'cocoa_api': AppKit is not None,
            })
        else:  # Linux/Unix
            caps.update({
                'termios': termios is not None,
                'x11_tools': os.system('which xdotool >/dev/null 2>&1') == 0,
                'wmctrl': os.system('which wmctrl >/dev/null 2>&1') == 0,
            })
        
        return caps
    
    def get_processes(self, name_filter: Optional[str] = None) -> List[ProcessInfo]:
        """Get list of running processes, optionally filtered by name"""
        processes = []
        
        if self.capabilities['psutil']:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'create_time']):
                    try:
                        info = proc.info
                        if name_filter and name_filter not in info.get('name', ''):
                            continue
                        
                        cmdline = info.get('cmdline', [])
                        command = ' '.join(cmdline) if cmdline else info.get('name', 'unknown')
                        
                        processes.append(ProcessInfo(
                            pid=info['pid'],
                            command=command,
                            cwd=info.get('cwd', ''),
                            created_at=info.get('create_time', 0),
                            status='running'
                        ))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                logger.error(f"Error getting processes: {e}")
        
        return processes
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process by PID"""
        try:
            if self.capabilities['psutil']:
                proc = psutil.Process(pid)
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                proc.wait(timeout=5)
            else:
                sig = signal.SIGKILL if force else signal.SIGTERM
                os.kill(pid, sig)
            
            logger.info(f"Process {pid} {'killed' if force else 'terminated'}")
            return True
        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            return False
    
    def execute_command(self, command: str, cwd: Optional[str] = None, 
                       env: Optional[Dict[str, str]] = None,
                       timeout: Optional[float] = None,
                       capture_output: bool = True) -> Dict[str, Any]:
        """Execute a command with comprehensive error handling"""
        try:
            # Prepare environment
            full_env = os.environ.copy()
            if env:
                full_env.update(env)
            
            # Execute command
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                env=full_env,
                timeout=timeout,
                capture_output=capture_output,
                text=True
            )
            
            execution_time = time.time() - start_time
            
            # Package results
            output = {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else '',
                'stderr': result.stderr if capture_output else '',
                'execution_time': execution_time,
                'cwd': cwd or os.getcwd(),
                'success': result.returncode == 0
            }
            
            if output['success']:
                logger.info(f"Command executed successfully: {command}")
            else:
                logger.warning(f"Command failed (code {result.returncode}): {command}")
                if result.stderr:
                    logger.warning(f"Error output: {result.stderr}")
            
            return output
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {command}")
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout}s',
                'execution_time': timeout or 0,
                'cwd': cwd or os.getcwd(),
                'success': False,
                'error': 'timeout'
            }
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return {
                'command': command,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': 0,
                'cwd': cwd or os.getcwd(),
                'success': False,
                'error': str(e)
            }


class TerminalController:
    """
    Terminal control using ANSI sequences and capability detection.
    Provides cross-platform terminal manipulation.
    """
    
    def __init__(self):
        self.term = Terminal() if Terminal else None
        self.capabilities = self._detect_terminal_capabilities()
        logger.info("TerminalController initialized")
        logger.debug(f"Terminal capabilities: {self.capabilities}")
    
    def _detect_terminal_capabilities(self) -> Dict[str, bool]:
        """Detect terminal capabilities"""
        caps = {
            'colors': False,
            'cursor_control': False,
            'clear_screen': False,
            'resize_detection': False,
        }
        
        if self.term:
            caps.update({
                'colors': self.term.number_of_colors > 0,
                'cursor_control': hasattr(self.term, 'move'),
                'clear_screen': hasattr(self.term, 'clear'),
                'resize_detection': hasattr(self.term, 'width'),
            })
        
        # Fallback detection
        if not caps['colors']:
            caps['colors'] = os.getenv('TERM', '').find('color') != -1
        
        return caps
    
    def clear_screen(self) -> bool:
        """Clear the terminal screen"""
        try:
            if self.term and self.capabilities['clear_screen']:
                print(self.term.clear, end='')
            else:
                # Fallback to ANSI escape sequence
                print('\033[2J\033[H', end='')
            sys.stdout.flush()
            return True
        except Exception as e:
            logger.error(f"Error clearing screen: {e}")
            return False
    
    def move_cursor(self, x: int, y: int) -> bool:
        """Move cursor to position (x, y)"""
        try:
            if self.term and self.capabilities['cursor_control']:
                print(self.term.move(y, x), end='')
            else:
                # Fallback to ANSI escape sequence
                print(f'\033[{y+1};{x+1}H', end='')
            sys.stdout.flush()
            return True
        except Exception as e:
            logger.error(f"Error moving cursor to ({x}, {y}): {e}")
            return False
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal size as (width, height)"""
        try:
            if self.term:
                return (self.term.width, self.term.height)
            else:
                # Fallback to os.get_terminal_size
                size = os.get_terminal_size()
                return (size.columns, size.lines)
        except Exception as e:
            logger.error(f"Error getting terminal size: {e}")
            return (80, 24)  # Default fallback
    
    def set_title(self, title: str) -> bool:
        """Set terminal window title"""
        try:
            # ANSI escape sequence for setting title
            print(f'\033]0;{title}\007', end='')
            sys.stdout.flush()
            logger.info(f"Terminal title set to: {title}")
            return True
        except Exception as e:
            logger.error(f"Error setting terminal title: {e}")
            return False


class SessionManager:
    """
    Manages terminal sessions with persistence and recovery capabilities.
    """
    
    def __init__(self, db_path: str = "terminal_sessions.db"):
        self.db_path = db_path
        self.sessions: Dict[str, TerminalSession] = {}
        self._init_database()
        self._load_sessions()
        logger.info(f"SessionManager initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize SQLite database for session persistence"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    terminal_type TEXT,
                    pid INTEGER,
                    working_dir TEXT,
                    environment TEXT,
                    created_at REAL,
                    last_active REAL,
                    status TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processes (
                    pid INTEGER PRIMARY KEY,
                    command TEXT,
                    cwd TEXT,
                    created_at REAL,
                    status TEXT,
                    terminal_id TEXT,
                    FOREIGN KEY (terminal_id) REFERENCES sessions (session_id)
                )
            """)
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def _load_sessions(self):
        """Load existing sessions from database"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT * FROM sessions WHERE status = 'active'")
            for row in cursor.fetchall():
                session_id, terminal_type, pid, working_dir, environment, created_at, last_active, status = row
                
                # Check if process is still running
                if psutil and psutil.pid_exists(pid):
                    self.sessions[session_id] = TerminalSession(
                        session_id=session_id,
                        terminal_type=terminal_type,
                        pid=pid,
                        working_dir=working_dir,
                        environment=json.loads(environment),
                        created_at=created_at,
                        last_active=last_active,
                        status=status
                    )
                else:
                    # Mark as terminated if process no longer exists
                    cursor.execute(
                        "UPDATE sessions SET status = 'terminated' WHERE session_id = ?",
                        (session_id,)
                    )
            
            self.conn.commit()
            
            logger.info(f"Loaded {len(self.sessions)} active sessions")
            
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
    
    def create_session(self, terminal_type: str = "bash", 
                      working_dir: Optional[str] = None,
                      environment: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Create a new terminal session"""
        try:
            import uuid
            session_id = str(uuid.uuid4())[:8]
            
            if working_dir is None:
                working_dir = os.getcwd()
            
            if environment is None:
                environment = {}
            
            # Create session object
            session = TerminalSession(
                session_id=session_id,
                terminal_type=terminal_type,
                pid=0,  # Will be set when process is actually created
                working_dir=working_dir,
                environment=environment,
                created_at=time.time(),
                last_active=time.time(),
                status="created"
            )
            
            # Store in memory
            self.sessions[session_id] = session
            
            # Persist to database
            self._save_session(session)
            
            logger.info(f"Created session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def _save_session(self, session: TerminalSession):
        """Save session to database"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, terminal_type, pid, working_dir, environment, created_at, last_active, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.terminal_type,
                session.pid,
                session.working_dir,
                json.dumps(session.environment),
                session.created_at,
                session.last_active,
                session.status
            ))
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[TerminalSession]:
        """List all active sessions"""
        return [s for s in self.sessions.values() if s.status == "active"]
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a session"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.status = "terminated"
                session.last_active = time.time()
                
                # Kill associated process if it exists
                if session.pid > 0 and psutil and psutil.pid_exists(session.pid):
                    psutil.Process(session.pid).terminate()
                
                # Update database
                self._save_session(session)
                
                logger.info(f"Terminated session {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error terminating session {session_id}: {e}")
            return False


# === TERMINAL SPAWNING LAYER ===
class TerminalSpawner:
    """
    Advanced terminal creation and management with multi-platform support.
    Handles different terminal emulators and window managers.
    """
    
    def __init__(self):
        self.system = SystemInterface()
        self.available_terminals = self._detect_available_terminals()
        self.window_manager = self._detect_window_manager()
        logger.info(f"TerminalSpawner initialized with {len(self.available_terminals)} terminal types")
        logger.debug(f"Available terminals: {list(self.available_terminals.keys())}")
    
    def _detect_available_terminals(self) -> Dict[str, Dict[str, Any]]:
        """Detect available terminal emulators"""
        terminals = {}
        
        # Define terminal configurations
        terminal_configs = {
            'gnome-terminal': {
                'command': 'gnome-terminal',
                'new_tab_args': ['--tab'],
                'new_window_args': ['--window'],
                'title_args': ['--title'],
                'working_dir_args': ['--working-directory'],
                'execute_args': ['--', 'bash', '-c'],
                'geometry_args': ['--geometry'],
                'supports_tabs': True,
                'supports_geometry': True,
            },
            'konsole': {
                'command': 'konsole',
                'new_tab_args': ['--new-tab'],
                'new_window_args': [],
                'title_args': ['--title'],
                'working_dir_args': ['--workdir'],
                'execute_args': ['-e'],
                'supports_tabs': True,
                'supports_geometry': False,
            },
            'xterm': {
                'command': 'xterm',
                'new_tab_args': [],  # xterm doesn't support tabs natively
                'new_window_args': [],
                'title_args': ['-title'],
                'working_dir_args': [],  # Set via cd command
                'execute_args': ['-e'],
                'geometry_args': ['-geometry'],
                'supports_tabs': False,
                'supports_geometry': True,
            },
            'terminator': {
                'command': 'terminator',
                'new_tab_args': ['--new-tab'],
                'new_window_args': [],
                'title_args': ['--title'],
                'working_dir_args': ['--working-directory'],
                'execute_args': ['-x'],
                'supports_tabs': True,
                'supports_geometry': True,
            },
            'alacritty': {
                'command': 'alacritty',
                'new_tab_args': [],  # Use tmux or similar for tabs
                'new_window_args': [],
                'title_args': ['--title'],
                'working_dir_args': ['--working-directory'],
                'execute_args': ['-e'],
                'supports_tabs': False,
                'supports_geometry': False,
            },
        }
        
        # Check which terminals are available
        for name, config in terminal_configs.items():
            if os.system(f'which {config["command"]} >/dev/null 2>&1') == 0:
                terminals[name] = config
                logger.debug(f"Found terminal: {name}")
        
        # Add fallback if no GUI terminals found
        if not terminals:
            terminals['bash'] = {
                'command': 'bash',
                'new_tab_args': [],
                'new_window_args': [],
                'title_args': [],
                'working_dir_args': [],
                'execute_args': ['-c'],
                'supports_tabs': False,
                'supports_geometry': False,
            }
        
        return terminals
    
    def _detect_window_manager(self) -> Optional[str]:
        """Detect the current window manager"""
        wm_detection = {
            'GNOME': lambda: os.getenv('GNOME_DESKTOP_SESSION_ID') is not None,
            'KDE': lambda: os.getenv('KDE_FULL_SESSION') is not None,
            'XFCE': lambda: os.getenv('XFCE_SESSION') is not None,
            'i3': lambda: os.system('pgrep i3 >/dev/null 2>&1') == 0,
            'X11': lambda: os.getenv('DISPLAY') is not None,
        }
        
        for wm_name, detect_func in wm_detection.items():
            try:
                if detect_func():
                    logger.debug(f"Detected window manager: {wm_name}")
                    return wm_name
            except:
                continue
        
        return None
    
    def get_preferred_terminal(self) -> Optional[str]:
        """Get the preferred terminal based on environment"""
        preference_order = []
        
        # Order by window manager
        if self.window_manager == 'GNOME':
            preference_order = ['gnome-terminal', 'terminator', 'xterm']
        elif self.window_manager == 'KDE':
            preference_order = ['konsole', 'gnome-terminal', 'xterm']
        else:
            preference_order = ['gnome-terminal', 'konsole', 'terminator', 'xterm', 'alacritty']
        
        # Return first available
        for terminal in preference_order:
            if terminal in self.available_terminals:
                return terminal
        
        # Fallback to any available
        if self.available_terminals:
            return list(self.available_terminals.keys())[0]
        
        return None
    
    def spawn_terminal(self, 
                      terminal_type: Optional[str] = None,
                      working_dir: Optional[str] = None,
                      title: Optional[str] = None,
                      command: Optional[str] = None,
                      geometry: Optional[str] = None,
                      new_window: bool = True) -> Optional[ProcessInfo]:
        """
        Spawn a new terminal window or tab.
        
        Args:
            terminal_type: Type of terminal to spawn (auto-detect if None)
            working_dir: Working directory for the terminal
            title: Window title
            command: Command to execute in terminal
            geometry: Window geometry (e.g., "80x24+100+100")
            new_window: Create new window vs new tab
        
        Returns:
            ProcessInfo for the spawned terminal, or None if failed
        """
        try:
            # Auto-select terminal if not specified
            if terminal_type is None:
                terminal_type = self.get_preferred_terminal()
            
            if terminal_type not in self.available_terminals:
                logger.error(f"Terminal type '{terminal_type}' not available")
                return None
            
            config = self.available_terminals[terminal_type]
            cmd_args = [config['command']]
            
            # Build command arguments
            if new_window and config.get('new_window_args'):
                cmd_args.extend(config['new_window_args'])
            elif not new_window and config.get('new_tab_args'):
                cmd_args.extend(config['new_tab_args'])
            
            if title and config.get('title_args'):
                cmd_args.extend(config['title_args'])
                cmd_args.append(title)
            
            if geometry and config.get('geometry_args'):
                cmd_args.extend(config['geometry_args'])
                cmd_args.append(geometry)
            
            if working_dir and config.get('working_dir_args'):
                cmd_args.extend(config['working_dir_args'])
                cmd_args.append(working_dir)
            
            if command and config.get('execute_args'):
                cmd_args.extend(config['execute_args'])
                if working_dir and not config.get('working_dir_args'):
                    # Prepend cd command if terminal doesn't support working dir directly
                    command = f"cd '{working_dir}' && {command}"
                cmd_args.append(command)
            
            # Execute terminal spawn command
            logger.info(f"Spawning terminal: {' '.join(cmd_args)}")
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(0.1)
            
            if process.poll() is None:
                # Process is running
                process_info = ProcessInfo(
                    pid=process.pid,
                    command=' '.join(cmd_args),
                    cwd=working_dir or os.getcwd(),
                    created_at=time.time(),
                    status='running',
                    terminal_id=f"{terminal_type}_{process.pid}"
                )
                
                logger.info(f"Successfully spawned {terminal_type} terminal (PID: {process.pid})")
                return process_info
            else:
                # Process failed to start
                stderr_output = process.stderr.read() if process.stderr else "Unknown error"
                logger.error(f"Failed to spawn terminal: {stderr_output}")
                return None
                
        except Exception as e:
            logger.error(f"Error spawning terminal: {e}")
            return None
    
    def spawn_multiple_terminals(self, 
                                count: int = 2,
                                terminal_type: Optional[str] = None,
                                layout: str = "grid",
                                base_title: str = "Terminal") -> List[ProcessInfo]:
        """
        Spawn multiple terminal windows with automatic layout.
        
        Args:
            count: Number of terminals to spawn
            terminal_type: Type of terminal to use
            layout: Layout pattern ("grid", "horizontal", "vertical")
            base_title: Base title for terminals
        
        Returns:
            List of ProcessInfo for spawned terminals
        """
        terminals = []
        
        # Calculate positions for grid layout
        if layout == "grid":
            cols = int(count ** 0.5) + (1 if count ** 0.5 != int(count ** 0.5) else 0)
            rows = (count + cols - 1) // cols
        elif layout == "horizontal":
            cols = count
            rows = 1
        else:  # vertical
            cols = 1
            rows = count
        
        # Spawn terminals with positioning
        for i in range(count):
            if layout != "none":
                col = i % cols
                row = i // cols
                # Basic positioning - can be enhanced based on screen size
                x = col * 600 + 50
                y = row * 400 + 50
                geometry = f"80x24+{x}+{y}"
            else:
                geometry = None
            
            title = f"{base_title} {i+1}" if count > 1 else base_title
            
            terminal_info = self.spawn_terminal(
                terminal_type=terminal_type,
                title=title,
                geometry=geometry,
                new_window=True
            )
            
            if terminal_info:
                terminals.append(terminal_info)
                time.sleep(0.2)  # Small delay between spawns
        
        logger.info(f"Spawned {len(terminals)} terminals in {layout} layout")
        return terminals


class WindowManager:
    """
    Window management utilities for positioning and controlling terminal windows.
    """
    
    def __init__(self):
        self.system = SystemInterface()
        self.capabilities = self._detect_capabilities()
        logger.debug(f"WindowManager capabilities: {self.capabilities}")
    
    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detect window management capabilities"""
        caps = {
            'xdotool': os.system('which xdotool >/dev/null 2>&1') == 0,
            'wmctrl': os.system('which wmctrl >/dev/null 2>&1') == 0,
            'xwininfo': os.system('which xwininfo >/dev/null 2>&1') == 0,
        }
        
        if sys.platform.startswith('win'):
            caps.update({
                'win32_api': win32gui is not None,
            })
        elif sys.platform.startswith('darwin'):
            caps.update({
                'applescript': NSAppleScript is not None,
            })
        
        return caps
    
    def list_windows(self, filter_title: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all windows, optionally filtered by title"""
        windows = []
        
        try:
            if self.capabilities.get('wmctrl'):
                result = subprocess.run(
                    ['wmctrl', '-l'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.split(None, 3)
                            if len(parts) >= 4:
                                window_id, desktop, pid, title = parts[0], parts[1], parts[2], parts[3]
                                
                                if filter_title is None or filter_title.lower() in title.lower():
                                    windows.append({
                                        'window_id': window_id,
                                        'desktop': desktop,
                                        'pid': pid,
                                        'title': title
                                    })
            
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
        
        return windows
    
    def focus_window(self, window_id: str) -> bool:
        """Focus a specific window by ID"""
        try:
            if self.capabilities.get('wmctrl'):
                result = subprocess.run(
                    ['wmctrl', '-i', '-a', window_id],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Error focusing window {window_id}: {e}")
        
        return False
    
    def move_window(self, window_id: str, x: int, y: int) -> bool:
        """Move a window to specific coordinates"""
        try:
            if self.capabilities.get('wmctrl'):
                result = subprocess.run(
                    ['wmctrl', '-i', '-r', window_id, '-e', f'0,{x},{y},-1,-1'],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Error moving window {window_id}: {e}")
        
        return False
    
    def resize_window(self, window_id: str, width: int, height: int) -> bool:
        """Resize a window to specific dimensions"""
        try:
            if self.capabilities.get('wmctrl'):
                result = subprocess.run(
                    ['wmctrl', '-i', '-r', window_id, '-e', f'0,-1,-1,{width},{height}'],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Error resizing window {window_id}: {e}")
        
        return False


# === PUBLIC API LAYER ===
# Initialize global instances
_system = SystemInterface()
_terminal = TerminalController()
_sessions = SessionManager()
_spawner = TerminalSpawner()
_window_manager = WindowManager()


def execute_command(command: str, 
                   cwd: Optional[str] = None,
                   timeout: Optional[float] = None,
                   capture_output: bool = True) -> Dict[str, Any]:
    """
    Execute a command with comprehensive error handling and logging.
    
    Args:
        command: Shell command to execute
        cwd: Working directory (default: current directory)
        timeout: Timeout in seconds (default: no timeout)
        capture_output: Whether to capture stdout/stderr (default: True)
    
    Returns:
        Dict with execution results
        
    Example:
        python -c "from tools import execute_command; print(execute_command('ls -la'))"
    """
    result = _system.execute_command(command, cwd, None, timeout, capture_output)
    
    # Print human-readable output
    if result['success']:
        print(f"✓ Command succeeded: {command}")
        if result['stdout'] and capture_output:
            print("Output:", result['stdout'])
    else:
        print(f"✗ Command failed: {command}")
        if result['stderr']:
            print("Error:", result['stderr'])
    
    return result


def get_processes(name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of running processes.
    
    Args:
        name_filter: Optional filter by process name
    
    Returns:
        List of process information dictionaries
        
    Example:
        python -c "from tools import get_processes; print(get_processes('python'))"
    """
    processes = _system.get_processes(name_filter)
    process_dicts = [asdict(p) for p in processes]
    
    print(f"Found {len(process_dicts)} processes" + (f" matching '{name_filter}'" if name_filter else ""))
    for proc in process_dicts[:10]:  # Show first 10
        print(f"  PID {proc['pid']}: {proc['command'][:60]}...")
    
    return process_dicts


def clear_terminal() -> bool:
    """
    Clear the terminal screen.
    
    Returns:
        True if successful, False otherwise
        
    Example:
        python -c "from tools import clear_terminal; clear_terminal()"
    """
    success = _terminal.clear_screen()
    if success:
        print("Terminal cleared")
    else:
        print("Failed to clear terminal")
    return success


def set_terminal_title(title: str) -> bool:
    """
    Set the terminal window title.
    
    Args:
        title: New title for the terminal window
    
    Returns:
        True if successful, False otherwise
        
    Example:
        python -c "from tools import set_terminal_title; set_terminal_title('My Terminal')"
    """
    success = _terminal.set_title(title)
    if success:
        print(f"Terminal title set to: {title}")
    else:
        print(f"Failed to set terminal title")
    return success


def get_terminal_info() -> Dict[str, Any]:
    """
    Get information about the current terminal.
    
    Returns:
        Dictionary with terminal information
        
    Example:
        python -c "from tools import get_terminal_info; print(get_terminal_info())"
    """
    width, height = _terminal.get_terminal_size()
    info = {
        'size': {'width': width, 'height': height},
        'capabilities': _terminal.capabilities,
        'platform': _system.platform,
        'system_capabilities': _system.capabilities
    }
    
    print(f"Terminal: {width}x{height}")
    print(f"Platform: {_system.platform}")
    print(f"Capabilities: {len([k for k, v in info['capabilities'].items() if v])} available")
    
    return info


def create_terminal_session(terminal_type: str = "bash",
                          working_dir: Optional[str] = None) -> Optional[str]:
    """
    Create a new terminal session.
    
    Args:
        terminal_type: Type of terminal to create (default: bash)
        working_dir: Working directory for the session
    
    Returns:
        Session ID if successful, None otherwise
        
    Example:
        python -c "from tools import create_terminal_session; print(create_terminal_session())"
    """
    session_id = _sessions.create_session(terminal_type, working_dir)
    if session_id:
        print(f"Created terminal session: {session_id}")
    else:
        print("Failed to create terminal session")
    return session_id


def list_terminal_sessions() -> List[Dict[str, Any]]:
    """
    List all active terminal sessions.
    
    Returns:
        List of session information dictionaries
        
    Example:
        python -c "from tools import list_terminal_sessions; print(list_terminal_sessions())"
    """
    sessions = _sessions.list_sessions()
    session_dicts = [asdict(s) for s in sessions]
    
    print(f"Active sessions: {len(session_dicts)}")
    for session in session_dicts:
        print(f"  {session['session_id']}: {session['terminal_type']} in {session['working_dir']}")
    
    return session_dicts


def spawn_terminal(terminal_type: Optional[str] = None,
                  working_dir: Optional[str] = None,
                  title: Optional[str] = None,
                  command: Optional[str] = None,
                  geometry: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Spawn a new terminal window.
    
    Args:
        terminal_type: Type of terminal ('gnome-terminal', 'konsole', 'xterm', etc.)
        working_dir: Working directory for the terminal
        title: Window title
        command: Command to execute in terminal
        geometry: Window geometry (e.g., "80x24+100+100")
    
    Returns:
        Process information dictionary, or None if failed
        
    Example:
        python -c "from tools import spawn_terminal; spawn_terminal(title='My Terminal', working_dir='/tmp')"
    """
    process_info = _spawner.spawn_terminal(
        terminal_type=terminal_type,
        working_dir=working_dir,
        title=title,
        command=command,
        geometry=geometry,
        new_window=True
    )
    
    if process_info:
        process_dict = asdict(process_info)
        print(f"✓ Spawned {terminal_type or 'default'} terminal (PID: {process_info.pid})")
        if title:
            print(f"  Title: {title}")
        if working_dir:
            print(f"  Working directory: {working_dir}")
        return process_dict
    else:
        print("✗ Failed to spawn terminal")
        return None


def spawn_multiple_terminals(count: int = 2,
                            terminal_type: Optional[str] = None,
                            layout: str = "grid",
                            base_title: str = "Terminal") -> List[Dict[str, Any]]:
    """
    Spawn multiple terminal windows with automatic layout.
    
    Args:
        count: Number of terminals to spawn
        terminal_type: Type of terminal to use
        layout: Layout pattern ("grid", "horizontal", "vertical", "none")
        base_title: Base title for terminals
    
    Returns:
        List of process information dictionaries
        
    Example:
        python -c "from tools import spawn_multiple_terminals; spawn_multiple_terminals(4, layout='grid')"
    """
    terminals = _spawner.spawn_multiple_terminals(
        count=count,
        terminal_type=terminal_type,
        layout=layout,
        base_title=base_title
    )
    
    terminal_dicts = [asdict(t) for t in terminals]
    
    if terminals:
        print(f"✓ Spawned {len(terminals)} terminals in {layout} layout")
        for i, terminal in enumerate(terminals):
            print(f"  Terminal {i+1}: PID {terminal.pid}")
    else:
        print("✗ Failed to spawn terminals")
    
    return terminal_dicts


def get_available_terminals() -> Dict[str, Any]:
    """
    Get information about available terminal emulators.
    
    Returns:
        Dictionary with available terminals and their capabilities
        
    Example:
        python -c "from tools import get_available_terminals; print(get_available_terminals())"
    """
    available = _spawner.available_terminals
    preferred = _spawner.get_preferred_terminal()
    window_manager = _spawner.window_manager
    
    info = {
        'available_terminals': list(available.keys()),
        'preferred_terminal': preferred,
        'window_manager': window_manager,
        'terminal_details': available
    }
    
    print(f"Available terminals: {len(available)}")
    for name in available.keys():
        marker = " (preferred)" if name == preferred else ""
        print(f"  - {name}{marker}")
    
    if window_manager:
        print(f"Window manager: {window_manager}")
    
    return info


def list_windows(filter_title: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all windows, optionally filtered by title.
    
    Args:
        filter_title: Optional filter by window title
    
    Returns:
        List of window information dictionaries
        
    Example:
        python -c "from tools import list_windows; print(list_windows('Terminal'))"
    """
    windows = _window_manager.list_windows(filter_title)
    
    print(f"Found {len(windows)} windows" + (f" matching '{filter_title}'" if filter_title else ""))
    for window in windows[:10]:  # Show first 10
        print(f"  {window['window_id']}: {window['title']}")
    
    return windows


def focus_window(window_id: str) -> bool:
    """
    Focus a specific window by ID.
    
    Args:
        window_id: Window ID from list_windows()
    
    Returns:
        True if successful, False otherwise
        
    Example:
        python -c "from tools import focus_window; focus_window('0x12345678')"
    """
    success = _window_manager.focus_window(window_id)
    
    if success:
        print(f"✓ Focused window {window_id}")
    else:
        print(f"✗ Failed to focus window {window_id}")
    
    return success


def move_window(window_id: str, x: int, y: int) -> bool:
    """
    Move a window to specific coordinates.
    
    Args:
        window_id: Window ID from list_windows()
        x: X coordinate
        y: Y coordinate
    
    Returns:
        True if successful, False otherwise
        
    Example:
        python -c "from tools import move_window; move_window('0x12345678', 100, 100)"
    """
    success = _window_manager.move_window(window_id, x, y)
    
    if success:
        print(f"✓ Moved window {window_id} to ({x}, {y})")
    else:
        print(f"✗ Failed to move window {window_id}")
    
    return success


def resize_window(window_id: str, width: int, height: int) -> bool:
    """
    Resize a window to specific dimensions.
    
    Args:
        window_id: Window ID from list_windows()
        width: New width in pixels
        height: New height in pixels
    
    Returns:
        True if successful, False otherwise
        
    Example:
        python -c "from tools import resize_window; resize_window('0x12345678', 800, 600)"
    """
    success = _window_manager.resize_window(window_id, width, height)
    
    if success:
        print(f"✓ Resized window {window_id} to {width}x{height}")
    else:
        print(f"✗ Failed to resize window {window_id}")
    
    return success


# === COGNITIVE OPERATING SYSTEM LAYER ===
class CognitiveOrchestrator:
    """
    Cognitive Operating System orchestrator that manages screen sharing,
    AI processing, and terminal control integration.
    """
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.terminal_controller = TerminalController()
        self.window_manager = WindowManager()
        self.daemon_process = None
        self.cognitive_sessions = {}
        self._initialize_cognitive_schema()
        
        logger.info("CognitiveOrchestrator initialized")
    
    def _initialize_cognitive_schema(self):
        """Initialize cognitive session schema in database"""
        try:
            cursor = self.session_manager.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cognitive_sessions (
                    session_id TEXT PRIMARY KEY,
                    daemon_pid INTEGER,
                    websocket_port INTEGER,
                    screen_context TEXT,
                    ai_conversation TEXT,
                    active_terminals TEXT,
                    cognitive_state TEXT,
                    created_at REAL,
                    last_activity REAL,
                    status TEXT DEFAULT 'active'
                )
            ''')
            self.session_manager.conn.commit()
            logger.info("Cognitive session schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize cognitive schema: {e}")
    
    def create_cognitive_session(self, websocket_port: int = 8080) -> str:
        """Create a new cognitive session"""
        session_id = str(uuid.uuid4())[:8]
        timestamp = time.time()
        
        session = CognitiveSession(
            session_id=session_id,
            daemon_pid=None,
            websocket_port=websocket_port,
            screen_context={},
            ai_conversation=[],
            active_terminals=[],
            cognitive_state={},
            created_at=timestamp,
            last_activity=timestamp
        )
        
        # Store in database
        cursor = self.session_manager.conn.cursor()
        cursor.execute('''
            INSERT INTO cognitive_sessions 
            (session_id, daemon_pid, websocket_port, screen_context, 
             ai_conversation, active_terminals, cognitive_state, 
             created_at, last_activity, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, None, websocket_port,
            json.dumps({}), json.dumps([]), json.dumps([]),
            json.dumps({}), timestamp, timestamp, 'active'
        ))
        self.session_manager.conn.commit()
        
        self.cognitive_sessions[session_id] = session
        logger.info(f"Created cognitive session: {session_id}")
        return session_id
    
    def start_daemon(self, session_id: str, background: bool = True) -> Dict[str, Any]:
        """Start the cognitive OS daemon"""
        if session_id not in self.cognitive_sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.cognitive_sessions[session_id]
        
        # Create daemon command
        daemon_script = f"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

class CognitiveDaemon:
    def __init__(self, port={session.websocket_port}):
        self.port = port
        self.clients = set()
        
    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"🧬 Cognitive client connected: {{websocket.remote_address}}")
        
    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"🧬 Cognitive client disconnected: {{websocket.remote_address}}")
        
    async def handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'test':
                response = {{
                    'type': 'test_response',
                    'message': f"🧬 Cognitive OS received: {{data.get('message')}}",
                    'timestamp': datetime.now().isoformat(),
                    'session_id': '{session_id}'
                }}
                await websocket.send(json.dumps(response))
                
            elif msg_type == 'screen_frame':
                print(f"🧠 Processing screen frame for session {session_id}")
                # TODO: Process with AI and trigger terminal actions
                
        except Exception as e:
            print(f"❌ Cognitive daemon error: {{e}}")
    
    async def client_handler(self, websocket):
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if websocket in self.clients:
                await self.unregister(websocket)
    
    async def start(self):
        print(f"🧬 Starting Cognitive OS daemon on port {{self.port}}")
        async with websockets.serve(self.client_handler, "localhost", self.port):
            await asyncio.Future()

daemon = CognitiveDaemon()
asyncio.run(daemon.start())
"""
        
        # Write daemon script to temp file
        daemon_file = f"/tmp/cognitive_daemon_{session_id}.py"
        with open(daemon_file, 'w') as f:
            f.write(daemon_script)
        
        # Start daemon process
        if background:
            cmd = f"nohup python3 {daemon_file} > /tmp/cognitive_daemon_{session_id}.log 2>&1 &"
        else:
            cmd = f"python3 {daemon_file}"
        
        try:
            if background:
                process = subprocess.Popen(cmd, shell=True)
                daemon_pid = process.pid
                
                # Update session with daemon PID
                session.daemon_pid = daemon_pid
                cursor = self.session_manager.conn.cursor()
                cursor.execute('''
                    UPDATE cognitive_sessions 
                    SET daemon_pid = ?, last_activity = ?
                    WHERE session_id = ?
                ''', (daemon_pid, time.time(), session_id))
                self.session_manager.conn.commit()
                
                logger.info(f"Started cognitive daemon (PID: {daemon_pid}) for session {session_id}")
                return {
                    "success": True,
                    "session_id": session_id,
                    "daemon_pid": daemon_pid,
                    "websocket_port": session.websocket_port,
                    "daemon_file": daemon_file
                }
            else:
                # Run in foreground (blocking)
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                }
                
        except Exception as e:
            logger.error(f"Failed to start cognitive daemon: {e}")
            return {"success": False, "error": str(e)}
    
    def get_cognitive_status(self, session_id: str = None) -> Dict[str, Any]:
        """Get status of cognitive sessions"""
        if session_id:
            if session_id in self.cognitive_sessions:
                session = self.cognitive_sessions[session_id]
                return {
                    "session_id": session_id,
                    "daemon_pid": session.daemon_pid,
                    "websocket_port": session.websocket_port,
                    "status": session.status,
                    "active_terminals": len(session.active_terminals),
                    "last_activity": session.last_activity
                }
            else:
                return {"error": "Session not found"}
        else:
            return {
                "active_sessions": len(self.cognitive_sessions),
                "sessions": [self.get_cognitive_status(sid) for sid in self.cognitive_sessions.keys()]
            }
    
    def stop_daemon(self, session_id: str) -> Dict[str, Any]:
        """Stop cognitive daemon for session"""
        if session_id not in self.cognitive_sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.cognitive_sessions[session_id]
        if session.daemon_pid:
            try:
                os.kill(session.daemon_pid, signal.SIGTERM)
                session.daemon_pid = None
                
                # Update database
                cursor = self.session_manager.conn.cursor()
                cursor.execute('''
                    UPDATE cognitive_sessions 
                    SET daemon_pid = NULL, status = 'stopped', last_activity = ?
                    WHERE session_id = ?
                ''', (time.time(), session_id))
                self.session_manager.conn.commit()
                
                logger.info(f"Stopped cognitive daemon for session {session_id}")
                return {"success": True, "session_id": session_id}
            except ProcessLookupError:
                logger.warning(f"Daemon process not found for session {session_id}")
                return {"success": True, "message": "Process already stopped"}
            except Exception as e:
                logger.error(f"Failed to stop daemon: {e}")
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": "No daemon running"}


# Global cognitive orchestrator instance
_cognitive_orchestrator = CognitiveOrchestrator()


# === COGNITIVE OS PUBLIC API ===
def start_cognitive_os(auto_start_browser: bool = True, websocket_port: int = 8080) -> Dict[str, Any]:
    """
    Start the Cognitive Operating System daemon.
    
    Args:
        auto_start_browser: Whether to automatically open browser interface
        websocket_port: Port for WebSocket server
    
    Returns:
        Dict with session info and daemon details
        
    Example:
        python -c "from tools import start_cognitive_os; print(start_cognitive_os())"
    """
    # Create cognitive session
    session_id = _cognitive_orchestrator.create_cognitive_session(websocket_port)
    
    # Start daemon
    daemon_result = _cognitive_orchestrator.start_daemon(session_id, background=True)
    
    if daemon_result["success"]:
        print(f"🧬 Cognitive OS started - Session: {session_id}")
        print(f"🚀 Daemon PID: {daemon_result['daemon_pid']}")
        print(f"🔗 WebSocket: ws://localhost:{websocket_port}/ws")
        
        # Optionally start browser interface
        if auto_start_browser:
            try:
                browser_file = "/home/evilbastardxd/cognitive-os-v04/auto_screen_capture.html"
                if os.path.exists(browser_file):
                    subprocess.Popen(f"nohup firefox {browser_file} > /dev/null 2>&1 &", shell=True)
                    print(f"🌐 Browser interface opened")
            except Exception as e:
                logger.warning(f"Failed to open browser: {e}")
        
        return {
            "success": True,
            "session_id": session_id,
            "daemon_pid": daemon_result["daemon_pid"],
            "websocket_port": websocket_port,
            "browser_interface": browser_file if auto_start_browser else None
        }
    else:
        print(f"❌ Failed to start Cognitive OS: {daemon_result.get('error')}")
        return daemon_result


def cognitive_status(session_id: str = None) -> Dict[str, Any]:
    """
    Get status of Cognitive OS sessions.
    
    Args:
        session_id: Specific session to check, or None for all sessions
    
    Returns:
        Dict with session status information
        
    Example:
        python -c "from tools import cognitive_status; print(cognitive_status())"
    """
    status = _cognitive_orchestrator.get_cognitive_status(session_id)
    
    if session_id:
        if "error" not in status:
            print(f"🧬 Session {session_id}: {status['status']}")
            print(f"🚀 Daemon PID: {status['daemon_pid']}")
            print(f"⚡ Active terminals: {status['active_terminals']}")
        else:
            print(f"❌ {status['error']}")
    else:
        print(f"🧬 Cognitive OS - Active sessions: {status['active_sessions']}")
        for session in status['sessions']:
            if "error" not in session:
                print(f"  • {session['session_id']}: {session['status']} (PID: {session['daemon_pid']})")
    
    return status


def stop_cognitive_os(session_id: str = None) -> Dict[str, Any]:
    """
    Stop Cognitive OS daemon(s).
    
    Args:
        session_id: Specific session to stop, or None to stop all
    
    Returns:
        Dict with stop operation results
        
    Example:
        python -c "from tools import stop_cognitive_os; print(stop_cognitive_os())"
    """
    if session_id:
        result = _cognitive_orchestrator.stop_daemon(session_id)
        if result["success"]:
            print(f"🧬 Stopped Cognitive OS session: {session_id}")
        else:
            print(f"❌ Failed to stop session {session_id}: {result.get('error')}")
        return result
    else:
        # Stop all sessions
        status = _cognitive_orchestrator.get_cognitive_status()
        results = []
        
        for session in status['sessions']:
            if "error" not in session and session['daemon_pid']:
                result = _cognitive_orchestrator.stop_daemon(session['session_id'])
                results.append(result)
        
        if results:
            stopped_count = sum(1 for r in results if r["success"])
            print(f"🧬 Stopped {stopped_count}/{len(results)} Cognitive OS sessions")
        else:
            print("🧬 No active Cognitive OS sessions to stop")
        
        return {"stopped_sessions": len(results), "results": results}


if __name__ == "__main__":
    # Self-test when run directly
    print("=== tools.py v0.2 - Terminal & Window Management ===")
    print("Testing enhanced functionality...")
    
    # Test system info
    print("\n1. System Information:")
    info = get_terminal_info()
    
    # Test available terminals
    print("\n2. Available Terminals:")
    terminals = get_available_terminals()
    
    # Test command execution
    print("\n3. Command Execution:")
    result = execute_command("echo 'Hello from tools.py v0.2'")
    
    # Test window listing
    print("\n4. Window Management:")
    windows = list_windows()
    
    # Test session creation
    print("\n5. Session Management:")
    session_id = create_terminal_session()
    if session_id:
        sessions = list_terminal_sessions()
    
    print("\n=== v0.2 Enhanced Layer Operational ✓ ===")
    print("Features available:")
    print("  ✓ Terminal spawning with auto-detection")
    print("  ✓ Multi-terminal layouts (grid/horizontal/vertical)")
    print("  ✓ Window management (focus/move/resize)")
    print("  ✓ Cross-platform terminal support")
    print("  ✓ Persistent session management")
    print("  ✓ Comprehensive error handling and logging")