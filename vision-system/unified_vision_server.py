#!/usr/bin/env python3
"""
Unified Vision Server - Simple, efficient real-time screen analysis
Single WebSocket server that handles both browser input and analysis output
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime, UTC
from typing import Dict, Any, Set, Optional
import logging
from PIL import Image
import io
import numpy as np
from dataclasses import dataclass, asdict, field
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FrameAnalysis:
    """Structured frame analysis result"""
    frame_id: int
    timestamp: str
    content_type: str
    brightness: float
    contrast: float
    dominant_color: str
    is_dark: bool
    is_bright: bool
    detected_ui_type: str
    confidence: float
    changes: list = field(default_factory=list)
    insights: list = field(default_factory=list)


class UnifiedVisionServer:
    """Single server handling both screen capture and analysis"""
    
    def __init__(self, port: int = 8766):
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.frame_count = 0
        self.last_frame_analysis: Optional[FrameAnalysis] = None
        self.analysis_cache = []
        self.max_cache = 10
        
    async def handle_client(self, websocket):
        """Handle all client connections - browser or analysis consumers"""
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"Client connected: {client_addr}")
        
        try:
            # Send initial handshake
            await websocket.send(json.dumps({
                'type': 'connected',
                'server': 'unified_vision_server',
                'version': '1.0',
                'timestamp': datetime.now(UTC).isoformat()
            }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')
                    
                    if message_type == 'screen_frame':
                        # Process incoming screen frame
                        analysis = await self.process_frame(data)
                        
                        # Send back acknowledgment with analysis
                        response = {
                            'type': 'frame_processed',
                            'frame_id': analysis.frame_id,
                            'analysis': asdict(analysis)
                        }
                        await websocket.send(json.dumps(response))
                        
                        # Broadcast analysis to all other clients
                        await self.broadcast_analysis(analysis, exclude=websocket)
                        
                    elif message_type == 'get_history':
                        # Send analysis history
                        await websocket.send(json.dumps({
                            'type': 'history',
                            'analyses': [asdict(a) for a in self.analysis_cache]
                        }))
                        
                    elif message_type == 'test':
                        # Echo test
                        await websocket.send(json.dumps({
                            'type': 'test_response',
                            'echo': data.get('message', ''),
                            'timestamp': datetime.now(UTC).isoformat()
                        }))
                        
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON'
                    }))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_addr}")
        finally:
            self.clients.remove(websocket)
    
    async def process_frame(self, frame_data: Dict[str, Any]) -> FrameAnalysis:
        """Process and analyze incoming frame"""
        self.frame_count += 1
        start_time = time.time()
        
        # Decode frame
        frame_base64 = frame_data.get('data', '')
        img_data = base64.b64decode(frame_base64)
        img = Image.open(io.BytesIO(img_data))
        img_array = np.array(img)
        
        # Basic visual analysis
        brightness = np.mean(img_array) / 255.0
        contrast = np.std(img_array) / 255.0
        
        # Color analysis
        avg_color = np.mean(img_array.reshape(-1, 3), axis=0)
        dominant_color = self._describe_color(avg_color)
        
        # UI type detection
        ui_type = self._detect_ui_type(img_array, brightness, contrast)
        
        # Change detection
        changes = self._detect_changes(brightness, contrast, ui_type)
        
        # Generate insights
        insights = self._generate_insights(brightness, contrast, ui_type, changes)
        
        # Calculate confidence based on processing time and clarity
        process_time = time.time() - start_time
        confidence = min(0.95, 0.8 + (0.2 * contrast) - (process_time * 0.1))
        
        analysis = FrameAnalysis(
            frame_id=self.frame_count,
            timestamp=datetime.now(UTC).isoformat(),
            content_type=ui_type,
            brightness=round(brightness, 3),
            contrast=round(contrast, 3),
            dominant_color=dominant_color,
            is_dark=brightness < 0.3,
            is_bright=brightness > 0.7,
            detected_ui_type=ui_type,
            confidence=round(confidence, 3),
            changes=changes,
            insights=insights
        )
        
        # Update cache
        self.last_frame_analysis = analysis
        self.analysis_cache.append(analysis)
        if len(self.analysis_cache) > self.max_cache:
            self.analysis_cache.pop(0)
        
        # Log analysis
        logger.info(f"Frame {self.frame_count}: {ui_type} (brightness: {brightness:.2f}, confidence: {confidence:.2f})")
        
        return analysis
    
    def _describe_color(self, rgb: np.ndarray) -> str:
        """Convert RGB to color description"""
        r, g, b = rgb
        
        if max(rgb) - min(rgb) < 30:
            if r > 200:
                return "white"
            elif r < 50:
                return "black"
            else:
                return "gray"
        elif r > g and r > b:
            return "red-toned"
        elif g > r and g > b:
            return "green-toned"
        elif b > r and b > g:
            return "blue-toned"
        else:
            return "mixed"
    
    def _detect_ui_type(self, img_array: np.ndarray, brightness: float, contrast: float) -> str:
        """Detect type of UI being displayed"""
        height, width = img_array.shape[:2]
        
        # Analyze top region
        top_region = img_array[:height//5]
        top_brightness = np.mean(top_region) / 255.0
        
        # Analyze color variance
        color_variance = np.std(img_array.reshape(-1, 3), axis=0)
        is_monochrome = np.max(color_variance) < 20
        
        # Decision tree for UI type
        if brightness < 0.2 and is_monochrome:
            return "terminal"
        elif brightness > 0.8 and contrast > 0.3:
            return "document"
        elif top_brightness < 0.3 and brightness > 0.5:
            return "ide"
        elif brightness > 0.6 and contrast < 0.2:
            return "browser"
        elif brightness < 0.3 and contrast > 0.4:
            return "dashboard"
        else:
            return "application"
    
    def _detect_changes(self, brightness: float, contrast: float, ui_type: str) -> list:
        """Detect changes from previous frame"""
        if not self.last_frame_analysis:
            return ["first_frame"]
        
        changes = []
        last = self.last_frame_analysis
        
        # Brightness change
        brightness_delta = abs(brightness - last.brightness)
        if brightness_delta > 0.1:
            direction = "increased" if brightness > last.brightness else "decreased"
            changes.append(f"brightness_{direction}_{brightness_delta:.2f}")
        
        # UI type change
        if ui_type != last.detected_ui_type:
            changes.append(f"ui_changed_from_{last.detected_ui_type}_to_{ui_type}")
        
        # Contrast change
        contrast_delta = abs(contrast - last.contrast)
        if contrast_delta > 0.1:
            changes.append(f"contrast_changed_{contrast_delta:.2f}")
        
        return changes if changes else ["stable"]
    
    def _generate_insights(self, brightness: float, contrast: float, ui_type: str, changes: list) -> list:
        """Generate actionable insights from analysis"""
        insights = []
        
        # UI-specific insights
        if ui_type == "terminal":
            insights.append("Terminal detected - monitor for commands")
            if brightness < 0.1:
                insights.append("Very dark terminal - possible vim/tmux session")
        
        elif ui_type == "browser":
            insights.append("Browser detected - web content active")
            if contrast < 0.1:
                insights.append("Low contrast - possible loading state")
        
        elif ui_type == "ide":
            insights.append("IDE detected - code editing session")
            if "ui_changed" in str(changes):
                insights.append("Context switch detected - new file or view")
        
        elif ui_type == "dashboard":
            insights.append("Dashboard detected - monitoring interface")
            if brightness < 0.2:
                insights.append("Dark theme dashboard - likely system monitoring")
        
        # Change-based insights
        if "brightness_increased" in str(changes):
            insights.append("Screen brightened - possible mode switch")
        elif "brightness_decreased" in str(changes):
            insights.append("Screen darkened - possible focus change")
        
        return insights
    
    async def broadcast_analysis(self, analysis: FrameAnalysis, exclude=None):
        """Broadcast analysis to all connected clients except sender"""
        message = json.dumps({
            'type': 'live_analysis',
            'analysis': asdict(analysis)
        })
        
        disconnected = set()
        for client in self.clients:
            if client != exclude:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)
        
        # Clean up disconnected clients
        self.clients -= disconnected
    
    async def start_server(self):
        """Start the unified vision server"""
        server = await websockets.serve(
            self.handle_client,
            'localhost',
            self.port
        )
        
        logger.info(f"🧬 Unified Vision Server running on ws://localhost:{self.port}")
        logger.info("Ready for browser connections and analysis consumers")
        
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            server.close()
            await server.wait_closed()


async def main():
    """Run the unified vision server"""
    server = UnifiedVisionServer()
    await server.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown complete")