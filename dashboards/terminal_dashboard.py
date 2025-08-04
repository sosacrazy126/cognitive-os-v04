#!/usr/bin/env python3
"""
Terminal Dashboard - Real-time monitoring and control interface
Interactive dashboard for managing cognitive agents
"""

import curses
import time
import threading
import json
from datetime import datetime
from typing import Dict, List, Any
import subprocess
from enhanced_terminal_orchestrator import get_orchestrator, AgentType

class TerminalDashboard:
    """
    Real-time terminal-based dashboard for cognitive agent monitoring
    """
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.refresh_rate = 1.0  # seconds
        self.running = True
        self.selected_session = 0
        self.view_mode = "overview"  # overview, details, logs
        self.last_update = datetime.now()
        
    def run(self):
        """Run the interactive dashboard"""
        curses.wrapper(self._main_loop)
    
    def _main_loop(self, stdscr):
        """Main dashboard loop"""
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(100) # 100ms timeout
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Success
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warning
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Info
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Highlight
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Header
        
        while self.running:
            try:
                # Clear screen
                stdscr.clear()
                
                # Get screen dimensions
                height, width = stdscr.getmaxyx()
                
                # Render dashboard
                if self.view_mode == "overview":
                    self._render_overview(stdscr, height, width)
                elif self.view_mode == "details":
                    self._render_details(stdscr, height, width)
                elif self.view_mode == "logs":
                    self._render_logs(stdscr, height, width)
                
                # Handle input
                self._handle_input(stdscr)
                
                # Refresh screen
                stdscr.refresh()
                
                # Sleep
                time.sleep(self.refresh_rate)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                # Error handling in curses context
                stdscr.addstr(height-1, 0, f"Error: {str(e)[:width-10]}")
                stdscr.refresh()
                time.sleep(2)
    
    def _render_overview(self, stdscr, height, width):
        """Render overview dashboard"""
        # Header
        self._render_header(stdscr, width)
        
        # Get dashboard data
        dashboard = self.orchestrator.generate_dashboard_report()
        
        # System status
        row = 3
        stdscr.addstr(row, 2, "🧬 COGNITIVE OS - TERMINAL ORCHESTRATOR", curses.color_pair(6))
        row += 2
        
        # Statistics
        stdscr.addstr(row, 2, f"📊 Active Sessions: {dashboard['total_active_sessions']}")
        row += 1
        
        if dashboard['system_resources']['total_cpu_percent'] > 0:
            stdscr.addstr(row, 2, f"⚡ CPU Usage: {dashboard['system_resources']['total_cpu_percent']:.1f}%")
            row += 1
            stdscr.addstr(row, 2, f"🧠 Memory Usage: {dashboard['system_resources']['total_memory_mb']:.1f} MB")
            row += 1
        
        # Available terminals
        terminals = ", ".join(dashboard['available_terminals'])
        stdscr.addstr(row, 2, f"🖥️  Available Terminals: {terminals[:width-25]}")
        row += 2
        
        # Active sessions
        if dashboard['active_sessions']:
            stdscr.addstr(row, 2, "🤖 ACTIVE COGNITIVE AGENTS:", curses.color_pair(4))
            row += 1
            stdscr.addstr(row, 2, "=" * (width - 4))
            row += 1
            
            # Headers
            headers = f"{'ID':<12} {'Agent Type':<18} {'Status':<10} {'Duration':<10} {'CPU%':<8} {'Memory':<10}"
            stdscr.addstr(row, 2, headers)
            row += 1
            stdscr.addstr(row, 2, "-" * len(headers))
            row += 1
            
            # Session list
            for i, session in enumerate(dashboard['active_sessions']):
                if row >= height - 5:  # Leave space for controls
                    break
                
                # Highlight selected session
                color = curses.color_pair(5) if i == self.selected_session else 0
                
                session_id = session['session_id'][:12]
                agent_type = session['agent_type'][:18]
                status = session['status'][:10]
                duration = f"{session['duration_seconds']}s"[:10]
                cpu = f"{session['cpu_percent']:.1f}"[:7]
                memory = f"{session['memory_mb']:.1f}MB"[:10]
                
                line = f"{session_id:<12} {agent_type:<18} {status:<10} {duration:<10} {cpu:<8} {memory:<10}"
                stdscr.addstr(row, 2, line, color)
                row += 1
        else:
            stdscr.addstr(row, 2, "No active sessions")
            row += 1
        
        # Agent distribution
        if dashboard['agent_distribution']:
            row += 1
            stdscr.addstr(row, 2, "📈 AGENT DISTRIBUTION:", curses.color_pair(4))
            row += 1
            for agent_type, count in dashboard['agent_distribution'].items():
                stdscr.addstr(row, 4, f"• {agent_type}: {count}")
                row += 1
        
        # Controls
        self._render_controls(stdscr, height, width)
    
    def _render_details(self, stdscr, height, width):
        """Render detailed view of selected session"""
        self._render_header(stdscr, width)
        
        sessions = self.orchestrator.list_active_sessions()
        
        if not sessions or self.selected_session >= len(sessions):
            stdscr.addstr(5, 2, "No session selected or available")
            self._render_controls(stdscr, height, width)
            return
        
        session = sessions[self.selected_session]
        
        row = 4
        stdscr.addstr(row, 2, f"🔍 SESSION DETAILS: {session['session_id']}", curses.color_pair(6))
        row += 2
        
        # Session information
        details = [
            ("Agent Type", session['agent_type']),
            ("Agent Name", session['agent_name']),
            ("Process ID", str(session['pid'])),
            ("Status", session['status']),
            ("Terminal Type", session['terminal_type']),
            ("Start Time", session['start_time']),
            ("Duration", f"{session['duration_seconds']} seconds"),
            ("CPU Usage", f"{session['cpu_percent']:.2f}%"),
            ("Memory Usage", f"{session['memory_mb']:.2f} MB"),
            ("Last Activity", session['last_activity'])
        ]
        
        for label, value in details:
            if row >= height - 5:
                break
            stdscr.addstr(row, 2, f"{label:<15}: {value}")
            row += 1
        
        # Process information
        row += 1
        stdscr.addstr(row, 2, "🔍 PROCESS ANALYSIS:", curses.color_pair(4))
        row += 1
        
        try:
            import psutil
            process = psutil.Process(session['pid'])
            
            process_info = [
                ("Command Line", " ".join(process.cmdline())[:width-20]),
                ("Working Dir", process.cwd()[:width-20]),
                ("Status", process.status()),
                ("Created", datetime.fromtimestamp(process.create_time()).strftime("%Y-%m-%d %H:%M:%S")),
                ("Threads", str(process.num_threads())),
                ("Open Files", str(len(process.open_files())))
            ]
            
            for label, value in process_info:
                if row >= height - 5:
                    break
                stdscr.addstr(row, 2, f"{label:<15}: {value}")
                row += 1
                
        except Exception as e:
            stdscr.addstr(row, 2, f"Process info unavailable: {str(e)[:width-25]}")
        
        self._render_controls(stdscr, height, width)
    
    def _render_logs(self, stdscr, height, width):
        """Render logs view"""
        self._render_header(stdscr, width)
        
        row = 4
        stdscr.addstr(row, 2, "📜 SYSTEM LOGS", curses.color_pair(6))
        row += 2
        
        # Read recent log entries
        try:
            with open("terminal_orchestra.log", "r") as f:
                lines = f.readlines()
                # Show last 20 lines
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                
                for line in recent_lines:
                    if row >= height - 5:
                        break
                    # Truncate line to fit screen
                    display_line = line.strip()[:width-4]
                    
                    # Color code based on log level
                    color = 0
                    if "ERROR" in line:
                        color = curses.color_pair(2)
                    elif "WARNING" in line:
                        color = curses.color_pair(3)
                    elif "INFO" in line:
                        color = curses.color_pair(1)
                    
                    stdscr.addstr(row, 2, display_line, color)
                    row += 1
        
        except FileNotFoundError:
            stdscr.addstr(row, 2, "No logs available")
        except Exception as e:
            stdscr.addstr(row, 2, f"Error reading logs: {str(e)}")
        
        self._render_controls(stdscr, height, width)
    
    def _render_header(self, stdscr, width):
        """Render dashboard header"""
        header = "🧬 COGNITIVE OS v0.4 - TERMINAL DASHBOARD"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Center the header
        header_x = max(0, (width - len(header)) // 2)
        
        stdscr.addstr(0, header_x, header, curses.color_pair(6))
        stdscr.addstr(1, width - len(timestamp) - 2, timestamp, curses.color_pair(4))
    
    def _render_controls(self, stdscr, height, width):
        """Render control instructions"""
        controls = [
            "Controls: [↑/↓] Navigate  [Enter] Details  [T] Terminate  [S] Spawn  [L] Logs  [Q] Quit",
            f"View: {self.view_mode.upper()}  |  Refresh: {self.refresh_rate}s  |  Selected: {self.selected_session}"
        ]
        
        for i, control_text in enumerate(controls):
            row = height - 3 + i
            if row < height:
                stdscr.addstr(row, 0, control_text[:width], curses.color_pair(6))
    
    def _handle_input(self, stdscr):
        """Handle keyboard input"""
        key = stdscr.getch()
        
        if key == ord('q') or key == ord('Q'):
            self.running = False
        
        elif key == curses.KEY_UP:
            self.selected_session = max(0, self.selected_session - 1)
        
        elif key == curses.KEY_DOWN:
            sessions = self.orchestrator.list_active_sessions()
            if sessions:
                self.selected_session = min(len(sessions) - 1, self.selected_session + 1)
        
        elif key == ord('\n') or key == ord('\r'):  # Enter
            self.view_mode = "details"
        
        elif key == ord('o') or key == ord('O'):
            self.view_mode = "overview"
        
        elif key == ord('l') or key == ord('L'):
            self.view_mode = "logs"
        
        elif key == ord('t') or key == ord('T'):
            self._terminate_selected_session()
        
        elif key == ord('s') or key == ord('S'):
            self._spawn_agent_menu(stdscr)
        
        elif key == ord('r') or key == ord('R'):
            # Force refresh
            pass
        
        elif key == ord('+'):
            self.refresh_rate = min(5.0, self.refresh_rate + 0.5)
        
        elif key == ord('-'):
            self.refresh_rate = max(0.5, self.refresh_rate - 0.5)
    
    def _terminate_selected_session(self):
        """Terminate the selected session"""
        sessions = self.orchestrator.list_active_sessions()
        if sessions and self.selected_session < len(sessions):
            session = sessions[self.selected_session]
            self.orchestrator.terminate_session(session['session_id'])
    
    def _spawn_agent_menu(self, stdscr):
        """Show agent spawning menu"""
        # Simple agent type selection
        # This is a basic implementation - could be enhanced with a proper menu
        agent_types = [
            ("1", AgentType.DEBUG_ASSISTANT, "Debug Assistant"),
            ("2", AgentType.TEST_GENERATOR, "Test Generator"),
            ("3", AgentType.DOCS_WRITER, "Documentation Writer"),
            ("4", AgentType.CODE_REVIEWER, "Code Reviewer"),
            ("5", AgentType.SECURITY_AUDITOR, "Security Auditor"),
            ("T", None, "Full Development Team"),
            ("A", None, "Full Audit Team")
        ]
        
        # Clear area for menu
        height, width = stdscr.getmaxyx()
        menu_start = height // 2 - 5
        
        stdscr.addstr(menu_start, 2, "🚀 SPAWN AGENT - Select type:", curses.color_pair(6))
        
        for i, (key, agent_type, name) in enumerate(agent_types):
            stdscr.addstr(menu_start + 2 + i, 4, f"[{key}] {name}")
        
        stdscr.addstr(menu_start + 2 + len(agent_types), 4, "[ESC] Cancel")
        stdscr.refresh()
        
        # Wait for selection
        while True:
            key = stdscr.getch()
            
            if key == 27:  # ESC
                break
            
            # Find matching option
            for option_key, agent_type, name in agent_types:
                if key == ord(option_key) or key == ord(option_key.lower()):
                    if agent_type:
                        self.orchestrator.spawn_agent(agent_type)
                    elif option_key == "T":
                        from enhanced_terminal_orchestrator import spawn_development_team
                        spawn_development_team()
                    elif option_key == "A":
                        from enhanced_terminal_orchestrator import spawn_full_audit_team
                        spawn_full_audit_team()
                    return
            
            time.sleep(0.1)

def main():
    """Main dashboard entry point"""
    try:
        dashboard = TerminalDashboard()
        dashboard.run()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard shutdown by user")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    finally:
        print("✅ Dashboard closed")

if __name__ == "__main__":
    main()