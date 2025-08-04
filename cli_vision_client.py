#!/usr/bin/env python3
"""
CLI Vision Client - Simple interface for CLI agents to consume screen vision
Connects to unified vision server and provides structured, actionable insights
"""

import asyncio
import websockets
import json
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VisionState:
    """Current vision state for CLI agent"""
    current_ui_type: str = "unknown"
    brightness: float = 0.5
    last_change: str = "none"
    active_insights: list = None
    confidence: float = 0.0
    frame_id: int = 0
    
    def __post_init__(self):
        if self.active_insights is None:
            self.active_insights = []


class CLIVisionClient:
    """Vision client optimized for CLI agents like Claude Code"""
    
    def __init__(self, server_url: str = "ws://localhost:8766"):
        self.server_url = server_url
        self.connection = None
        self.vision_state = VisionState()
        self.frame_handlers = {}
        self.running = False
        
    def on_terminal_detected(self, handler: Callable):
        """Register handler for when terminal is detected"""
        self.frame_handlers['terminal'] = handler
        return self
        
    def on_browser_detected(self, handler: Callable):
        """Register handler for when browser is detected"""
        self.frame_handlers['browser'] = handler
        return self
        
    def on_ide_detected(self, handler: Callable):
        """Register handler for when IDE is detected"""
        self.frame_handlers['ide'] = handler
        return self
        
    def on_change_detected(self, handler: Callable):
        """Register handler for any UI change"""
        self.frame_handlers['change'] = handler
        return self
    
    async def connect(self):
        """Connect to vision server"""
        try:
            self.connection = await websockets.connect(self.server_url)
            logger.info(f"Connected to vision server at {self.server_url}")
            
            # Wait for handshake
            handshake = await self.connection.recv()
            data = json.loads(handshake)
            logger.info(f"Server: {data.get('server')} v{data.get('version')}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def start_monitoring(self):
        """Start monitoring screen and processing insights"""
        if not self.connection:
            if not await self.connect():
                return
        
        self.running = True
        logger.info("👁️  Vision monitoring active")
        
        try:
            async for message in self.connection:
                if not self.running:
                    break
                    
                try:
                    data = json.loads(message)
                    
                    if data['type'] == 'live_analysis':
                        await self._process_analysis(data['analysis'])
                    elif data['type'] == 'frame_processed':
                        # We sent a frame and got analysis back
                        await self._process_analysis(data['analysis'])
                        
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Processing error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Vision server connection closed")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
    
    async def _process_analysis(self, analysis: Dict[str, Any]):
        """Process frame analysis and trigger appropriate handlers"""
        
        # Update vision state
        old_ui_type = self.vision_state.current_ui_type
        self.vision_state.current_ui_type = analysis['detected_ui_type']
        self.vision_state.brightness = analysis['brightness']
        self.vision_state.confidence = analysis['confidence']
        self.vision_state.frame_id = analysis['frame_id']
        self.vision_state.active_insights = analysis['insights']
        
        # Detect UI change
        if old_ui_type != "unknown" and old_ui_type != analysis['detected_ui_type']:
            self.vision_state.last_change = f"{old_ui_type} → {analysis['detected_ui_type']}"
            
            # Trigger change handler
            if 'change' in self.frame_handlers:
                await self._call_handler('change', self.vision_state)
        
        # Trigger UI-specific handlers
        ui_type = analysis['detected_ui_type']
        if ui_type in self.frame_handlers:
            await self._call_handler(ui_type, self.vision_state)
        
        # Log significant insights
        for insight in analysis['insights']:
            if any(keyword in insight.lower() for keyword in ['detected', 'changed', 'switch']):
                logger.info(f"🔍 {insight}")
    
    async def _call_handler(self, handler_type: str, state: VisionState):
        """Call registered handler safely"""
        handler = self.frame_handlers.get(handler_type)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(state)
                else:
                    handler(state)
            except Exception as e:
                logger.error(f"Handler error ({handler_type}): {e}")
    
    async def get_current_state(self) -> VisionState:
        """Get current vision state"""
        return self.vision_state
    
    async def request_history(self) -> Optional[list]:
        """Request analysis history from server"""
        if not self.connection:
            return None
            
        try:
            await self.connection.send(json.dumps({'type': 'get_history'}))
            response = await asyncio.wait_for(self.connection.recv(), timeout=2.0)
            data = json.loads(response)
            
            if data['type'] == 'history':
                return data['analyses']
                
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            
        return None
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Vision monitoring stopped")
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.connection:
            await self.connection.close()
            self.connection = None


# Example usage for CLI agents
async def example_cli_usage():
    """Example of how a CLI agent would use this"""
    
    # Create vision client
    vision = CLIVisionClient()
    
    # Define what to do when we see different UIs
    @vision.on_terminal_detected
    async def handle_terminal(state: VisionState):
        print(f"\n🖥️  Terminal detected! (confidence: {state.confidence:.1%})")
        print(f"   Brightness: {state.brightness:.2f}")
        for insight in state.active_insights:
            print(f"   → {insight}")
    
    @vision.on_browser_detected
    def handle_browser(state: VisionState):
        print(f"\n🌐 Browser detected! Frame #{state.frame_id}")
        if state.brightness > 0.7:
            print("   Light theme detected")
    
    @vision.on_ide_detected
    def handle_ide(state: VisionState):
        print(f"\n💻 IDE detected! Likely coding session")
    
    @vision.on_change_detected
    async def handle_change(state: VisionState):
        print(f"\n🔄 UI Changed: {state.last_change}")
    
    # Connect and start monitoring
    if await vision.connect():
        try:
            # Monitor for a while
            await vision.start_monitoring()
        except KeyboardInterrupt:
            vision.stop()
            await vision.disconnect()
            print("\n👋 Vision monitoring stopped")


# Direct CLI interface
class VisionCLI:
    """Direct CLI commands for vision interaction"""
    
    def __init__(self):
        self.client = CLIVisionClient()
    
    async def status(self):
        """Get current vision status"""
        state = await self.client.get_current_state()
        return {
            'connected': self.client.connection is not None,
            'current_ui': state.current_ui_type,
            'brightness': state.brightness,
            'last_change': state.last_change,
            'frame_id': state.frame_id,
            'confidence': state.confidence
        }
    
    async def watch(self, duration: int = 60):
        """Watch screen for specified duration"""
        if await self.client.connect():
            # Simple monitoring with console output
            @self.client.on_change_detected
            def log_change(state):
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {state.current_ui_type.upper()} - {state.active_insights[0] if state.active_insights else 'monitoring...'}")
            
            print(f"Watching screen for {duration} seconds...")
            
            # Start monitoring in background
            monitor_task = asyncio.create_task(self.client.start_monitoring())
            
            # Wait for duration
            await asyncio.sleep(duration)
            
            # Stop
            self.client.stop()
            await self.client.disconnect()
            
            return "Monitoring complete"
        
        return "Failed to connect"


if __name__ == "__main__":
    # Run example
    asyncio.run(example_cli_usage())