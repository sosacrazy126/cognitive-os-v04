#!/usr/bin/env python3
"""
Enhanced Cognitive OS Debug Tool with Multiple Access Methods
"""

import asyncio
import websockets
import json
import time
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List

# Setup comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/tmp/cognitive_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CognitiveDebugger:
    def __init__(self):
        self.active_ports = [8080, 8081, 8082, 8083]
        self.screen_data_received = False
        self.message_count = 0
        
    async def test_port(self, port: int) -> Dict[str, Any]:
        """Test a specific WebSocket port"""
        uri = f'ws://localhost:{port}/ws'
        result = {
            'port': port,
            'connected': False,
            'session_id': None,
            'messages_received': 0,
            'screen_frames': 0,
            'error': None
        }
        
        try:
            logger.info(f"Testing connection to port {port}")
            async with websockets.connect(uri, timeout=3) as websocket:
                result['connected'] = True
                logger.info(f"✅ Connected to port {port}")
                
                # Send test message
                test_msg = {
                    'type': 'test',
                    'message': f'Debug test from port {port}',
                    'timestamp': datetime.now().isoformat()
                }
                await websocket.send(json.dumps(test_msg))
                logger.debug(f"📤 Sent test message to port {port}")
                
                # Listen for responses
                try:
                    while True:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(response)
                        result['messages_received'] += 1
                        
                        if data.get('type') == 'test_response':
                            result['session_id'] = data.get('session_id')
                            logger.info(f"📥 Test response from port {port}: {data.get('message')}")
                            
                        elif data.get('type') == 'screen_frame':
                            result['screen_frames'] += 1
                            logger.info(f"📺 Screen frame received on port {port}!")
                            self.screen_data_received = True
                            
                        else:
                            logger.debug(f"📨 Other message on port {port}: {data.get('type')}")
                            
                except asyncio.TimeoutError:
                    logger.debug(f"⏰ No more messages on port {port}")
                    
        except Exception as e:
            result['error'] = str(e)
            logger.warning(f"❌ Port {port} failed: {e}")
            
        return result
    
    async def monitor_all_ports(self) -> List[Dict[str, Any]]:
        """Monitor all active ports simultaneously"""
        logger.info("🔍 Monitoring all Cognitive OS ports...")
        tasks = [self.test_port(port) for port in self.active_ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, dict)]
        return valid_results
    
    def check_daemon_logs(self):
        """Check all daemon log files"""
        logger.info("📋 Checking daemon logs...")
        import glob
        
        log_files = glob.glob('/tmp/cognitive_daemon_*.log')
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    if content.strip():
                        logger.info(f"📋 {log_file}:")
                        logger.info(content[-300:])  # Last 300 chars
                    else:
                        logger.info(f"📋 {log_file}: Empty")
            except Exception as e:
                logger.error(f"Error reading {log_file}: {e}")
    
    def check_network_status(self):
        """Check network connections and processes"""
        logger.info("🌐 Checking network status...")
        
        # Check listening ports
        netstat = subprocess.run('netstat -tuln | grep 808', shell=True, capture_output=True, text=True)
        logger.info(f"Active 808x ports:\n{netstat.stdout}")
        
        # Check daemon processes
        ps_check = subprocess.run('ps aux | grep cognitive_daemon | grep -v grep', shell=True, capture_output=True, text=True)
        daemon_lines = ps_check.stdout.strip().split('\n') if ps_check.stdout.strip() else []
        logger.info(f"Active daemons: {len(daemon_lines)}")
        for line in daemon_lines:
            logger.info(f"  🔄 {line}")
    
    async def enhanced_screen_monitoring(self, port: int = 8083, duration: int = 10):
        """Enhanced screen frame monitoring with detailed logging"""
        uri = f'ws://localhost:{port}/ws'
        logger.info(f"🧬 Starting enhanced screen monitoring on port {port} for {duration} seconds")
        
        try:
            async with websockets.connect(uri) as websocket:
                logger.info(f"✅ Connected to enhanced monitoring on port {port}")
                
                # Send enhanced test message
                enhanced_msg = {
                    'type': 'test',
                    'message': 'Enhanced screen monitoring active',
                    'debug': True,
                    'timestamp': datetime.now().isoformat()
                }
                await websocket.send(json.dumps(enhanced_msg))
                
                start_time = time.time()
                message_count = 0
                screen_frame_count = 0
                
                while time.time() - start_time < duration:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        message_count += 1
                        
                        msg_type = data.get('type')
                        logger.info(f"📨 Message {message_count}: {msg_type}")
                        
                        if msg_type == 'screen_frame':
                            screen_frame_count += 1
                            frame_size = len(message)
                            logger.info(f"📺 SCREEN FRAME {screen_frame_count}: {frame_size} bytes")
                            
                            # Log frame metadata if available
                            if 'width' in data:
                                logger.info(f"   Resolution: {data.get('width')}x{data.get('height')}")
                            if 'timestamp' in data:
                                logger.info(f"   Timestamp: {data.get('timestamp')}")
                                
                        elif msg_type == 'test_response':
                            logger.info(f"   Response: {data.get('message')}")
                            logger.info(f"   Session: {data.get('session_id')}")
                            
                    except asyncio.TimeoutError:
                        logger.debug("⏰ Waiting for messages...")
                        
                logger.info(f"🏁 Monitoring complete: {message_count} messages, {screen_frame_count} screen frames")
                return {
                    'total_messages': message_count,
                    'screen_frames': screen_frame_count,
                    'duration': duration,
                    'frames_per_second': screen_frame_count / duration if duration > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"❌ Enhanced monitoring failed: {e}")
            return {'error': str(e)}

async def run_comprehensive_test():
    """Run comprehensive Cognitive OS connectivity test"""
    debugger = CognitiveDebugger()
    
    print("🧬 COMPREHENSIVE COGNITIVE OS DEBUG TEST")
    print("=" * 60)
    
    # Check system status
    debugger.check_network_status()
    debugger.check_daemon_logs()
    
    # Test all ports
    print("\n1️⃣ Testing all WebSocket ports...")
    port_results = await debugger.monitor_all_ports()
    
    active_sessions = [r for r in port_results if r['connected']]
    print(f"✅ Active sessions: {len(active_sessions)}")
    
    for result in active_sessions:
        print(f"   Port {result['port']}: Session {result['session_id']} - {result['messages_received']} msgs, {result['screen_frames']} frames")
    
    # Enhanced monitoring on primary port
    if active_sessions:
        primary_port = active_sessions[0]['port']
        print(f"\n2️⃣ Enhanced monitoring on port {primary_port}...")
        monitoring_result = await debugger.enhanced_screen_monitoring(primary_port, duration=5)
        print(f"Monitoring result: {monitoring_result}")
    
    print(f"\n🧬 DEBUG COMPLETE - Screen data received: {debugger.screen_data_received}")
    print("📋 Full logs available in: /tmp/cognitive_debug.log")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())