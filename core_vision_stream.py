#!/usr/bin/env python3
"""
Core Vision Stream - Minimal real-time screen capture for CLI agents
Stripped down to essentials, no browser dependencies
"""

import asyncio
import base64
import json
import mss
import numpy as np
from PIL import Image
import websockets
import io
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisionStream:
    """Core vision capture and streaming without browser dependencies"""
    
    def __init__(self, fps: int = 5, quality: int = 85):
        self.fps = fps
        self.quality = quality
        self.frame_interval = 1.0 / fps
        self.is_running = False
        self.current_frame = None
        self.frame_processors = []
        self.websocket_server = None
        self.connected_clients = set()
        
    async def capture_screen(self) -> Optional[Dict[str, Any]]:
        """Capture screen using mss (no browser needed)"""
        try:
            # Check if display is available
            import os
            if not os.environ.get('DISPLAY'):
                # Mock frame for headless testing
                return self._create_mock_frame()
                
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                
                # Resize for performance (optional)
                max_width = 1280
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=self.quality)
                frame_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Create frame data
                frame_data = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'frame': frame_base64,
                    'width': img.width,
                    'height': img.height,
                    'format': 'jpeg',
                    'fps': self.fps
                }
                
                self.current_frame = frame_data
                return frame_data
                
        except Exception as e:
            logger.error(f"Screen capture error: {e}")
            # Fall back to mock frame on any capture error
            return self._create_mock_frame()
    
    def _create_mock_frame(self) -> Dict[str, Any]:
        """Create a mock frame for testing in headless environments"""
        # Generate a simple test pattern
        width, height = 640, 480
        img = Image.new('RGB', (width, height), color='blue')
        
        # Add some visual elements for testing
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 200, 150], fill='red')
        draw.rectangle([300, 200, 450, 300], fill='green')
        draw.text((250, 100), "MOCK FRAME", fill='white')
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=self.quality)
        frame_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'frame': frame_base64,
            'width': width,
            'height': height,
            'format': 'jpeg',
            'fps': self.fps,
            'mock': True
        }
    
    async def process_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply registered processors to frame"""
        processed_data = frame_data.copy()
        
        for processor in self.frame_processors:
            try:
                result = await processor(frame_data)
                if result:
                    processed_data.update(result)
            except Exception as e:
                logger.error(f"Frame processor error: {e}")
                
        return processed_data
    
    def add_processor(self, processor: Callable):
        """Add a frame processor function"""
        self.frame_processors.append(processor)
        
    async def stream_loop(self):
        """Main capture and stream loop"""
        self.is_running = True
        
        while self.is_running:
            try:
                # Capture frame
                frame_data = await self.capture_screen()
                if not frame_data:
                    continue
                
                # Process frame
                processed_data = await self.process_frame(frame_data)
                
                # Broadcast to connected clients
                if self.connected_clients:
                    message = json.dumps(processed_data)
                    disconnected = set()
                    
                    for client in self.connected_clients:
                        try:
                            await client.send(message)
                        except:
                            disconnected.add(client)
                    
                    self.connected_clients -= disconnected
                
                # Maintain FPS
                await asyncio.sleep(self.frame_interval)
                
            except Exception as e:
                logger.error(f"Stream loop error: {e}")
                await asyncio.sleep(1)
    
    async def handle_client(self, websocket):
        """Handle WebSocket client connections"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            # Send current frame immediately
            if self.current_frame:
                await websocket.send(json.dumps(self.current_frame))
            
            # Keep connection alive
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def start_server(self, host: str = 'localhost', port: int = 8765):
        """Start WebSocket server"""
        self.websocket_server = await websockets.serve(
            self.handle_client, host, port
        )
        logger.info(f"Vision stream server started on ws://{host}:{port}")
        
        # Start capture loop
        capture_task = asyncio.create_task(self.stream_loop())
        
        # Keep server running
        await asyncio.Future()  # Run forever
        
    def stop(self):
        """Stop the vision stream"""
        self.is_running = False
        if self.websocket_server:
            self.websocket_server.close()


# Example frame processors
async def brightness_analyzer(frame_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze frame brightness"""
    try:
        # Decode frame
        img_data = base64.b64decode(frame_data['frame'])
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to grayscale and calculate mean brightness
        gray = img.convert('L')
        brightness = np.mean(np.array(gray)) / 255.0
        
        return {
            'analysis': {
                'brightness': round(brightness, 3),
                'is_dark': brightness < 0.3,
                'is_bright': brightness > 0.7
            }
        }
    except Exception as e:
        logger.error(f"Brightness analysis error: {e}")
        return {}


async def edge_detector(frame_data: Dict[str, Any]) -> Dict[str, Any]:
    """Detect significant changes in frame"""
    try:
        # Simple edge detection placeholder
        return {
            'analysis': {
                'has_significant_change': False,
                'change_regions': []
            }
        }
    except Exception as e:
        logger.error(f"Edge detection error: {e}")
        return {}


# CLI Interface
def create_vision_stream(fps: int = 5, quality: int = 85) -> VisionStream:
    """Factory function for CLI usage"""
    stream = VisionStream(fps=fps, quality=quality)
    
    # Add default processors
    stream.add_processor(brightness_analyzer)
    stream.add_processor(edge_detector)
    
    return stream


async def main():
    """Example usage"""
    stream = create_vision_stream(fps=5, quality=85)
    
    try:
        await stream.start_server(host='localhost', port=8765)
    except KeyboardInterrupt:
        logger.info("Shutting down vision stream...")
        stream.stop()


if __name__ == "__main__":
    asyncio.run(main())