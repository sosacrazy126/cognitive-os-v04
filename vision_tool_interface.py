#!/usr/bin/env python3
"""
Vision Tool Interface - Minimal tool-calling interface for CLI agents
Provides structured access to vision stream and system control
"""

import asyncio
import json
import websockets
from typing import Dict, Any, List, Optional, Callable
import subprocess
import os
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
import io
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Structured tool call format"""
    tool: str
    action: str
    parameters: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class ToolResult:
    """Structured tool result format"""
    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class VisionToolInterface:
    """Minimal interface for CLI agents to interact with vision and system"""
    
    def __init__(self, vision_ws_url: str = "ws://localhost:8765"):
        self.vision_ws_url = vision_ws_url
        self.current_frame = None
        self.vision_connection = None
        self.tools = {
            'vision': self._vision_tools(),
            'system': self._system_tools(),
            'terminal': self._terminal_tools()
        }
        
    def _vision_tools(self) -> Dict[str, Callable]:
        """Vision-related tools"""
        return {
            'get_frame': self.get_current_frame,
            'analyze_frame': self.analyze_frame,
            'start_stream': self.start_vision_stream,
            'stop_stream': self.stop_vision_stream,
            'capture_region': self.capture_region
        }
    
    def _system_tools(self) -> Dict[str, Callable]:
        """System control tools"""
        return {
            'execute': self.execute_command,
            'read_file': self.read_file,
            'write_file': self.write_file,
            'list_directory': self.list_directory
        }
    
    def _terminal_tools(self) -> Dict[str, Callable]:
        """Terminal interaction tools"""
        return {
            'spawn': self.spawn_terminal,
            'send_keys': self.send_terminal_keys,
            'read_output': self.read_terminal_output
        }
    
    async def connect_vision(self):
        """Connect to vision stream WebSocket"""
        try:
            self.vision_connection = await websockets.connect(self.vision_ws_url)
            logger.info(f"Connected to vision stream at {self.vision_ws_url}")
            
            # Start frame receiver
            asyncio.create_task(self._receive_frames())
            return ToolResult(success=True, data="Connected to vision stream")
        except Exception as e:
            logger.error(f"Vision connection error: {e}")
            return ToolResult(success=False, error=str(e))
    
    async def _receive_frames(self):
        """Continuously receive frames from vision stream"""
        try:
            async for message in self.vision_connection:
                self.current_frame = json.loads(message)
        except Exception as e:
            logger.error(f"Frame receiver error: {e}")
            self.vision_connection = None
    
    async def get_current_frame(self, **params) -> ToolResult:
        """Get the current vision frame"""
        if not self.current_frame:
            return ToolResult(success=False, error="No frame available")
        
        # Option to exclude base64 data for lighter response
        if params.get('metadata_only', False):
            frame_data = {k: v for k, v in self.current_frame.items() if k != 'frame'}
        else:
            frame_data = self.current_frame
            
        return ToolResult(success=True, data=frame_data)
    
    async def analyze_frame(self, **params) -> ToolResult:
        """Analyze current frame with specified analysis type"""
        if not self.current_frame:
            return ToolResult(success=False, error="No frame available")
        
        analysis_type = params.get('type', 'basic')
        
        try:
            if analysis_type == 'basic':
                # Return existing analysis if available
                return ToolResult(
                    success=True, 
                    data=self.current_frame.get('analysis', {})
                )
            
            elif analysis_type == 'ocr':
                # Placeholder for OCR integration
                return ToolResult(
                    success=True,
                    data={'text_regions': [], 'text': ''}
                )
            
            elif analysis_type == 'objects':
                # Placeholder for object detection
                return ToolResult(
                    success=True,
                    data={'objects': [], 'count': 0}
                )
            
            else:
                return ToolResult(success=False, error=f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def capture_region(self, **params) -> ToolResult:
        """Capture specific screen region"""
        x = params.get('x', 0)
        y = params.get('y', 0)
        width = params.get('width', 100)
        height = params.get('height', 100)
        
        try:
            import mss
            with mss.mss() as sct:
                monitor = {"top": y, "left": x, "width": width, "height": height}
                screenshot = sct.grab(monitor)
                
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                
                return ToolResult(
                    success=True,
                    data={
                        'region': monitor,
                        'image': base64.b64encode(buffer.getvalue()).decode('utf-8')
                    }
                )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def execute_command(self, **params) -> ToolResult:
        """Execute system command"""
        command = params.get('command')
        if not command:
            return ToolResult(success=False, error="No command specified")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=params.get('timeout', 30)
            )
            
            return ToolResult(
                success=result.returncode == 0,
                data={
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Command timeout")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def read_file(self, **params) -> ToolResult:
        """Read file contents"""
        path = params.get('path')
        if not path:
            return ToolResult(success=False, error="No path specified")
        
        try:
            with open(path, 'r') as f:
                content = f.read(params.get('max_bytes', 1024*1024))  # 1MB default limit
            return ToolResult(success=True, data={'content': content, 'path': path})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def write_file(self, **params) -> ToolResult:
        """Write file contents"""
        path = params.get('path')
        content = params.get('content')
        
        if not path or content is None:
            return ToolResult(success=False, error="Path and content required")
        
        try:
            mode = 'a' if params.get('append', False) else 'w'
            with open(path, mode) as f:
                f.write(content)
            return ToolResult(success=True, data={'path': path, 'bytes_written': len(content)})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def list_directory(self, **params) -> ToolResult:
        """List directory contents"""
        path = params.get('path', '.')
        
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                items.append({
                    'name': item,
                    'type': 'directory' if os.path.isdir(item_path) else 'file',
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else None
                })
            return ToolResult(success=True, data={'path': path, 'items': items})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def spawn_terminal(self, **params) -> ToolResult:
        """Spawn a new terminal"""
        terminal = params.get('terminal', 'xterm')
        
        try:
            # Simple terminal spawn
            subprocess.Popen([terminal])
            return ToolResult(success=True, data={'terminal': terminal})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def send_terminal_keys(self, **params) -> ToolResult:
        """Send keys to terminal (requires xdotool)"""
        keys = params.get('keys')
        if not keys:
            return ToolResult(success=False, error="No keys specified")
        
        try:
            result = subprocess.run(['xdotool', 'type', keys], capture_output=True)
            return ToolResult(success=result.returncode == 0, data={'keys': keys})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def read_terminal_output(self, **params) -> ToolResult:
        """Read terminal output (placeholder for real implementation)"""
        return ToolResult(
            success=True, 
            data={'output': 'Terminal output reading requires specific terminal integration'}
        )
    
    async def start_vision_stream(self, **params) -> ToolResult:
        """Start vision streaming"""
        if not self.vision_connection:
            return await self.connect_vision()
        return ToolResult(success=True, data="Vision stream already connected")
    
    async def stop_vision_stream(self, **params) -> ToolResult:
        """Stop vision streaming"""
        if self.vision_connection:
            await self.vision_connection.close()
            self.vision_connection = None
            return ToolResult(success=True, data="Vision stream disconnected")
        return ToolResult(success=True, data="Vision stream not connected")
    
    async def call_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call"""
        try:
            category = self.tools.get(tool_call.tool)
            if not category:
                return ToolResult(success=False, error=f"Unknown tool category: {tool_call.tool}")
            
            action = category.get(tool_call.action)
            if not action:
                return ToolResult(success=False, error=f"Unknown action: {tool_call.action}")
            
            # Execute the tool
            result = await action(**tool_call.parameters)
            return result
            
        except Exception as e:
            logger.error(f"Tool call error: {e}")
            return ToolResult(success=False, error=str(e))
    
    async def batch_call(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute multiple tool calls"""
        results = []
        for call in tool_calls:
            result = await self.call_tool(call)
            results.append(result)
        return results


# CLI Agent Interface
class CLIAgent:
    """Simple CLI agent with vision and tool capabilities"""
    
    def __init__(self, name: str = "vision_agent"):
        self.name = name
        self.interface = VisionToolInterface()
        self.running = False
        
    async def initialize(self):
        """Initialize agent and connect to vision"""
        logger.info(f"Initializing {self.name}...")
        result = await self.interface.connect_vision()
        return result.success
        
    async def perceive(self) -> Dict[str, Any]:
        """Get current perception from vision"""
        frame_result = await self.interface.call_tool(
            ToolCall(tool='vision', action='get_frame', parameters={'metadata_only': True})
        )
        
        if frame_result.success:
            analysis_result = await self.interface.call_tool(
                ToolCall(tool='vision', action='analyze_frame', parameters={'type': 'basic'})
            )
            
            return {
                'frame': frame_result.data,
                'analysis': analysis_result.data if analysis_result.success else {}
            }
        return {}
    
    async def act(self, action: str, **params) -> ToolResult:
        """Execute an action through tools"""
        # Parse action format: "category.action"
        parts = action.split('.')
        if len(parts) != 2:
            return ToolResult(success=False, error="Invalid action format. Use: category.action")
        
        tool_call = ToolCall(tool=parts[0], action=parts[1], parameters=params)
        return await self.interface.call_tool(tool_call)
    
    async def think_act_loop(self):
        """Simple perception-action loop"""
        self.running = True
        
        while self.running:
            try:
                # Perceive
                perception = await self.perceive()
                
                # Decide (placeholder for AI integration)
                if perception.get('analysis', {}).get('is_dark', False):
                    # Example: If screen is dark, list current directory
                    await self.act('system.list_directory', path='.')
                
                # Wait before next cycle
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Agent loop error: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop the agent"""
        self.running = False


async def example_usage():
    """Example of using the CLI agent"""
    agent = CLIAgent(name="example_agent")
    
    if await agent.initialize():
        # Example tool calls
        result = await agent.act('vision.get_frame', metadata_only=True)
        print(f"Current frame: {result.data}")
        
        result = await agent.act('system.execute', command='date')
        print(f"System time: {result.data}")
        
        # Start perception-action loop
        try:
            await agent.think_act_loop()
        except KeyboardInterrupt:
            agent.stop()
            await agent.interface.stop_vision_stream()


if __name__ == "__main__":
    asyncio.run(example_usage())