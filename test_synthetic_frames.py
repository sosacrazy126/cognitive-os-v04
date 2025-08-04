#!/usr/bin/env python3
"""
Test screen sharing pipeline with synthetic frames
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime, UTC
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

def create_synthetic_frame(frame_num, text=""):
    """Create a synthetic test frame"""
    # Create image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Draw different patterns based on frame number
    if frame_num % 3 == 0:
        # Terminal-like dark screen
        img = Image.new('RGB', (width, height), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        # Draw some text
        y = 20
        for i in range(10):
            draw.text((10, y), f"$ command_{i} --option value", fill=(0, 255, 0))
            y += 30
        content_type = "terminal"
    elif frame_num % 3 == 1:
        # Browser-like bright screen
        img = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        # Draw header
        draw.rectangle([0, 0, width, 60], fill=(50, 50, 200))
        draw.text((10, 20), "Browser Window - Cognitive OS Dashboard", fill='white')
        # Draw content area
        draw.rectangle([50, 100, width-50, height-50], fill='white', outline='gray')
        content_type = "browser"
    else:
        # Dashboard with mixed elements
        img = Image.new('RGB', (width, height), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)
        # Draw panels
        draw.rectangle([10, 10, width//2-5, height//2-5], fill=(0, 100, 200, 128), outline=(0, 200, 255))
        draw.rectangle([width//2+5, 10, width-10, height//2-5], fill=(200, 100, 0, 128), outline=(255, 200, 0))
        draw.text((20, 20), "Reasoning Chain", fill='white')
        draw.text((width//2+15, 20), "Insights", fill='white')
        content_type = "dashboard"
    
    # Add frame info
    draw.text((10, height-30), f"Frame {frame_num} - {text}", fill=(255, 255, 255))
    
    return img, content_type

async def test_pipeline():
    """Test the complete pipeline with synthetic frames"""
    
    uri = "ws://localhost:8084"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to Screen Share Bridge at {uri}")
            
            # Send test message first
            test_msg = {
                'type': 'test',
                'message': 'Synthetic frame test',
                'timestamp': datetime.now(UTC).isoformat()
            }
            await websocket.send(json.dumps(test_msg))
            print("📤 Sent test message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2)
                print(f"📥 Test response: {json.loads(response).get('message')}")
            except asyncio.TimeoutError:
                print("⚠️  No test response")
            
            # Send synthetic frames
            frame_types = ["terminal", "browser", "dashboard"]
            
            for i in range(6):
                print(f"\n🎨 Creating synthetic frame {i+1}...")
                
                # Create synthetic frame
                img, content_type = create_synthetic_frame(i, f"Type: {frame_types[i % 3]}")
                
                # Convert to JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=80)
                base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Create frame message
                frame_msg = {
                    'type': 'screen_frame',
                    'data': base64_data,
                    'width': img.width,
                    'height': img.height,
                    'timestamp': datetime.now(UTC).isoformat(),
                    'frameNumber': i
                }
                
                # Send frame
                await websocket.send(json.dumps(frame_msg))
                print(f"📤 Sent {content_type} frame ({img.width}x{img.height})")
                
                # Wait for acknowledgment
                try:
                    ack = await asyncio.wait_for(websocket.recv(), timeout=2)
                    ack_data = json.loads(ack)
                    print(f"📥 Acknowledged: Frame ID {ack_data.get('frame_id')}")
                except asyncio.TimeoutError:
                    print("⚠️  No acknowledgment")
                
                # Wait before next frame
                await asyncio.sleep(2)
            
            print("\n✅ Pipeline test completed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def check_logs():
    """Check bridge and vision logs"""
    await asyncio.sleep(1)
    
    print("\n📊 ANALYSIS RESULTS:")
    print("=" * 60)
    
    # Check vision log
    try:
        with open('vision.log', 'r') as f:
            content = f.read()
            if content:
                print("\n🔍 Vision Analysis Log:")
                print("-" * 60)
                # Show last 20 lines
                lines = content.strip().split('\n')
                for line in lines[-20:]:
                    print(line)
    except Exception as e:
        print(f"Could not read vision.log: {e}")
    
    # Check bridge log
    try:
        with open('bridge.log', 'r') as f:
            content = f.read()
            if content:
                print("\n🌉 Bridge Log:")
                print("-" * 60)
                # Show last 10 lines
                lines = content.strip().split('\n')[-10:]
                for line in lines:
                    print(line)
    except:
        pass

async def main():
    print("🧬 COGNITIVE OS SCREEN SHARE PIPELINE TEST")
    print("Testing with synthetic frames to simulate different screen types")
    print("=" * 60)
    
    await test_pipeline()
    await check_logs()

if __name__ == "__main__":
    asyncio.run(main())