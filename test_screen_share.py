#!/usr/bin/env python3
"""
Test script to simulate browser screen sharing
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime
import mss
from PIL import Image
import io

async def test_screen_share():
    """Simulate browser sending screen frames"""
    
    # Connect to bridge as if we're the browser
    uri = "ws://localhost:8084"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to bridge at {uri}")
            
            # Send test message
            test_msg = {
                'type': 'test',
                'message': 'Test from simulated browser',
                'timestamp': datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(test_msg))
            print("📤 Sent test message")
            
            # Capture and send a few screen frames
            with mss.mss() as sct:
                monitor = sct.monitors[0]  # Primary monitor
                
                for i in range(5):
                    print(f"\n📸 Capturing frame {i+1}...")
                    
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    
                    # Convert to PIL Image
                    img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                    
                    # Resize for faster transmission
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    
                    # Convert to JPEG
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=70)
                    
                    # Encode to base64
                    base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    # Create frame message
                    frame_msg = {
                        'type': 'screen_frame',
                        'data': base64_data,
                        'width': img.width,
                        'height': img.height,
                        'timestamp': datetime.utcnow().isoformat(),
                        'frameNumber': i
                    }
                    
                    # Send frame
                    await websocket.send(json.dumps(frame_msg))
                    print(f"📤 Sent frame {i+1} ({img.width}x{img.height})")
                    
                    # Wait for acknowledgment
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2)
                        ack = json.loads(response)
                        print(f"📥 Received: {ack.get('type')} - Frame ID: {ack.get('frame_id')}")
                    except asyncio.TimeoutError:
                        print("⚠️  No acknowledgment received")
                    
                    # Wait before next frame
                    await asyncio.sleep(1)
            
            print("\n✅ Test completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def check_analysis_output():
    """Check vision analysis output"""
    await asyncio.sleep(1)  # Give it time to process
    
    try:
        with open('vision.log', 'r') as f:
            print("\n📊 Vision Analysis Output:")
            print("-" * 60)
            print(f.read())
    except:
        pass

async def main():
    """Run the test"""
    print("🧬 Testing Cognitive OS Screen Share Pipeline")
    print("=" * 60)
    
    # Run screen share test
    await test_screen_share()
    
    # Check analysis
    await check_analysis_output()

if __name__ == "__main__":
    asyncio.run(main())