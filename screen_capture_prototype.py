"""
Screen Capture Prototype for tools.py v0.3 AI Integration
Testing different screen capture approaches and browser compatibility.
"""

import subprocess
import sys
import time
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

# Test dependencies availability
def check_dependencies() -> Dict[str, bool]:
    """Check which screen capture libraries are available"""
    deps = {
        'mss': False,
        'pyautogui': False, 
        'pillow': False,
        'opencv': False,
        'flask': False,
        'websockets': False
    }
    
    # Test mss (fastest cross-platform screenshots)
    try:
        import mss
        deps['mss'] = True
        print("✓ mss available - fast cross-platform screenshots")
    except ImportError:
        print("✗ mss not available - install with: pip install mss")
    
    # Test pyautogui (easy but slower)
    try:
        import pyautogui
        deps['pyautogui'] = True
        print("✓ pyautogui available - easy screenshot API")
    except ImportError:
        print("✗ pyautogui not available - install with: pip install pyautogui")
    
    # Test Pillow for image processing
    try:
        from PIL import Image
        deps['pillow'] = True
        print("✓ Pillow available - image processing")
    except ImportError:
        print("✗ Pillow not available - install with: pip install Pillow")
    
    # Test OpenCV for video processing
    try:
        import cv2
        deps['opencv'] = True
        print("✓ OpenCV available - video processing")
    except ImportError:
        print("✗ OpenCV not available - install with: pip install opencv-python")
    
    # Test Flask for web server
    try:
        import flask
        deps['flask'] = True
        print("✓ Flask available - web server")
    except ImportError:
        print("✗ Flask not available - install with: pip install flask")
    
    # Test websockets for real-time communication
    try:
        import websockets
        deps['websockets'] = True
        print("✓ websockets available - real-time communication")
    except ImportError:
        print("✗ websockets not available - install with: pip install websockets")
    
    return deps

def test_screen_capture_mss():
    """Test MSS library for fast screenshots"""
    try:
        import mss
        import time
        
        print("\n=== Testing MSS Screen Capture ===")
        
        with mss.mss() as sct:
            # Get monitor information
            monitors = sct.monitors
            print(f"Detected {len(monitors)-1} monitors:")
            
            for i, monitor in enumerate(monitors[1:], 1):
                print(f"  Monitor {i}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
            
            # Test screenshot speed
            monitor = monitors[1]  # Primary monitor
            start_time = time.time()
            
            for i in range(5):
                screenshot = sct.grab(monitor)
                # Convert to PIL Image for testing
                img = mss.tools.to_png(screenshot.rgb, screenshot.size)
                
            end_time = time.time()
            avg_time = (end_time - start_time) / 5
            fps = 1 / avg_time
            
            print(f"Average screenshot time: {avg_time:.3f}s ({fps:.1f} FPS)")
            print(f"Screenshot size: {screenshot.width}x{screenshot.height}")
            
            # Save a test screenshot
            output_path = "/home/evilbastardxd/test_screenshot.png"
            sct.shot(output=output_path)
            print(f"✓ Test screenshot saved to: {output_path}")
            
            return True
            
    except Exception as e:
        print(f"✗ MSS test failed: {e}")
        return False

def test_screen_capture_pyautogui():
    """Test PyAutoGUI library for screenshots"""
    try:
        import pyautogui
        import time
        
        print("\n=== Testing PyAutoGUI Screen Capture ===")
        
        # Get screen size
        screen_size = pyautogui.size()
        print(f"Screen size: {screen_size.width}x{screen_size.height}")
        
        # Test screenshot speed
        start_time = time.time()
        
        for i in range(5):
            screenshot = pyautogui.screenshot()
            
        end_time = time.time()
        avg_time = (end_time - start_time) / 5
        fps = 1 / avg_time
        
        print(f"Average screenshot time: {avg_time:.3f}s ({fps:.1f} FPS)")
        
        # Save a test screenshot
        output_path = "/home/evilbastardxd/test_screenshot_pyautogui.png"
        screenshot.save(output_path)
        print(f"✓ Test screenshot saved to: {output_path}")
        
        # Test region capture
        region_screenshot = pyautogui.screenshot(region=(100, 100, 400, 300))
        region_path = "/home/evilbastardxd/test_region_screenshot.png"
        region_screenshot.save(region_path)
        print(f"✓ Region screenshot saved to: {region_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ PyAutoGUI test failed: {e}")
        return False

def create_web_interface():
    """Create HTML interface for browser-based screen capture"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screen Capture Test - tools.py v0.3</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .controls { margin: 20px 0; }
        button { padding: 10px 20px; margin: 5px; font-size: 16px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        video { width: 100%; max-width: 600px; border: 1px solid #ccc; }
        .compatibility { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Screen Capture API Test - tools.py v0.3</h1>
        
        <div class="compatibility">
            <h3>Browser Compatibility Status</h3>
            <div id="compatibility-info">Checking browser capabilities...</div>
        </div>
        
        <div class="controls">
            <button id="start-capture">📺 Start Screen Capture</button>
            <button id="stop-capture" disabled>⏹️ Stop Capture</button>
            <button id="test-websocket">🔗 Test WebSocket Connection</button>
        </div>
        
        <div id="status" class="status" style="display: none;"></div>
        
        <div>
            <h3>Live Screen Capture</h3>
            <video id="screen-video" autoplay muted></video>
        </div>
        
        <div>
            <h3>Capture Information</h3>
            <pre id="capture-info"></pre>
        </div>
    </div>

    <script>
        let screenStream = null;
        let websocket = null;
        
        // Check browser compatibility
        function checkCompatibility() {
            const info = document.getElementById('compatibility-info');
            let report = '';
            
            // Check getDisplayMedia support
            if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
                report += '✅ getDisplayMedia: Supported\\n';
            } else {
                report += '❌ getDisplayMedia: Not supported\\n';
            }
            
            // Check WebRTC support
            if (window.RTCPeerConnection) {
                report += '✅ WebRTC: Supported\\n';
            } else {
                report += '❌ WebRTC: Not supported\\n';
            }
            
            // Check WebSocket support
            if (window.WebSocket) {
                report += '✅ WebSocket: Supported\\n';
            } else {
                report += '❌ WebSocket: Not supported\\n';
            }
            
            // Browser info
            report += `\\n🌐 Browser: ${navigator.userAgent}\\n`;
            report += `📱 Platform: ${navigator.platform}\\n`;
            report += `🖥️ Screen: ${screen.width}x${screen.height}\\n`;
            
            info.textContent = report;
        }
        
        // Start screen capture
        async function startCapture() {
            try {
                screenStream = await navigator.mediaDevices.getDisplayMedia({
                    video: {
                        mediaSource: 'screen',
                        width: { ideal: 1920 },
                        height: { ideal: 1080 },
                        frameRate: { ideal: 30 }
                    },
                    audio: true
                });
                
                const videoElement = document.getElementById('screen-video');
                videoElement.srcObject = screenStream;
                
                document.getElementById('start-capture').disabled = true;
                document.getElementById('stop-capture').disabled = false;
                
                showStatus('✅ Screen capture started successfully!', 'success');
                
                // Update capture info
                const track = screenStream.getVideoTracks()[0];
                const settings = track.getSettings();
                document.getElementById('capture-info').textContent = JSON.stringify(settings, null, 2);
                
                // Handle stream end
                track.onended = () => {
                    stopCapture();
                    showStatus('ℹ️ Screen capture ended by user', 'success');
                };
                
            } catch (error) {
                console.error('Error starting capture:', error);
                showStatus(`❌ Failed to start capture: ${error.message}`, 'error');
            }
        }
        
        // Stop screen capture
        function stopCapture() {
            if (screenStream) {
                screenStream.getTracks().forEach(track => track.stop());
                screenStream = null;
                
                const videoElement = document.getElementById('screen-video');
                videoElement.srcObject = null;
                
                document.getElementById('start-capture').disabled = false;
                document.getElementById('stop-capture').disabled = true;
                
                document.getElementById('capture-info').textContent = '';
            }
        }
        
        // Test WebSocket connection to Python backend
        function testWebSocket() {
            try {
                websocket = new WebSocket('ws://localhost:8080/ws');
                
                websocket.onopen = () => {
                    showStatus('✅ WebSocket connected to Python backend', 'success');
                    websocket.send(JSON.stringify({
                        type: 'test',
                        message: 'Hello from browser!'
                    }));
                };
                
                websocket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    showStatus(`📨 Received from Python: ${data.message}`, 'success');
                };
                
                websocket.onerror = (error) => {
                    showStatus('❌ WebSocket connection failed - Python server not running?', 'error');
                };
                
                websocket.onclose = () => {
                    showStatus('ℹ️ WebSocket connection closed', 'success');
                };
                
            } catch (error) {
                showStatus(`❌ WebSocket error: ${error.message}`, 'error');
            }
        }
        
        // Show status message
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }
        
        // Event listeners
        document.getElementById('start-capture').onclick = startCapture;
        document.getElementById('stop-capture').onclick = stopCapture;
        document.getElementById('test-websocket').onclick = testWebSocket;
        
        // Initialize
        checkCompatibility();
    </script>
</body>
</html>'''
    
    output_path = "/home/evilbastardxd/screen_capture_test.html"
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"✓ Web interface created: {output_path}")
    print("  Open in browser to test getDisplayMedia API")
    return output_path

def create_websocket_server():
    """Create WebSocket server for browser-Python communication"""
    server_code = '''#!/usr/bin/env python3
"""
WebSocket server for screen capture prototype
Bridges browser screen capture with Python backend
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenCaptureServer:
    def __init__(self):
        self.clients = set()
        
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        logger.info(f"Client {websocket.remote_address} connected")
        
    async def unregister(self, websocket):
        """Unregister a client"""
        self.clients.remove(websocket)
        logger.info(f"Client {websocket.remote_address} disconnected")
        
    async def handle_message(self, websocket, message):
        """Handle incoming message from browser"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'test':
                # Echo test message
                response = {
                    'type': 'test_response',
                    'message': f"Python server received: {data.get('message')}",
                    'timestamp': datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                
            elif msg_type == 'screen_frame':
                # Handle screen frame data (base64 encoded)
                logger.info("Received screen frame data")
                # TODO: Process frame with AI
                
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def client_handler(self, websocket, path):
        """Handle WebSocket client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

async def main():
    server = ScreenCaptureServer()
    
    print("🚀 Starting WebSocket server on ws://localhost:8080/ws")
    print("   Open screen_capture_test.html in browser to test")
    
    async with websockets.serve(server.client_handler, "localhost", 8080):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    output_path = "/home/evilbastardxd/websocket_server.py"
    with open(output_path, 'w') as f:
        f.write(server_code)
    
    # Make executable
    subprocess.run(['chmod', '+x', output_path])
    
    print(f"✓ WebSocket server created: {output_path}")
    print("  Run with: python websocket_server.py")
    return output_path

def generate_research_report(deps: Dict[str, bool]) -> str:
    """Generate comprehensive research report"""
    report = f"""
# Screen Capture Research Report - tools.py v0.3
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Dependency Analysis

### Available Libraries:
"""
    
    for lib, available in deps.items():
        status = "✅ Available" if available else "❌ Missing"
        report += f"- **{lib}**: {status}\n"
    
    report += """
## 🔍 Technical Findings

### Python Screen Capture Options:

1. **MSS (Multiple Screen Shot)**
   - ✅ Fastest cross-platform screenshots
   - ✅ Low CPU usage, high FPS potential
   - ✅ Supports multi-monitor setups
   - ✅ Direct memory access to screen buffer
   - 🔧 Best for: Real-time screen streaming

2. **PyAutoGUI**
   - ✅ Easy to use, well documented
   - ✅ Cross-platform compatibility
   - ❌ Slower than MSS
   - 🔧 Best for: Simple screenshot needs

3. **Browser getDisplayMedia()**
   - ✅ Native screen capture with user permission
   - ✅ High quality, efficient encoding
   - ✅ Built-in region selection UI
   - ❌ Requires browser environment
   - 🔧 Best for: User-controlled screen sharing

### Recommended Architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │  Python Backend │    │  AI Studio API │
│                 │    │                 │    │                 │
│ getDisplayMedia │◄──►│  WebSocket      │◄──►│  Gemini Live    │
│ Screen Capture  │    │  Server         │    │  Processing     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
 User Interface          tools.py Integration    Terminal Commands
```

## 🚀 Implementation Priority:

### Phase 1: Browser-Based Prototype
- ✅ HTML interface with getDisplayMedia()
- ✅ WebSocket communication with Python
- ✅ Basic screen capture testing

### Phase 2: Python Integration
- 🔄 WebSocket server for browser communication
- 🔄 Integration with existing tools.py
- 🔄 Basic AI command processing

### Phase 3: Production Features
- ⏳ Google AI Studio Live API integration
- ⏳ Advanced terminal control mapping
- ⏳ Session persistence and recovery

## 📋 Next Steps:

1. **Install missing dependencies**:
   ```bash
   pip install mss pyautogui websockets flask opencv-python
   ```

2. **Test browser compatibility**:
   - Open screen_capture_test.html in different browsers
   - Verify getDisplayMedia() functionality
   - Test WebSocket communication

3. **Develop prototype**:
   - Build basic screen capture → AI → terminal pipeline
   - Test with simple commands like "open terminal"
   - Validate performance and reliability

4. **Integrate with tools.py**:
   - Add screen capture server to existing codebase
   - Connect AI responses to terminal control functions
   - Implement session management

## 🔧 Development Environment Setup:

The prototype files have been created:
- `screen_capture_test.html` - Browser interface for testing
- `websocket_server.py` - Python WebSocket server
- `screen_capture_prototype.py` - This research script

Ready for next phase implementation! 🚀
"""
    
    return report

def main():
    """Main testing and research function"""
    print("🚀 Screen Capture Research & Prototype Development")
    print("=" * 60)
    
    # Check dependencies
    deps = check_dependencies()
    
    # Test available screen capture methods
    if deps['mss']:
        test_screen_capture_mss()
    
    if deps['pyautogui']:
        test_screen_capture_pyautogui()
    
    # Create web interface and server
    print("\n=== Creating Prototype Files ===")
    web_interface = create_web_interface()
    websocket_server = create_websocket_server()
    
    # Generate research report
    report = generate_research_report(deps)
    report_path = "/home/evilbastardxd/screen_capture_research_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✓ Research report generated: {report_path}")
    
    print("\n" + "=" * 60)
    print("🎯 PROTOTYPE READY FOR TESTING!")
    print("\nNext steps:")
    print("1. Install missing dependencies if needed")
    print("2. Run: python websocket_server.py")
    print("3. Open screen_capture_test.html in browser")
    print("4. Test screen capture and WebSocket communication")
    print("\nThis will validate our hybrid architecture approach! 🚀")

if __name__ == "__main__":
    main()