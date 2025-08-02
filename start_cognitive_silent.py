#!/usr/bin/env python3
"""
Start Cognitive OS silently with all components as background subprocesses
"""

import subprocess
import time
import os
import sys
import signal
import atexit

# Track subprocess PIDs for cleanup
subprocesses = []

def cleanup():
    """Clean up all subprocesses on exit"""
    for proc in subprocesses:
        try:
            if proc.poll() is None:  # Process is still running
                proc.terminate()
                proc.wait(timeout=5)
        except:
            pass

# Register cleanup function
atexit.register(cleanup)

def start_cognitive_silent():
    """Start Cognitive OS completely in background"""
    
    print("🧬 COGNITIVE OS v0.4 - SILENT BACKGROUND MODE")
    print("=" * 50)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Start Enhanced Daemon as subprocess
    print("1️⃣ Starting Enhanced Cognitive Daemon...")
    daemon_proc = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "enhanced_cognitive_daemon.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=base_dir
    )
    subprocesses.append(daemon_proc)
    print(f"✅ Daemon started (PID: {daemon_proc.pid})")
    
    # Wait for daemon to initialize
    time.sleep(2)
    
    # Step 2: Start browser with auto screen capture
    print("2️⃣ Starting browser with auto screen capture...")
    browser_file = os.path.join(base_dir, "auto_screen_capture.html")
    
    # Create a wrapper script to handle browser startup
    browser_script = f"""#!/bin/bash
    # Wait a moment for daemon to be ready
    sleep 1
    # Open browser with auto screen capture
    firefox {browser_file} 2>/dev/null &
    """
    
    browser_proc = subprocess.Popen(
        ["bash", "-c", browser_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("✅ Browser launched with auto screen capture")
    
    # Step 3: Optionally start monitor (can be disabled for true silent mode)
    monitor_enabled = True  # Set to False for completely silent operation
    monitor_proc = None
    
    if monitor_enabled:
        print("3️⃣ Starting screen monitor...")
        monitor_proc = subprocess.Popen(
            [sys.executable, os.path.join(base_dir, "live_screen_monitor.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=base_dir
        )
        subprocesses.append(monitor_proc)
        print(f"✅ Monitor started (PID: {monitor_proc.pid})")
    
    # Step 4: Save process info
    pid_file = os.path.join(base_dir, ".cognitive_pids")
    with open(pid_file, "w") as f:
        f.write(f"daemon_pid={daemon_proc.pid}\n")
        if monitor_proc:
            f.write(f"monitor_pid={monitor_proc.pid}\n")
        f.write(f"websocket_port=8084\n")
        f.write(f"timestamp={time.time()}\n")
    
    print("\n" + "=" * 50)
    print("🚀 COGNITIVE OS RUNNING IN BACKGROUND")
    print("=" * 50)
    print(f"📊 Daemon PID: {daemon_proc.pid}")
    if monitor_proc:
        print(f"📊 Monitor PID: {monitor_proc.pid}")
    print(f"🔗 WebSocket: ws://localhost:8084/ws")
    print(f"📁 PID file: {pid_file}")
    
    print("\n📋 Management Commands:")
    print("  - Check processes: ps aux | grep cognitive")
    print("  - View daemon logs: tail -f daemon.log")
    print("  - Stop daemon: kill", daemon_proc.pid)
    print("  - Stop all: python3 stop_cognitive_silent.py")
    
    print("\n✅ Screen sharing will auto-start when you:")
    print("  1. Grant screen permission in Firefox")
    print("  2. Select the screen/window to share")
    
    # Optional: Keep script running to monitor subprocesses
    keep_running = False  # Set to True to monitor subprocesses
    
    if keep_running:
        print("\n🔄 Monitoring subprocesses (Ctrl+C to stop all)...")
        try:
            while True:
                # Check if daemon is still running
                if daemon_proc.poll() is not None:
                    print("⚠️ Daemon stopped unexpectedly!")
                    break
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping all processes...")
            cleanup()
    
    return {
        "success": True,
        "daemon_pid": daemon_proc.pid,
        "monitor_pid": monitor_proc.pid if monitor_proc else None,
        "websocket_port": 8084,
        "pid_file": pid_file
    }

if __name__ == "__main__":
    result = start_cognitive_silent()
    
    # Exit immediately if not keeping running
    if not result.get("keep_running", False):
        print("\n💡 Processes running in background. Script exiting.")
        # Detach from subprocesses
        for proc in subprocesses:
            proc.stdout = None
            proc.stderr = None