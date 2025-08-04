#!/usr/bin/env python3
"""
Simple demo of the vision system for CLI agents
"""

import asyncio
from vision_tools import describe_sync, see_sync, watch_sync
import websockets
import json
import base64
from PIL import Image, ImageDraw
import io


async def send_demo_frame():
    """Send a single demo frame to show the system works"""
    uri = "ws://localhost:8766"
    
    async with websockets.connect(uri) as websocket:
        # Get handshake
        await websocket.recv()
        
        # Create a terminal-like frame
        img = Image.new('RGB', (800, 600), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        # Draw terminal content
        y = 30
        draw.text((20, y), "$ python demo_vision.py", fill=(0, 255, 0))
        y += 30
        draw.text((20, y), ">>> Testing vision system...", fill=(0, 255, 0))
        y += 30
        draw.text((20, y), ">>> Frame sent successfully", fill=(0, 255, 0))
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Send frame
        frame_msg = {
            'type': 'screen_frame',
            'data': base64_data,
            'width': 800,
            'height': 600
        }
        
        await websocket.send(json.dumps(frame_msg))
        
        # Get response
        response = await websocket.recv()
        data = json.loads(response)
        
        if data['type'] == 'frame_processed':
            print("✅ Frame processed successfully")
            print(f"   Detected: {data['analysis']['detected_ui_type']}")


async def main():
    print("🧬 VISION SYSTEM DEMO")
    print("=" * 50)
    
    # Send a test frame
    print("\n1. Sending test frame...")
    await send_demo_frame()
    
    # Wait a moment for processing
    await asyncio.sleep(0.5)
    
    # Now use vision tools
    print("\n2. Using vision tools to see what's on screen:")
    
    # Describe what we see
    description = describe_sync()
    print(f"   Description: {description}")
    
    # Get detailed info
    screen_info = see_sync()
    print(f"\n3. Detailed vision data:")
    print(f"   UI Type: {screen_info.get('ui_type')}")
    print(f"   Brightness: {screen_info.get('brightness')}")
    print(f"   Is Dark: {screen_info.get('is_dark')}")
    print(f"   Confidence: {screen_info.get('confidence')}")
    
    if screen_info.get('insights'):
        print(f"   Insights:")
        for insight in screen_info['insights']:
            print(f"     - {insight}")
    
    print("\n✅ Demo complete!")
    print("\nThis is how CLI agents like Claude Code can see and understand screen content.")
    print("The unified server provides real-time analysis of whatever is being displayed.")


if __name__ == "__main__":
    asyncio.run(main())