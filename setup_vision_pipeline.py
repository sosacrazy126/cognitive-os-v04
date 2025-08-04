#!/usr/bin/env python3
"""
One-time setup script for Vision Pipeline
Configures environment and dependencies for real-time vision streaming
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import platform

def check_python_version():
    """Ensure Python 3.8+"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]}")

def install_dependencies():
    """Install required packages"""
    packages = [
        'websockets',
        'mss',        # Screen capture without browser
        'pillow',     # Image processing
        'numpy',      # Numerical operations
        'aiofiles',   # Async file operations
    ]
    
    print("\nInstalling dependencies...")
    for package in packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    return True

def check_system_tools():
    """Check for optional system tools"""
    tools = {
        'xdotool': 'Terminal automation (optional)',
        'xterm': 'Terminal emulator (optional)',
        'gnome-terminal': 'GNOME terminal (optional)'
    }
    
    print("\nChecking system tools...")
    available = {}
    for tool, desc in tools.items():
        result = subprocess.run(['which', tool], capture_output=True)
        available[tool] = result.returncode == 0
        status = "✓" if available[tool] else "✗"
        print(f"{status} {tool}: {desc}")
    
    return available

def create_config():
    """Create configuration file"""
    config_path = Path('vision_config.json')
    
    config = {
        "vision": {
            "fps": 5,
            "quality": 85,
            "max_width": 1280,
            "websocket_port": 8765
        },
        "tools": {
            "terminal": "xterm",  # Default terminal
            "file_size_limit": 1048576,  # 1MB
            "command_timeout": 30
        },
        "gemini": {
            "api_key": "",  # User needs to add this
            "api_endpoint": "https://generativelanguage.googleapis.com/v1beta",
            "model": "gemini-pro-vision"
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✓ Created {config_path}")
    print("  Edit this file to customize settings")
    return config_path

def create_launcher():
    """Create simple launcher script"""
    launcher_content = '''#!/usr/bin/env python3
"""Vision Pipeline Launcher"""

import asyncio
import sys
from core_vision_stream import create_vision_stream
from vision_tool_interface import CLIAgent
import json

async def main():
    # Load config
    with open('vision_config.json', 'r') as f:
        config = json.load(f)
    
    # Start vision stream
    print("Starting vision stream...")
    stream = create_vision_stream(
        fps=config['vision']['fps'],
        quality=config['vision']['quality']
    )
    
    # Start stream server
    stream_task = asyncio.create_task(
        stream.start_server(port=config['vision']['websocket_port'])
    )
    
    # Wait a moment for server to start
    await asyncio.sleep(1)
    
    # Start CLI agent
    print("Starting CLI agent...")
    agent = CLIAgent(name="vision_cli_agent")
    
    if await agent.initialize():
        print("✓ Agent initialized")
        print(f"Vision stream: ws://localhost:{config['vision']['websocket_port']}")
        print("Press Ctrl+C to stop")
        
        try:
            await agent.think_act_loop()
        except KeyboardInterrupt:
            print("\\nShutting down...")
            agent.stop()
            stream.stop()
    else:
        print("✗ Failed to initialize agent")
        stream.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nShutdown complete")
'''
    
    launcher_path = Path('launch_vision.py')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    # Make executable
    os.chmod(launcher_path, 0o755)
    
    print(f"✓ Created {launcher_path}")
    return launcher_path

def create_gemini_integration():
    """Create Gemini Live API integration module"""
    gemini_content = '''#!/usr/bin/env python3
"""
Gemini Live API Integration for Real-time Vision
Prepared for future integration with Google's Multimodal Live API
"""

import asyncio
import json
import base64
from typing import Dict, Any, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)


class GeminiVisionProcessor:
    """Process vision frames using Gemini Live API"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro-vision"):
        self.api_key = api_key
        self.model = model
        self.api_endpoint = "https://generativelanguage.googleapis.com/v1beta"
        self.session = None
        
    async def initialize(self):
        """Initialize API session"""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
    async def process_frame(self, frame_data: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Process a single frame with Gemini"""
        if not self.session:
            await self.initialize()
            
        try:
            # Prepare request
            request_data = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": frame_data['frame']  # Base64 encoded
                            }
                        }
                    ]
                }]
            }
            
            # Send to Gemini
            async with self.session.post(
                f"{self.api_endpoint}/models/{self.model}:generateContent",
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "analysis": result['candidates'][0]['content']['parts'][0]['text']
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Gemini processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close API session"""
        if self.session:
            await self.session.close()


class GeminiLiveStream:
    """Future implementation for Gemini Multimodal Live API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Placeholder for WebRTC/WebSocket streaming
        
    async def start_stream(self):
        """Start live video stream to Gemini"""
        # TODO: Implement when API becomes available
        # Will use WebRTC for low-latency streaming
        pass
        
    async def process_stream(self, video_source: str):
        """Process continuous video stream"""
        # TODO: Implement real-time processing
        pass


# Integration with Vision Pipeline
async def enhance_with_gemini(vision_interface, api_key: str):
    """Enhance vision interface with Gemini capabilities"""
    processor = GeminiVisionProcessor(api_key)
    await processor.initialize()
    
    # Add Gemini processor to vision tools
    async def gemini_analyze(**params):
        frame_result = await vision_interface.get_current_frame()
        if not frame_result.success:
            return frame_result
            
        prompt = params.get('prompt', 'Describe what you see in this image')
        result = await processor.process_frame(frame_result.data, prompt)
        
        return {
            "success": result.get("success", False),
            "data": result.get("analysis", ""),
            "error": result.get("error")
        }
    
    # Register new tool
    vision_interface.tools['vision']['gemini_analyze'] = gemini_analyze
    
    return processor


# Example usage
async def example_gemini_integration():
    """Example of using Gemini with vision pipeline"""
    from vision_tool_interface import VisionToolInterface
    
    # Load config
    with open('vision_config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['gemini']['api_key']
    if not api_key:
        print("Please add your Gemini API key to vision_config.json")
        return
        
    # Create interface and enhance with Gemini
    interface = VisionToolInterface()
    await interface.connect_vision()
    
    processor = await enhance_with_gemini(interface, api_key)
    
    try:
        # Analyze current screen
        result = await interface.call_tool({
            'tool': 'vision',
            'action': 'gemini_analyze',
            'parameters': {'prompt': 'What application is visible on the screen?'}
        })
        
        print(f"Gemini Analysis: {result}")
        
    finally:
        await processor.close()


if __name__ == "__main__":
    asyncio.run(example_gemini_integration())
'''
    
    gemini_path = Path('gemini_vision_integration.py')
    with open(gemini_path, 'w') as f:
        f.write(gemini_content)
    
    print(f"✓ Created {gemini_path}")
    return gemini_path

def main():
    """Run setup process"""
    print("Vision Pipeline Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        print("\nSetup failed: Could not install dependencies")
        sys.exit(1)
    
    # Check system tools
    tools = check_system_tools()
    
    # Create configuration
    config_path = create_config()
    
    # Create launcher
    launcher_path = create_launcher()
    
    # Create Gemini integration
    gemini_path = create_gemini_integration()
    
    print("\n" + "=" * 40)
    print("Setup Complete!")
    print("\nNext steps:")
    print("1. Edit vision_config.json to add your Gemini API key (optional)")
    print("2. Run: python launch_vision.py")
    print("3. Connect your CLI agent to ws://localhost:8765")
    print("\nCore modules:")
    print("- core_vision_stream.py: Screen capture without browser")
    print("- vision_tool_interface.py: Tool-calling interface")
    print("- gemini_vision_integration.py: AI vision processing")
    
    if not tools.get('xdotool'):
        print("\nNote: Install xdotool for terminal automation features")

if __name__ == "__main__":
    main()