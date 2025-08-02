#!/usr/bin/env python3
"""
Simple connection test for Cognitive OS
"""

import sys
import os
import asyncio
import websockets
import json

# Add the cognitive OS directory to path
sys.path.insert(0, '/home/evilbastardxd/cognitive-os-v04')

async def test_connection():
    """Test if the enhanced daemon is running"""
    try:
        print("🔗 Testing connection to ws://localhost:8084/ws")
        
        async with websockets.connect('ws://localhost:8084/ws') as websocket:
            print("✅ Connected successfully!")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            data = json.loads(welcome)
            print(f"🧬 Session: {data.get('session_id', 'unknown')}")
            print(f"💫 Capabilities: {data.get('capabilities', [])}")
            
            # Send test message
            test_msg = {'type': 'test', 'message': 'Connection test'}
            await websocket.send(json.dumps(test_msg))
            
            # Get response
            response = await websocket.recv()
            resp_data = json.loads(response)
            
            if resp_data.get('type') == 'test_response':
                print("📤 Test response received!")
                stats = resp_data.get('daemon_stats', {})
                print(f"📊 Frames processed: {stats.get('frames_processed', 0)}")
                print(f"👥 Clients connected: {stats.get('clients_connected', 0)}")
                print(f"💾 Data received: {stats.get('data_received_mb', 0)} MB")
                return True
            else:
                print(f"❓ Unexpected response: {resp_data}")
                return False
                
    except ConnectionRefusedError:
        print("❌ Connection refused - daemon not running")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_daemon_status():
    """Check if daemon processes are running"""
    import subprocess
    
    print("🔍 Checking for running daemon processes...")
    
    try:
        # Check for cognitive processes
        result = subprocess.run(['pgrep', '-f', 'enhanced_cognitive_daemon'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"✅ Found {len(pids)} daemon process(es):")
            for pid in pids:
                print(f"   PID: {pid}")
            return True
        else:
            print("❌ No daemon processes found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False

def start_daemon():
    """Start the enhanced daemon"""
    import subprocess
    
    print("🚀 Starting enhanced cognitive daemon...")
    
    try:
        daemon_path = '/home/evilbastardxd/cognitive-os-v04/enhanced_cognitive_daemon.py'
        
        # Start daemon in background
        process = subprocess.Popen([
            'python3', daemon_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Daemon started with PID: {process.pid}")
        print("⏰ Waiting 3 seconds for daemon to initialize...")
        
        import time
        time.sleep(3)
        
        # Check if it's still running
        if process.poll() is None:
            print("✅ Daemon appears to be running")
            return process
        else:
            print("❌ Daemon failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Error output: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start daemon: {e}")
        return None

async def main():
    print("🧬 COGNITIVE OS v0.4 - CONNECTION TEST")
    print("=" * 50)
    
    # Step 1: Check if daemon is already running
    daemon_running = check_daemon_status()
    
    if not daemon_running:
        print("\n🚀 No daemon found, starting one...")
        daemon_process = start_daemon()
        if not daemon_process:
            print("❌ Could not start daemon, exiting")
            return
    
    # Step 2: Test connection
    print("\n🔗 Testing WebSocket connection...")
    connection_success = await test_connection()
    
    if connection_success:
        print("\n🎉 SUCCESS! Cognitive OS daemon is running and responding")
        print("\n📋 Next steps:")
        print("1. Run: python -c \"from quick_screen_test import start_full_screen_test; start_full_screen_test()\"")
        print("2. Or use: python -c \"from quick_screen_test import quick_monitor; quick_monitor()\"")
    else:
        print("\n❌ Connection test failed")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if port 8084 is available: netstat -tulpn | grep 8084")
        print("2. Check daemon logs: tail -f /tmp/enhanced_cognitive_daemon.log")
        print("3. Restart the daemon manually: python3 enhanced_cognitive_daemon.py")

if __name__ == "__main__":
    asyncio.run(main())
