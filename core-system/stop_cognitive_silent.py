#!/usr/bin/env python3
"""
Stop Cognitive OS background processes
"""

import os
import signal
import subprocess

def stop_cognitive_silent():
    """Stop all Cognitive OS background processes"""
    
    print("🛑 STOPPING COGNITIVE OS BACKGROUND PROCESSES")
    print("=" * 50)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pid_file = os.path.join(base_dir, ".cognitive_pids")
    
    # Read PIDs from file
    if os.path.exists(pid_file):
        print(f"📁 Reading PIDs from {pid_file}")
        pids = {}
        with open(pid_file, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=")
                    if "pid" in key:
                        pids[key] = int(value)
        
        # Stop processes
        for name, pid in pids.items():
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✅ Stopped {name}: {pid}")
            except ProcessLookupError:
                print(f"⚠️ Process {name} ({pid}) not found")
            except Exception as e:
                print(f"❌ Error stopping {name} ({pid}): {e}")
        
        # Remove PID file
        os.remove(pid_file)
        print("✅ Removed PID file")
    else:
        print("⚠️ No PID file found")
    
    # Also try to find and stop any cognitive processes
    print("\n🔍 Searching for any remaining cognitive processes...")
    try:
        # Find cognitive daemon processes
        result = subprocess.run(
            ["pgrep", "-f", "cognitive_daemon"],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✅ Stopped cognitive daemon PID: {pid}")
                    except:
                        pass
        
        # Find screen monitor processes
        result = subprocess.run(
            ["pgrep", "-f", "live_screen_monitor"],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✅ Stopped screen monitor PID: {pid}")
                    except:
                        pass
                        
    except Exception as e:
        print(f"⚠️ Error searching for processes: {e}")
    
    print("\n✅ All Cognitive OS processes stopped")

if __name__ == "__main__":
    stop_cognitive_silent()