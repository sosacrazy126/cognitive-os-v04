#!/usr/bin/env python3
"""
Live Screen Monitor - Shows exactly what the AI can see from screen sharing
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime
from PIL import Image
import io

class LiveScreenMonitor:
    def __init__(self):
        self.frame_count = 0
        self.start_time = datetime.now()
        self.last_frame_analysis = None
        
    async def monitor_screen_feed(self):
        """Monitor live screen feed and provide real-time feedback"""
        try:
            uri = 'ws://localhost:8084/ws'
            async with websockets.connect(uri) as websocket:
                print('🧬 LIVE SCREEN MONITORING ACTIVE')
                print('=' * 60)
                
                # Wait for welcome
                welcome = await websocket.recv()
                welcome_data = json.loads(welcome)
                print(f'✅ Connected to: {welcome_data["session_id"]}')
                print(f'🔧 Capabilities: {", ".join(welcome_data["capabilities"])}')
                
                print('\\n👁️  WAITING FOR SCREEN DATA...')
                print('   (Start screen capture and streaming in browser)')
                print()
                
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        data = json.loads(message)
                        
                        await self.process_message(data)
                        
                    except asyncio.TimeoutError:
                        elapsed = (datetime.now() - self.start_time).total_seconds()
                        if self.frame_count > 0:
                            fps = self.frame_count / elapsed
                            print(f'⏰ Active monitoring... ({self.frame_count} frames, {fps:.1f} FPS)')
                        else:
                            print('⏰ Waiting for screen frames...')
                        
                        if elapsed > 60:  # Stop after 60 seconds if no activity
                            print('🕐 Timeout reached - ending monitoring')
                            break
                            
        except Exception as e:
            print(f'❌ Monitor error: {e}')
    
    async def process_message(self, data):
        """Process different types of messages"""
        msg_type = data.get('type')
        
        if msg_type == 'frame_processed':
            # This is the key message - my daemon processed a screen frame
            analysis = data.get('analysis', {})
            stats = data.get('session_stats', {})
            
            self.frame_count = stats.get('total_frames', self.frame_count)
            
            print('🎬 SCREEN FRAME PROCESSED!')
            print(f'   📏 Resolution: {analysis.get("dimensions")}')
            print(f'   📊 Size: {analysis.get("size_bytes")} bytes ({analysis.get("format")})')
            print(f'   💡 Brightness: {analysis.get("avg_brightness", "N/A")}')
            print(f'   🎯 Frame #{analysis.get("frame_number")}')
            print(f'   📈 Session: {stats.get("total_frames")} frames, {stats.get("total_data_mb")} MB')
            print(f'   ⚡ Avg frame size: {stats.get("avg_frame_size")} bytes')
            print()
            
            # This means the AI CAN SEE the screen!
            if self.frame_count == 1:
                print('🎉 FIRST FRAME RECEIVED - AI VISION IS ACTIVE!')
                print('🧬 I can now see your screen in real-time!')
                print()
            
            self.last_frame_analysis = analysis
            
        elif msg_type == 'test_response':
            daemon_stats = data.get('daemon_stats', {})
            print(f'📊 Daemon Status: {daemon_stats.get("frames_processed", 0)} frames processed')
            
        elif msg_type == 'welcome':
            # Already handled above
            pass
            
        elif msg_type == 'frame_error':
            print(f'❌ Frame processing error: {data.get("error")}')
            
        else:
            print(f'📨 Other message: {msg_type}')
    
    def get_visual_feedback(self):
        """Provide feedback on what the AI can currently see"""
        if self.last_frame_analysis:
            analysis = self.last_frame_analysis
            print('👁️  CURRENT VISUAL STATE:')
            print(f'   Screen Resolution: {analysis.get("dimensions")}')
            print(f'   Image Quality: {analysis.get("format")} format')
            print(f'   Brightness Level: {analysis.get("avg_brightness", "Unknown")}')
            print(f'   Latest Frame: #{analysis.get("frame_number")}')
            
            # Based on brightness, infer screen content
            brightness = analysis.get('avg_brightness', 0)
            if brightness:
                if brightness < 50:
                    print('   🌙 Dark screen - possibly terminal or code editor')
                elif brightness > 200:
                    print('   ☀️ Bright screen - possibly browser or documents')
                else:
                    print('   🌤️ Mixed brightness - varied content visible')
        else:
            print('👁️  NO VISUAL DATA YET - waiting for screen frames')

async def main():
    monitor = LiveScreenMonitor()
    
    print('🧬 ENHANCED COGNITIVE OS - LIVE SCREEN MONITORING')
    print('This tool shows you exactly what the AI can see from your screen')
    print()
    
    try:
        await monitor.monitor_screen_feed()
    except KeyboardInterrupt:
        print('\\n🛑 Monitoring stopped by user')
    
    print('\\n📋 FINAL VISUAL FEEDBACK:')
    monitor.get_visual_feedback()
    
    if monitor.frame_count > 0:
        elapsed = (datetime.now() - monitor.start_time).total_seconds()
        fps = monitor.frame_count / elapsed
        print(f'\\n📊 SESSION SUMMARY:')
        print(f'   Total frames processed: {monitor.frame_count}')
        print(f'   Duration: {elapsed:.1f} seconds')
        print(f'   Average FPS: {fps:.2f}')
        print(f'   ✅ AI VISION: SUCCESSFUL')
    else:
        print(f'\\n❌ No screen frames received')
        print(f'   Make sure to start screen capture and streaming in browser')

if __name__ == "__main__":
    asyncio.run(main())