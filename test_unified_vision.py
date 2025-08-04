#!/usr/bin/env python3
"""
Test the unified vision server with synthetic frames
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime, UTC
from PIL import Image, ImageDraw
import io
import numpy as np


async def send_test_frames():
    """Send synthetic frames to unified vision server"""
    
    uri = "ws://localhost:8766"
    
    async with websockets.connect(uri) as websocket:
        # Get handshake
        handshake = await websocket.recv()
        print(f"Connected: {json.loads(handshake)['server']}")
        
        # Create and send a few different UI types
        ui_types = [
            ("terminal", (20, 20, 20), "Dark terminal with green text"),
            ("browser", (240, 240, 240), "Light browser window"),
            ("ide", (30, 30, 40), "Dark IDE with code"),
            ("dashboard", (25, 25, 35), "Monitoring dashboard")
        ]
        
        for i, (ui_type, bg_color, desc) in enumerate(ui_types):
            print(f"\n📸 Sending {ui_type} frame...")
            
            # Create image
            img = Image.new('RGB', (800, 600), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Add some UI elements based on type
            if ui_type == "terminal":
                # Draw terminal lines
                y = 20
                for j in range(10):
                    draw.text((10, y), f"$ command_{j} --verbose", fill=(0, 255, 0))
                    y += 25
                    
            elif ui_type == "browser":
                # Draw browser header
                draw.rectangle([0, 0, 800, 60], fill=(70, 130, 180))
                draw.text((20, 20), "https://example.com - Browser", fill='white')
                # Content area
                draw.rectangle([50, 100, 750, 500], fill='white')
                
            elif ui_type == "ide":
                # Draw code editor look
                draw.rectangle([0, 0, 60, 600], fill=(40, 40, 50))  # Line numbers
                draw.text((10, 100), "1", fill=(100, 100, 100))
                draw.text((10, 120), "2", fill=(100, 100, 100))
                draw.text((70, 100), "def process_frame(self, data):", fill=(150, 200, 255))
                draw.text((70, 120), "    # Analyze frame", fill=(100, 150, 100))
                
            elif ui_type == "dashboard":
                # Draw panels
                draw.rectangle([10, 10, 390, 290], outline=(0, 150, 255), width=2)
                draw.rectangle([410, 10, 790, 290], outline=(255, 150, 0), width=2)
                draw.text((20, 20), "System Metrics", fill=(0, 200, 255))
                draw.text((420, 20), "Live Feed", fill=(255, 200, 0))
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Send frame
            frame_msg = {
                'type': 'screen_frame',
                'data': base64_data,
                'width': 800,
                'height': 600,
                'timestamp': datetime.now(UTC).isoformat()
            }
            
            await websocket.send(json.dumps(frame_msg))
            
            # Get analysis response
            response = await websocket.recv()
            analysis = json.loads(response)
            
            if analysis['type'] == 'frame_processed':
                result = analysis['analysis']
                print(f"✅ Analysis received:")
                print(f"   Detected: {result['detected_ui_type']}")
                print(f"   Brightness: {result['brightness']}")
                print(f"   Confidence: {result['confidence']}")
                print(f"   Insights: {result['insights']}")
            
            await asyncio.sleep(2)
        
        print("\n✅ Test complete!")


async def test_vision_tools():
    """Test the vision tools after frames are available"""
    await asyncio.sleep(1)  # Let frames process
    
    print("\n🔧 Testing Vision Tools:")
    print("-" * 50)
    
    # Import here to avoid connection issues
    from vision_tools import see, describe, watch, is_terminal, is_dark_mode
    
    # Test see()
    print("\n1. Testing see():")
    result = await see()
    print(f"   UI Type: {result.get('ui_type')}")
    print(f"   Description: {result.get('description')}")
    
    # Test describe()
    print("\n2. Testing describe():")
    desc = await describe()
    print(f"   {desc}")
    
    # Test specific checks
    print("\n3. Testing specific checks:")
    print(f"   Is terminal? {await is_terminal()}")
    print(f"   Is dark mode? {await is_dark_mode()}")
    
    # Test watch()
    print("\n4. Testing watch (3 seconds):")
    changes = await watch(3)
    for change in changes:
        print(f"   {change}")


async def main():
    print("🧬 Testing Unified Vision Server")
    print("=" * 50)
    
    # Start frame sender
    frame_task = asyncio.create_task(send_test_frames())
    
    # Start tool tester in parallel
    tools_task = asyncio.create_task(test_vision_tools())
    
    # Wait for both
    await frame_task
    await tools_task


if __name__ == "__main__":
    asyncio.run(main())