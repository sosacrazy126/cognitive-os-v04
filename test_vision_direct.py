#!/usr/bin/env python3
"""
Direct test of vision pipeline connection
"""

import asyncio
import websockets
import json

async def test_vision_connection():
    """Connect directly to vision server and monitor frames"""
    
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to vision server at {uri}")
            
            # Listen for frames
            print("🔍 Listening for frames...")
            
            frame_count = 0
            async for message in websocket:
                frame_count += 1
                data = json.loads(message)
                
                print(f"\n📸 FRAME {frame_count}:")
                print(f"  Timestamp: {data.get('timestamp')}")
                print(f"  Dimensions: {data.get('width')}x{data.get('height')}")
                print(f"  Source: {data.get('source')}")
                print(f"  Format: {data.get('format')}")
                print(f"  FPS: {data.get('fps')}")
                
                # Show analysis if present
                if 'analysis' in data:
                    analysis = data['analysis']
                    print(f"  Analysis:")
                    print(f"    - Brightness: {analysis.get('brightness')}")
                    print(f"    - Is Dark: {analysis.get('is_dark')}")
                    print(f"    - Is Bright: {analysis.get('is_bright')}")
                
                # Don't show the actual base64 data
                if 'frame' in data:
                    print(f"  Frame data: {len(data['frame'])} bytes (base64)")
                
                if frame_count >= 10:
                    print("\n✅ Received 10 frames, test complete!")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧬 Direct Vision Server Test")
    print("=" * 60)
    asyncio.run(test_vision_connection())