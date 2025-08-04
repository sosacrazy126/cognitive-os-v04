#!/usr/bin/env python3
"""
Enhanced Cognitive OS Daemon with Screen Frame Processing
"""

import asyncio
import websockets
import json
import logging
import base64
import time
from datetime import datetime
from typing import Dict, Any
import io
from PIL import Image

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/tmp/enhanced_cognitive_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedCognitiveDaemon:
    def __init__(self, port=8084):
        self.port = port
        self.clients = set()
        self.screen_frames_received = 0
        self.total_data_received = 0
        self.session_id = 'enhanced-cognitive-session'
        self.frame_processing_enabled = True
        
        logger.info(f"🧬 Enhanced Cognitive Daemon initializing on port {port}")
        
    async def register(self, websocket):
        """Register a new client with enhanced logging"""
        self.clients.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🔗 Client connected: {client_info} (Total clients: {len(self.clients)})")
        
        # Send welcome message
        welcome_msg = {
            'type': 'welcome',
            'message': '🧬 Connected to Enhanced Cognitive OS Daemon',
            'session_id': self.session_id,
            'capabilities': ['screen_processing', 'frame_analysis', 'real_time_feedback'],
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_msg))
        
    async def unregister(self, websocket):
        """Unregister a client"""
        if websocket in self.clients:
            self.clients.remove(websocket)
            logger.info(f"🔌 Client disconnected (Remaining clients: {len(self.clients)})")
        
    async def process_screen_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming screen frame data"""
        try:
            # Decode base64 image data
            image_data = base64.b64decode(frame_data['data'])
            
            # Process with PIL for analysis
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Basic frame analysis
            analysis = {
                'frame_number': frame_data.get('frameNumber', 0),
                'dimensions': f"{width}x{height}",
                'format': image.format or 'JPEG',
                'mode': image.mode,
                'size_bytes': len(image_data),
                'timestamp': frame_data.get('timestamp', time.time() * 1000)
            }
            
            # Advanced analysis (you can add AI processing here)
            # For now, we'll do basic image statistics
            if image.mode == 'RGB':
                # Get basic color statistics
                pixels = list(image.getdata())
                avg_brightness = sum(sum(pixel) for pixel in pixels) / (len(pixels) * 3)
                analysis['avg_brightness'] = round(avg_brightness, 2)
            
            self.screen_frames_received += 1
            self.total_data_received += len(image_data)
            
            logger.info(f"📺 Processed frame {analysis['frame_number']}: "
                       f"{analysis['dimensions']}, {analysis['size_bytes']} bytes, "
                       f"brightness: {analysis.get('avg_brightness', 'N/A')}")
            
            return {
                'type': 'frame_processed',
                'analysis': analysis,
                'session_stats': {
                    'total_frames': self.screen_frames_received,
                    'total_data_mb': round(self.total_data_received / (1024 * 1024), 2),
                    'avg_frame_size': round(self.total_data_received / max(self.screen_frames_received, 1), 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Frame processing error: {e}")
            return {
                'type': 'frame_error',
                'error': str(e),
                'frame_number': frame_data.get('frameNumber', 'unknown')
            }
    
    async def handle_message(self, websocket, message):
        """Handle incoming messages with enhanced processing"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            logger.debug(f"📨 Received message type: {msg_type} from {websocket.remote_address}")
            
            if msg_type == 'test':
                # Enhanced test response
                response = {
                    'type': 'test_response',
                    'message': f"🧬 Enhanced Cognitive OS received: {data.get('message')}",
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'daemon_stats': {
                        'frames_processed': self.screen_frames_received,
                        'clients_connected': len(self.clients),
                        'data_received_mb': round(self.total_data_received / (1024 * 1024), 2)
                    }
                }
                await websocket.send(json.dumps(response))
                logger.info(f"📤 Test response sent with stats")
                
            elif msg_type == 'screen_frame':
                if self.frame_processing_enabled:
                    # Process the screen frame
                    processing_result = await self.process_screen_frame(data)
                    
                    # Send processing feedback
                    await websocket.send(json.dumps(processing_result))
                    
                    # Log frame reception
                    frame_num = data.get('frameNumber', 'unknown')
                    frame_size = len(message)
                    logger.info(f"🎬 Frame {frame_num} processed: {frame_size} bytes total message")
                    
                    # TODO: This is where AI processing would happen
                    # You could integrate with Google AI Studio Live API here
                    # to analyze the screen content and generate terminal commands
                    
                else:
                    logger.debug(f"📺 Frame received but processing disabled")
                    
            elif msg_type == 'command':
                # Handle AI-generated commands (future enhancement)
                command = data.get('command', '')
                logger.info(f"⚡ AI Command received: {command}")
                
                # TODO: Execute command via tools.py integration
                response = {
                    'type': 'command_result',
                    'command': command,
                    'result': 'Command processing not implemented yet',
                    'timestamp': datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                
            else:
                logger.warning(f"❓ Unknown message type: {msg_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON received: {e}")
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    async def client_handler(self, websocket):
        """Enhanced client handler with better error handling"""
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.debug("🔌 Client connection closed normally")
        except Exception as e:
            logger.error(f"❌ Client handler error: {e}")
        finally:
            await self.unregister(websocket)
    
    async def periodic_stats(self):
        """Periodic stats logging"""
        while True:
            await asyncio.sleep(30)  # Every 30 seconds
            if self.screen_frames_received > 0:
                logger.info(f"📊 Stats: {self.screen_frames_received} frames, "
                           f"{round(self.total_data_received / (1024 * 1024), 2)} MB processed, "
                           f"{len(self.clients)} clients connected")
    
    async def start(self):
        """Start the enhanced daemon"""
        logger.info(f"🧬 Starting Enhanced Cognitive OS Daemon on port {self.port}")
        logger.info(f"🎯 Ready for screen frame processing and AI integration")
        
        # Start periodic stats
        stats_task = asyncio.create_task(self.periodic_stats())
        
        try:
            async with websockets.serve(self.client_handler, "localhost", self.port):
                logger.info(f"✅ Enhanced Cognitive Daemon listening on ws://localhost:{self.port}/ws")
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"❌ Daemon startup failed: {e}")
            stats_task.cancel()

async def main():
    daemon = EnhancedCognitiveDaemon(port=8084)
    await daemon.start()

if __name__ == "__main__":
    print("🧬 Enhanced Cognitive OS Daemon v0.4")
    print("=" * 50)
    asyncio.run(main())