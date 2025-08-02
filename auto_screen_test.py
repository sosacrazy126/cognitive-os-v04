#!/usr/bin/env python3
"""
Auto Screen Test - Automatically connects and monitors full screen sharing
"""

import asyncio
import websockets
import json
import subprocess
import time
import os
import signal
from datetime import datetime

class AutoScreenTest:
    def __init__(self):
        self.daemon_process = None
        self.browser_process = None
        self.monitor_active = False
        self.frames_received = 0
        
    def start_daemon(self):
        """Start the enhanced cognitive daemon"""
        print("🚀 Starting Enhanced Cognitive Daemon...")
        cmd = ["python3", "/home/evilbastardxd/enhanced_cognitive_daemon.py"]
        self.daemon_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Give daemon time to start
        print("✅ Daemon started")
        
    def open_browser_interface(self):
        """Open browser with auto-connect script"""
        print("🌐 Opening browser interface...")
        
        # Create auto-connect HTML that will automatically start everything
        auto_html = """<!DOCTYPE html>
<html>
<head>
    <title>Auto Screen Test - Cognitive OS</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: white; margin: 20px; }
        .status { padding: 15px; margin: 10px 0; border-radius: 8px; }
        .success { background: #155724; color: #d4edda; }
        .error { background: #721c24; color: #f8d7da; }
        .info { background: #0c5460; color: #d1ecf1; }
        button { padding: 12px 24px; margin: 10px; font-size: 16px; border: none; border-radius: 8px; cursor: pointer; }
        .primary { background: #007acc; color: white; }
        .success-btn { background: #28a745; color: white; }
        .danger { background: #dc3545; color: white; }
        video { width: 100%; max-width: 600px; border: 2px solid #007acc; border-radius: 8px; }
        #log { background: #222; padding: 15px; border-radius: 8px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>
    <h1>🧬 Auto Screen Test - Cognitive OS v0.4</h1>
    
    <div id="status" class="status info">
        🔄 Initializing auto screen test...
    </div>
    
    <div>
        <button id="auto-start" class="primary">🚀 AUTO START FULL TEST</button>
        <button id="manual-capture" class="success-btn">📺 Manual Screen Capture</button>
        <button id="stop-test" class="danger" disabled>⏹️ Stop Test</button>
    </div>
    
    <div>
        <h3>📺 Screen Capture</h3>
        <video id="screen-video" autoplay muted></video>
    </div>
    
    <div>
        <h3>📋 Test Log</h3>
        <div id="log"></div>
    </div>

    <script>
        class AutoScreenTest {
            constructor() {
                this.websocket = null;
                this.screenStream = null;
                this.isStreaming = false;
                this.frameCount = 0;
                this.autoMode = false;
                
                this.setupEventListeners();
                this.log('🧬 Auto Screen Test initialized');
            }
            
            setupEventListeners() {
                document.getElementById('auto-start').onclick = () => this.autoStartTest();
                document.getElementById('manual-capture').onclick = () => this.startScreenCapture();
                document.getElementById('stop-test').onclick = () => this.stopTest();
            }
            
            log(message) {
                const timestamp = new Date().toLocaleTimeString(); 
                const logDiv = document.getElementById('log');
                logDiv.innerHTML += `[${timestamp}] ${message}<br>`;
                logDiv.scrollTop = logDiv.scrollHeight;
                console.log(message);
            }
            
            updateStatus(message, className = 'info') {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = `status ${className}`;
            }
            
            async autoStartTest() {
                this.log('🚀 Starting automatic full screen test...');
                this.autoMode = true;
                
                try {
                    // Step 1: Connect to WebSocket
                    await this.connectWebSocket();
                    
                    // Step 2: Start screen capture
                    await this.startScreenCapture();
                    
                    // Step 3: Start streaming
                    await this.startStreaming();
                    
                    this.updateStatus('✅ Auto test running - AI can see your screen!', 'success');
                    document.getElementById('auto-start').disabled = true;
                    document.getElementById('stop-test').disabled = false;
                    
                } catch (error) {
                    this.log(`❌ Auto test failed: ${error.message}`);
                    this.updateStatus(`❌ Auto test failed: ${error.message}`, 'error');
                }
            }
            
            async connectWebSocket() {
                return new Promise((resolve, reject) => {
                    this.log('🔗 Connecting to Cognitive OS daemon...');
                    
                    this.websocket = new WebSocket('ws://localhost:8084/ws');
                    
                    this.websocket.onopen = () => {
                        this.log('✅ WebSocket connected');
                        resolve();
                    };
                    
                    this.websocket.onmessage = (event) => {
                        try {
                            const data = JSON.parse(event.data);
                            if (data.type === 'welcome') {
                                this.log(`🧬 Connected to session: ${data.session_id}`);
                            } else if (data.type === 'frame_processed') {
                                this.frameCount++;
                                this.log(`📺 Frame processed: ${this.frameCount}`);
                            }
                        } catch (e) {
                            // Binary data
                        }
                    };
                    
                    this.websocket.onerror = () => reject(new Error('WebSocket connection failed'));
                    
                    setTimeout(() => reject(new Error('WebSocket connection timeout')), 5000);
                });
            }
            
            async startScreenCapture() {
                this.log('📺 Starting screen capture...');
                
                try {
                    this.screenStream = await navigator.mediaDevices.getDisplayMedia({
                        video: {
                            mediaSource: 'screen',
                            width: { ideal: 1920 },
                            height: { ideal: 1080 },
                            frameRate: { ideal: 10 }
                        },
                        audio: false
                    });
                    
                    document.getElementById('screen-video').srcObject = this.screenStream;
                    this.log('✅ Screen capture active');
                    
                    // Handle stream end
                    const track = this.screenStream.getVideoTracks()[0];
                    track.onended = () => {
                        this.log('⏹️ Screen capture ended by user');
                        this.stopTest();
                    };
                    
                } catch (error) {
                    throw new Error(`Screen capture failed: ${error.message}`);
                }
            }
            
            async startStreaming() {
                if (!this.screenStream || !this.websocket) {
                    throw new Error('Screen capture and WebSocket required');
                }
                
                this.log('🚀 Starting frame streaming at 5 FPS...');
                this.isStreaming = true;
                
                const video = document.getElementById('screen-video');
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                const captureFrame = () => {
                    if (!this.isStreaming) return;
                    
                    try {
                        canvas.width = video.videoWidth || 800;
                        canvas.height = video.videoHeight || 600;
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        canvas.toBlob((blob) => {
                            if (blob && this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                                const reader = new FileReader();
                                reader.onload = () => {
                                    const base64Data = reader.result.split(',')[1];
                                    
                                    const frameMessage = {
                                        type: 'screen_frame',
                                        data: base64Data,
                                        width: canvas.width,
                                        height: canvas.height,
                                        timestamp: Date.now(),
                                        frameNumber: this.frameCount
                                    };
                                    
                                    this.websocket.send(JSON.stringify(frameMessage));
                                };
                                reader.readAsDataURL(blob);
                            }
                        }, 'image/jpeg', 0.8);
                        
                    } catch (error) {
                        this.log(`❌ Frame capture error: ${error.message}`);
                    }
                };
                
                // Start streaming at 5 FPS
                this.streamingInterval = setInterval(captureFrame, 200);
                this.log('✅ Frame streaming started');
            }
            
            stopTest() {
                this.log('⏹️ Stopping auto test...');
                
                if (this.streamingInterval) {
                    clearInterval(this.streamingInterval);
                    this.isStreaming = false;
                }
                
                if (this.screenStream) {
                    this.screenStream.getTracks().forEach(track => track.stop());
                    this.screenStream = null;
                }
                
                if (this.websocket) {
                    this.websocket.close();
                    this.websocket = null;
                }
                
                document.getElementById('auto-start').disabled = false;
                document.getElementById('stop-test').disabled = true;
                
                this.updateStatus('⏹️ Test stopped', 'info');
                this.log('✅ Auto test stopped');
            }
        }
        
        // Initialize when page loads
        window.addEventListener('DOMContentLoaded', () => {
            window.autoTest = new AutoScreenTest();
        });
    </script>
</body>
</html>"""
        
        # Write auto-connect HTML
        auto_file = "/home/evilbastardxd/auto_screen_test.html"
        with open(auto_file, 'w') as f:
            f.write(auto_html)
        
        # Open in browser
        cmd = ["firefox", auto_file]
        self.browser_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Give browser time to open
        print("✅ Browser opened with auto-test interface")
        
    async def monitor_live_feed(self):
        """Monitor the live screen feed and provide real-time feedback"""
        print("👁️  Starting live monitoring...")
        
        try:
            uri = 'ws://localhost:8084/ws'
            async with websockets.connect(uri) as websocket:
                print("🧬 Connected to Enhanced Cognitive Daemon")
                
                # Wait for welcome
                welcome = await websocket.recv()
                welcome_data = json.loads(welcome)
                print(f"✅ Session: {welcome_data['session_id']}")
                
                start_time = datetime.now()
                frame_count = 0
                
                print("\n👁️  LIVE AI VISION FEEDBACK:")
                print("=" * 50)
                
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        
                        if data.get('type') == 'frame_processed':
                            frame_count += 1
                            analysis = data.get('analysis', {})
                            stats = data.get('session_stats', {})
                            
                            print(f"📺 FRAME {frame_count} PROCESSED:")
                            print(f"   Resolution: {analysis.get('dimensions')}")
                            print(f"   Brightness: {analysis.get('avg_brightness')}")
                            print(f"   Size: {analysis.get('size_bytes')} bytes")
                            print(f"   Total data: {stats.get('total_data_mb')} MB")
                            
                            # Provide visual interpretation
                            brightness = analysis.get('avg_brightness', 0)
                            if brightness:
                                if brightness < 50:
                                    print("   🌙 AI SEES: Dark screen (terminal/code editor)")
                                elif brightness > 200:
                                    print("   ☀️ AI SEES: Bright screen (browser/documents)")
                                else:
                                    print("   🌤️ AI SEES: Mixed content screen")
                            
                            print()
                            
                            if frame_count == 1:
                                print("🎉 FIRST FRAME! AI VISION IS ACTIVE!")
                                print("🧬 I can now see your screen in real-time!")
                                print()
                            
                        elif data.get('type') == 'test_response':
                            print(f"📊 Daemon stats: {data.get('daemon_stats')}")
                            
                    except asyncio.TimeoutError:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        if frame_count > 0:
                            fps = frame_count / elapsed
                            print(f"⏰ Monitoring active... ({frame_count} frames, {fps:.1f} FPS)")
                        else:
                            print("⏰ Waiting for screen frames...")
                        
                        if elapsed > 120:  # 2 minute timeout
                            break
                            
        except Exception as e:
            print(f"❌ Monitor error: {e}")
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up...")
        
        if self.daemon_process:
            self.daemon_process.terminate()
            print("✅ Daemon stopped")
            
        if self.browser_process:
            self.browser_process.terminate()
            print("✅ Browser closed")
    
    async def run_full_test(self):
        """Run the complete automatic screen test"""
        print("🧬 AUTOMATIC FULL SCREEN TEST")
        print("=" * 60)
        
        try:
            # Start daemon
            self.start_daemon()
            
            # Open browser
            self.open_browser_interface()
            
            print("\n🎯 NEXT STEPS:")
            print("1. In the Firefox browser that opened:")
            print("   - Click '🚀 AUTO START FULL TEST'")
            print("   - Grant screen sharing permissions when prompted")
            print("2. The test will automatically:")
            print("   - Connect to the daemon")
            print("   - Start screen capture")
            print("   - Begin streaming frames")
            print("3. I will provide live feedback on what I can see!")
            print()
            
            # Start monitoring
            await self.monitor_live_feed()
            
        except KeyboardInterrupt:
            print("\n🛑 Test stopped by user")
        finally:
            self.cleanup()

def run_auto_screen_test():
    """Function to easily run the auto screen test"""
    test = AutoScreenTest()
    try:
        asyncio.run(test.run_full_test())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        test.cleanup()

if __name__ == "__main__":
    run_auto_screen_test()