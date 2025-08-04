#!/usr/bin/env python3
"""
Screen Share Bridge - Connects browser screen sharing to vision pipeline
Receives frames from enhanced_screen_capture.html and feeds to vision system
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime
from typing import Dict, Any, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScreenShareBridge:
    """Bridge between browser screen sharing and vision pipeline"""
    
    def __init__(self, browser_port: int = 8084, vision_port: int = 8765):
        self.browser_port = browser_port
        self.vision_port = vision_port
        self.browser_clients: Set = set()
        self.vision_clients: Set = set()
        self.latest_frame = None
        self.frame_count = 0
        self.running = False
        
    async def handle_browser_client(self, websocket):
        """Handle connections from browser screen sharing dashboard"""
        self.browser_clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"Browser client connected: {client_addr}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get('type') == 'screen_frame':
                        # Convert browser frame to vision pipeline format
                        vision_frame = self._convert_browser_frame(data)
                        self.latest_frame = vision_frame
                        self.frame_count += 1
                        
                        # Broadcast to vision clients
                        await self._broadcast_to_vision(vision_frame)
                        
                        # Send acknowledgment back to browser
                        ack = {
                            'type': 'frame_ack',
                            'frame_id': self.frame_count,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        await websocket.send(json.dumps(ack))
                        
                    elif data.get('type') == 'test':
                        # Handle test messages
                        response = {
                            'type': 'test_response',
                            'message': 'Bridge operational',
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        await websocket.send(json.dumps(response))
                        logger.info(f"Test message from {client_addr}")
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from browser client {client_addr}")
                except Exception as e:
                    logger.error(f"Error processing browser message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Browser client disconnected: {client_addr}")
        finally:
            self.browser_clients.remove(websocket)
    
    async def handle_vision_client(self, websocket):
        """Handle connections from vision pipeline clients"""
        self.vision_clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"Vision client connected: {client_addr}")
        
        try:
            # Send latest frame immediately if available
            if self.latest_frame:
                await websocket.send(json.dumps(self.latest_frame))
                
            # Keep connection alive and handle any incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"Vision client message: {data.get('type', 'unknown')}")
                except:
                    pass  # Ignore malformed messages
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Vision client disconnected: {client_addr}")
        finally:
            self.vision_clients.remove(websocket)
    
    def _convert_browser_frame(self, browser_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert browser frame format to vision pipeline format"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'frame': browser_data['data'],  # Base64 JPEG data
            'width': browser_data.get('width', 1920),
            'height': browser_data.get('height', 1080),
            'format': 'jpeg',
            'fps': 5,  # Estimated based on browser capture
            'source': 'browser_screen_share',
            'analysis': {
                'brightness': 0.5,  # Placeholder - could add actual analysis
                'is_dark': False,
                'is_bright': False
            }
        }
    
    async def _broadcast_to_vision(self, frame_data: Dict[str, Any]):
        """Broadcast frame to all connected vision clients"""
        if not self.vision_clients:
            return
            
        message = json.dumps(frame_data)
        disconnected = set()
        
        for client in self.vision_clients:
            try:
                await client.send(message)
            except:
                disconnected.add(client)
        
        # Clean up disconnected clients
        self.vision_clients -= disconnected
    
    async def start_bridge(self):
        """Start both WebSocket servers"""
        self.running = True
        
        # Start browser-facing server (receives screen frames)
        browser_server = await websockets.serve(
            self.handle_browser_client,
            'localhost', 
            self.browser_port
        )
        logger.info(f"Browser server listening on ws://localhost:{self.browser_port}")
        
        # Start vision-facing server (provides frames to vision pipeline)
        vision_server = await websockets.serve(
            self.handle_vision_client,
            'localhost',
            self.vision_port
        )
        logger.info(f"Vision server listening on ws://localhost:{self.vision_port}")
        
        logger.info("🌉 Screen Share Bridge operational")
        logger.info("Browser → Bridge → Vision Pipeline")
        
        # Keep servers running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down bridge...")
            browser_server.close()
            vision_server.close()
            await browser_server.wait_closed()
            await vision_server.wait_closed()


async def main():
    """Main bridge execution"""
    bridge = ScreenShareBridge()
    await bridge.start_bridge()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBridge shutdown complete")