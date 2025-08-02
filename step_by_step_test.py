#!/usr/bin/env python3
"""
Step-by-step Cognitive OS Tester
Let's debug this together!
"""

import os
import sys
import subprocess
import time
import signal

def cleanup_existing():
    """Clean up any existing processes"""
    print("🧹 Step 1: Cleaning up existing processes...")
    
    try:
        # Kill any existing daemon processes
        subprocess.run(['pkill', '-f', 'enhanced_cognitive_daemon'], 
                      capture_output=True, timeout=5)
        subprocess.run(['pkill', '-f', 'auto_screen_test'], 
                      capture_output=True, timeout=5)
        print("✅ Cleanup completed")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def check_dependencies():
    """Check if required dependencies are available"""
    print("\n🔍 Step 2: Checking dependencies...")
    
    dependencies = ['websockets', 'PIL', 'psutil', 'asyncio']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️ Missing dependencies: {missing}")
        print("Install with: pip install websockets pillow psutil")
        return False
    
    print("✅ All dependencies available")
    return True

def start_daemon():
    """Start the enhanced daemon manually"""
    print("\n🚀 Step 3: Starting Enhanced Cognitive Daemon...")
    
    daemon_path = '/home/evilbastardxd/cognitive-os-v04/enhanced_cognitive_daemon.py'
    
    if not os.path.exists(daemon_path):
        print(f"❌ Daemon file not found: {daemon_path}")
        return None
    
    try:
        # Start daemon
        process = subprocess.Popen([
            sys.executable, daemon_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Daemon started with PID: {process.pid}")
        
        # Give it time to start
        print("⏰ Waiting 5 seconds for daemon to initialize...")
        time.sleep(5)
        
        # Check if still running
        if process.poll() is None:
            print("✅ Daemon is running!")
            return process
        else:
            print("❌ Daemon failed to start")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"STDOUT: {stdout.decode()}")
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start daemon: {e}")
        return None

def test_websocket():
    """Test WebSocket connection"""
    print("\n🔗 Step 4: Testing WebSocket connection...")
    
    # Create a simple test script
    test_script = '''
import asyncio
import websockets
import json

async def test():
    try:
        async with websockets.connect("ws://localhost:8084/ws") as websocket:
            print("✅ WebSocket connected!")
            
            # Wait for welcome
            welcome = await websocket.recv()
            data = json.loads(welcome)
            print(f"🧬 Session: {data.get('session_id')}")
            
            # Send test
            await websocket.send(json.dumps({"type": "test", "message": "Hello!"}))
            
            # Get response
            response = await websocket.recv()
            resp_data = json.loads(response)
            print(f"📤 Response: {resp_data.get('message', 'No message')}")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

result = asyncio.run(test())
exit(0 if result else 1)
'''
    
    try:
        result = subprocess.run([
            sys.executable, '-c', test_script
        ], capture_output=True, text=True, timeout=10)
        
        print("WebSocket Test Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ WebSocket test timed out")
        return False
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False

def run_browser_test():
    """Open browser interface"""
    print("\n🌐 Step 5: Opening browser interface...")
    
    html_file = '/home/evilbastardxd/cognitive-os-v04/enhanced_screen_capture.html'
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    try:
        # Open Firefox with the enhanced screen capture
        subprocess.Popen([
            'firefox', html_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Firefox opened with enhanced screen capture interface")
        print("\n📋 Manual steps:")
        print("1. In Firefox, click 'Start Screen Sharing'")
        print("2. Grant screen sharing permissions")
        print("3. You should see frames being processed in real-time")
        return True
        
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        return False

def main():
    print("🧬 COGNITIVE OS v0.4 - STEP-BY-STEP TESTER")
    print("=" * 60)
    
    # Change to the cognitive OS directory
    os.chdir('/home/evilbastardxd/cognitive-os-v04')
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Step 1: Cleanup
    cleanup_existing()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot proceed without dependencies")
        return
    
    # Step 3: Start daemon
    daemon_process = start_daemon()
    if not daemon_process:
        print("\n❌ Cannot proceed without daemon")
        return
    
    try:
        # Step 4: Test WebSocket
        websocket_success = test_websocket()
        
        if websocket_success:
            print("\n🎉 SUCCESS! WebSocket connection working!")
            
            # Step 5: Open browser
            browser_success = run_browser_test()
            
            if browser_success:
                print("\n🎉 FULL SUCCESS! System is ready for testing!")
                print("\n⏰ Daemon will continue running...")
                print("Press Ctrl+C to stop the daemon")
                
                # Keep daemon running
                try:
                    daemon_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping daemon...")
                    daemon_process.terminate()
                    daemon_process.wait()
                    print("✅ Daemon stopped")
            
        else:
            print("\n❌ WebSocket connection failed")
            daemon_process.terminate()
    
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        if daemon_process:
            daemon_process.terminate()

if __name__ == "__main__":
    main()
