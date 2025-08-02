#!/usr/bin/env python3
"""
Quick Screen Test Function - Simple function to start full automatic screen sharing test
"""

import tools
import subprocess
import time
import asyncio
import websockets
import json
from datetime import datetime

def start_full_screen_test():
    """
    Quick function to start complete automatic screen sharing test.
    
    Usage:
        python -c "from quick_screen_test import start_full_screen_test; start_full_screen_test()"
    """
    print("🧬 STARTING FULL AUTOMATIC SCREEN SHARING TEST")
    print("=" * 60)
    
    # Stop any existing processes first
    print("🧹 Cleaning up any existing processes...")
    subprocess.run("pkill -f enhanced_cognitive_daemon", shell=True)
    subprocess.run("pkill -f auto_screen_test", shell=True)
    time.sleep(1)
    
    # Start the auto test
    print("🚀 Launching automatic screen test...")
    subprocess.run(["python3", "/home/evilbastardxd/auto_screen_test.py"])

def quick_monitor():
    """
    Quick function to just monitor existing screen sharing.
    
    Usage:
        python -c "from quick_screen_test import quick_monitor; quick_monitor()"
    """
    import asyncio
    
    async def monitor():
        try:
            uri = 'ws://localhost:8084/ws'
            async with websockets.connect(uri) as websocket:
                print("🧬 QUICK MONITOR - Connected to Cognitive OS")
                
                # Wait for welcome
                welcome = await websocket.recv()
                data = json.loads(welcome)
                print(f"✅ Session: {data['session_id']}")
                print("\n👁️  MONITORING SCREEN FRAMES...")
                
                frame_count = 0
                start_time = datetime.now()
                
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        data = json.loads(message)
                        
                        if data.get('type') == 'frame_processed':
                            frame_count += 1
                            analysis = data.get('analysis', {})
                            
                            print(f"📺 FRAME {frame_count}: {analysis.get('dimensions')} - Brightness: {analysis.get('avg_brightness')}")
                            
                            if frame_count == 1:
                                print("🎉 AI VISION ACTIVE - I can see your screen!")
                                
                    except asyncio.TimeoutError:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        if frame_count > 0:
                            print(f"⏰ {frame_count} frames received ({frame_count/elapsed:.1f} FPS)")
                        else:
                            print("⏰ Waiting for screen frames...")
                            
                        if elapsed > 30:
                            break
                            
        except Exception as e:
            print(f"❌ Monitor error: {e}")
    
    print("🧬 QUICK SCREEN MONITOR")
    print("=" * 30)
    asyncio.run(monitor())

def test_connection():
    """
    Quick function to test if enhanced daemon is running.
    
    Usage:
        python -c "from quick_screen_test import test_connection; test_connection()"
    """
    import asyncio
    
    async def test():
        try:
            uri = 'ws://localhost:8084/ws'
            async with websockets.connect(uri) as websocket:
                print("✅ Enhanced Cognitive Daemon is running")
                
                welcome = await websocket.recv()
                data = json.loads(welcome)
                print(f"🧬 Session: {data['session_id']}")
                print(f"🔧 Capabilities: {', '.join(data['capabilities'])}")
                
                # Send test
                test_msg = {'type': 'test', 'message': 'Connection test'}
                await websocket.send(json.dumps(test_msg))
                
                response = await websocket.recv()
                resp_data = json.loads(response)
                stats = resp_data.get('daemon_stats', {})
                
                print(f"📊 Frames processed: {stats.get('frames_processed', 0)}")
                print(f"👥 Clients connected: {stats.get('clients_connected', 0)}")
                print(f"💾 Data received: {stats.get('data_received_mb', 0)} MB")
                
                return True
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("💡 Run start_full_screen_test() to start the daemon")
            return False
    
    print("🧬 TESTING DAEMON CONNECTION")
    print("=" * 30)
    return asyncio.run(test())

if __name__ == "__main__":
    print("🧬 Quick Screen Test Functions Available:")
    print("  start_full_screen_test() - Start complete automatic test")
    print("  quick_monitor() - Monitor existing screen sharing") 
    print("  test_connection() - Test if daemon is running")
    print()
    print("Usage examples:")
    print('  python -c "from quick_screen_test import start_full_screen_test; start_full_screen_test()"')
    print('  python -c "from quick_screen_test import quick_monitor; quick_monitor()"')
    print('  python -c "from quick_screen_test import test_connection; test_connection()"')