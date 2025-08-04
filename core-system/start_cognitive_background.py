#!/usr/bin/env python3
"""
Start Cognitive OS with full screen sharing in background terminals
"""

import subprocess
import time
import os
import tools

def start_cognitive_background():
    """Start Cognitive OS with all components in background"""
    
    print("🧬 COGNITIVE OS v0.4 - BACKGROUND STARTUP")
    print("=" * 50)
    
    # Step 1: Start Enhanced Daemon in background terminal
    print("1️⃣ Starting Enhanced Cognitive Daemon in background terminal...")
    daemon_cmd = f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 enhanced_cognitive_daemon.py"
    daemon_terminal = tools.spawn_terminal(
        title="Cognitive Daemon",
        command=daemon_cmd
    )
    
    if daemon_terminal['success']:
        print(f"✅ Daemon started in terminal (PID: {daemon_terminal['pid']})")
    else:
        print(f"❌ Failed to start daemon: {daemon_terminal.get('error')}")
        return
    
    # Wait for daemon to initialize
    time.sleep(2)
    
    # Step 2: Start browser with auto screen capture in background
    print("2️⃣ Starting auto screen capture in browser...")
    browser_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_screen_capture.html")
    
    # Use nohup to detach browser completely
    browser_cmd = f"nohup firefox {browser_file} > /dev/null 2>&1 &"
    subprocess.Popen(browser_cmd, shell=True)
    print("✅ Browser launched in background with auto screen capture")
    
    # Step 3: Start monitoring terminal in background
    print("3️⃣ Starting live screen monitor in background terminal...")
    monitor_cmd = f"cd {os.path.dirname(os.path.abspath(__file__))} && python3 live_screen_monitor.py"
    monitor_terminal = tools.spawn_terminal(
        title="Screen Monitor",
        command=monitor_cmd
    )
    
    if monitor_terminal['success']:
        print(f"✅ Monitor started in terminal (PID: {monitor_terminal['pid']})")
    else:
        print(f"❌ Failed to start monitor: {monitor_terminal.get('error')}")
    
    # Step 4: Create session in database
    print("4️⃣ Creating cognitive session record...")
    session_id = tools._cognitive_orchestrator.create_cognitive_session(
        websocket_port=8084,
        daemon_pid=daemon_terminal['pid']
    )
    print(f"✅ Session created: {session_id}")
    
    print("\n" + "=" * 50)
    print("🚀 COGNITIVE OS STARTED IN BACKGROUND")
    print("=" * 50)
    print(f"📊 Daemon Terminal PID: {daemon_terminal['pid']}")
    print(f"📊 Monitor Terminal PID: {monitor_terminal['pid']}")
    print(f"🔗 WebSocket: ws://localhost:8084/ws")
    print(f"🆔 Session ID: {session_id}")
    print("\n📋 Commands:")
    print("  - Check status: python3 -c \"import tools; tools.cognitive_status()\"")
    print("  - Stop all: python3 -c \"import tools; tools.stop_cognitive_os()\"")
    print("\n🎯 Screen sharing will start automatically in browser!")
    
    return {
        "success": True,
        "session_id": session_id,
        "daemon_pid": daemon_terminal['pid'],
        "monitor_pid": monitor_terminal['pid'],
        "websocket_port": 8084
    }

if __name__ == "__main__":
    start_cognitive_background()