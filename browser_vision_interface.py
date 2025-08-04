#!/usr/bin/env python3
"""
Browser Vision Interface - Connects to screen sharing bridge for real-time analysis
Provides structured analysis of browser-shared screen content
"""

import asyncio
import json
import websockets
from typing import Dict, Any, Optional
from datetime import datetime
import base64
import io
from PIL import Image
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserVisionInterface:
    """Interface for analyzing browser-shared screen content"""
    
    def __init__(self, bridge_url: str = "ws://localhost:8765"):
        self.bridge_url = bridge_url
        self.connection = None
        self.current_frame = None
        self.frame_count = 0
        self.analysis_history = []
        self.max_history = 10
        
    async def connect(self):
        """Connect to screen sharing bridge"""
        try:
            self.connection = await websockets.connect(self.bridge_url)
            logger.info(f"Connected to vision bridge at {self.bridge_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to bridge: {e}")
            return False
    
    async def start_analysis_loop(self):
        """Start continuous frame analysis loop"""
        if not self.connection:
            if not await self.connect():
                return
        
        logger.info("🔍 Starting browser vision analysis...")
        
        try:
            async for message in self.connection:
                try:
                    frame_data = json.loads(message)
                    
                    if frame_data.get('source') == 'browser_screen_share':
                        # Analyze the frame
                        analysis = await self.analyze_frame(frame_data)
                        
                        # Store in history
                        self.analysis_history.append(analysis)
                        if len(self.analysis_history) > self.max_history:
                            self.analysis_history.pop(0)
                        
                        # Print analysis
                        self._print_analysis(analysis)
                        
                        self.frame_count += 1
                        
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received from bridge")
                except Exception as e:
                    logger.error(f"Frame analysis error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection to bridge closed")
        except Exception as e:
            logger.error(f"Analysis loop error: {e}")
    
    async def analyze_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a screen frame and return structured insights"""
        
        analysis = {
            'timestamp': frame_data.get('timestamp'),
            'frame_id': self.frame_count,
            'dimensions': f"{frame_data.get('width', 0)}x{frame_data.get('height', 0)}",
            'source': frame_data.get('source'),
            'visual_analysis': {},
            'content_analysis': {},
            'change_detection': {},
            'actionable_items': [],
            'confidence': 0.0
        }
        
        try:
            # Decode base64 frame
            frame_base64 = frame_data.get('frame', '')
            if frame_base64:
                img_data = base64.b64decode(frame_base64)
                img = Image.open(io.BytesIO(img_data))
                
                # Visual analysis
                analysis['visual_analysis'] = await self._analyze_visual_content(img)
                
                # Content analysis (basic pattern recognition)
                analysis['content_analysis'] = await self._analyze_content_patterns(img)
                
                # Change detection
                analysis['change_detection'] = self._detect_changes(analysis)
                
                # Extract actionable items
                analysis['actionable_items'] = self._extract_actionable_items(analysis)
                
                # Overall confidence
                analysis['confidence'] = self._calculate_confidence(analysis)
                
                self.current_frame = analysis
                
        except Exception as e:
            analysis['error'] = str(e)
            logger.error(f"Frame decoding error: {e}")
        
        return analysis
    
    async def _analyze_visual_content(self, img: Image.Image) -> Dict[str, Any]:
        """Analyze visual characteristics of the image"""
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Basic visual metrics
        brightness = np.mean(img_array) / 255.0
        contrast = np.std(img_array) / 255.0
        
        # Color analysis
        avg_color = np.mean(img_array.reshape(-1, 3), axis=0)
        dominant_color = self._describe_color(avg_color)
        
        # Edge detection (simple)
        edges = self._simple_edge_detection(img_array)
        
        return {
            'brightness': round(brightness, 3),
            'contrast': round(contrast, 3),
            'dominant_color': dominant_color,
            'is_dark': brightness < 0.3,
            'is_bright': brightness > 0.7,
            'has_high_contrast': contrast > 0.3,
            'edge_density': edges,
            'likely_content_type': self._classify_content_type(brightness, contrast, edges)
        }
    
    async def _analyze_content_patterns(self, img: Image.Image) -> Dict[str, Any]:
        """Analyze content patterns to identify likely screen content"""
        
        img_array = np.array(img)
        height, width = img_array.shape[:2]
        
        # Zone analysis
        zones = {
            'top': img_array[:height//4],
            'middle': img_array[height//4:3*height//4], 
            'bottom': img_array[3*height//4:]
        }
        
        zone_analysis = {}
        for zone_name, zone_data in zones.items():
            brightness = np.mean(zone_data) / 255.0
            zone_analysis[zone_name] = {
                'brightness': round(brightness, 3),
                'likely_type': self._classify_zone_type(zone_name, brightness)
            }
        
        # Pattern detection
        patterns = self._detect_ui_patterns(img_array)
        
        return {
            'zones': zone_analysis,
            'detected_patterns': patterns,
            'likely_application': self._guess_application_type(zone_analysis, patterns),
            'text_regions': self._detect_text_regions(img_array)
        }
    
    def _describe_color(self, rgb: np.ndarray) -> str:
        """Convert RGB to color description"""
        r, g, b = rgb
        
        if r > 200 and g > 200 and b > 200:
            return "light/white"
        elif r < 50 and g < 50 and b < 50:
            return "dark/black"
        elif r > g and r > b:
            return "reddish"
        elif g > r and g > b:
            return "greenish"
        elif b > r and b > g:
            return "bluish"
        else:
            return "neutral"
    
    def _simple_edge_detection(self, img_array: np.ndarray) -> int:
        """Simple edge detection for UI element counting"""
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array
            
        # Simple gradient
        dx = np.abs(np.diff(gray, axis=1))
        dy = np.abs(np.diff(gray, axis=0))
        
        edge_count = np.sum(dx > 30) + np.sum(dy > 30)
        return edge_count
    
    def _classify_content_type(self, brightness: float, contrast: float, edges: int) -> str:
        """Classify likely content type based on visual characteristics"""
        
        if brightness < 0.2 and contrast > 0.2:
            return "terminal/console"
        elif brightness > 0.8 and contrast > 0.3:
            return "document/text"
        elif edges > 5000:
            return "complex_ui/dashboard"
        elif brightness > 0.5 and contrast < 0.2:
            return "simple_ui/webpage"
        else:
            return "mixed_content"
    
    def _classify_zone_type(self, zone_name: str, brightness: float) -> str:
        """Classify zone type based on position and brightness"""
        
        if zone_name == 'top':
            if brightness < 0.3:
                return "dark_header/menu"
            else:
                return "light_header/toolbar"
        elif zone_name == 'middle':
            if brightness > 0.7:
                return "content_area/document"
            else:
                return "application_content"
        else:  # bottom
            if brightness < 0.3:
                return "status_bar/footer"
            else:
                return "content_footer"
    
    def _detect_ui_patterns(self, img_array: np.ndarray) -> list:
        """Detect common UI patterns"""
        patterns = []
        
        mean_brightness = np.mean(img_array)
        
        # Terminal pattern
        if mean_brightness < 50:
            patterns.append("terminal_interface")
        
        # High contrast suggests UI elements
        if np.std(img_array) > 80:
            patterns.append("ui_elements")
        
        # Window pattern (borders)
        edges = self._simple_edge_detection(img_array)
        if edges > 1000:
            patterns.append("windowed_application")
        
        return patterns
    
    def _detect_text_regions(self, img_array: np.ndarray) -> list:
        """Detect likely text regions"""
        # Placeholder for OCR integration
        contrast = np.std(img_array)
        
        if contrast > 60:
            return ["high_contrast_text_regions"]
        elif contrast > 30:
            return ["moderate_text_content"]
        else:
            return ["low_text_content"]
    
    def _guess_application_type(self, zones: Dict, patterns: list) -> str:
        """Guess application type from analysis"""
        
        if "terminal_interface" in patterns:
            return "terminal/console"
        elif zones['top']['likely_type'] == "dark_header/menu":
            return "desktop_application"
        elif "ui_elements" in patterns:
            return "web_browser/dashboard"
        else:
            return "unknown_application"
    
    def _detect_changes(self, current_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes from previous frames"""
        
        if not self.analysis_history:
            return {"status": "first_frame", "changes": []}
        
        last_analysis = self.analysis_history[-1]
        changes = []
        
        # Compare brightness
        current_brightness = current_analysis['visual_analysis'].get('brightness', 0)
        last_brightness = last_analysis['visual_analysis'].get('brightness', 0)
        
        if abs(current_brightness - last_brightness) > 0.1:
            changes.append(f"Brightness changed: {last_brightness:.2f} → {current_brightness:.2f}")
        
        # Compare application type
        current_app = current_analysis['content_analysis'].get('likely_application', '')
        last_app = last_analysis['content_analysis'].get('likely_application', '')
        
        if current_app != last_app:
            changes.append(f"Application changed: {last_app} → {current_app}")
        
        return {
            "status": "changed" if changes else "stable",
            "changes": changes,
            "time_since_last": "1s"  # Approximate
        }
    
    def _extract_actionable_items(self, analysis: Dict[str, Any]) -> list:
        """Extract actionable items from analysis"""
        
        items = []
        visual = analysis.get('visual_analysis', {})
        content = analysis.get('content_analysis', {})
        
        # Terminal detected
        if content.get('likely_application') == 'terminal/console':
            items.append({
                'type': 'terminal_active',
                'description': 'Terminal/console window detected',
                'suggested_action': 'monitor_commands',
                'priority': 'medium'
            })
        
        # High contrast suggests active UI
        if visual.get('has_high_contrast'):
            items.append({
                'type': 'active_ui',
                'description': 'Active UI with high contrast detected',
                'suggested_action': 'analyze_ui_elements',
                'priority': 'low'
            })
        
        # Dark screen might indicate error or loading
        if visual.get('is_dark'):
            items.append({
                'type': 'dark_screen',
                'description': 'Dark screen detected - possible error or loading',
                'suggested_action': 'check_system_status',
                'priority': 'high'
            })
        
        return items
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis"""
        
        confidence = 0.5  # Base confidence
        
        # Higher for successful visual analysis
        if 'visual_analysis' in analysis and not analysis.get('error'):
            confidence += 0.3
        
        # Higher for detected patterns
        patterns = analysis.get('content_analysis', {}).get('detected_patterns', [])
        confidence += min(len(patterns) * 0.1, 0.2)
        
        return min(confidence, 1.0)
    
    def _print_analysis(self, analysis: Dict[str, Any]):
        """Print structured analysis to console"""
        
        timestamp = analysis.get('timestamp', 'unknown')
        frame_id = analysis.get('frame_id', 0)
        
        print(f"\n🔍 FRAME ANALYSIS #{frame_id} [{timestamp}]")
        print("=" * 60)
        
        # Visual analysis
        visual = analysis.get('visual_analysis', {})
        print(f"📊 Visual: {visual.get('brightness', 0):.2f} brightness, {visual.get('dominant_color', 'unknown')} tone")
        print(f"   Content type: {visual.get('likely_content_type', 'unknown')}")
        
        # Content analysis  
        content = analysis.get('content_analysis', {})
        print(f"🖥️  Application: {content.get('likely_application', 'unknown')}")
        patterns = content.get('detected_patterns', [])
        if patterns:
            print(f"   Patterns: {', '.join(patterns)}")
        
        # Changes
        changes = analysis.get('change_detection', {})
        if changes.get('changes'):
            print(f"🔄 Changes: {'; '.join(changes['changes'])}")
        
        # Actionable items
        items = analysis.get('actionable_items', [])
        if items:
            print("⚡ Actions:")
            for item in items:
                priority = item.get('priority', 'low').upper()
                print(f"   [{priority}] {item.get('description', '')}")
        
        confidence = analysis.get('confidence', 0)
        print(f"🎯 Confidence: {confidence:.1%}")
        print()
    
    async def get_current_analysis(self) -> Optional[Dict[str, Any]]:
        """Get the most recent frame analysis"""
        return self.current_frame
    
    async def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of recent analysis"""
        
        if not self.analysis_history:
            return {"status": "no_data"}
        
        recent = self.analysis_history[-5:]  # Last 5 frames
        
        # Aggregate data
        applications = [a['content_analysis'].get('likely_application', 'unknown') for a in recent]
        brightness_levels = [a['visual_analysis'].get('brightness', 0) for a in recent]
        
        return {
            "frames_analyzed": len(self.analysis_history),
            "recent_applications": list(set(applications)),
            "avg_brightness": sum(brightness_levels) / len(brightness_levels),
            "stability": "stable" if len(set(applications)) == 1 else "changing",
            "last_update": recent[-1].get('timestamp') if recent else None
        }


async def main():
    """Main browser vision analysis"""
    interface = BrowserVisionInterface()
    
    print("🔍 Browser Vision Interface")
    print("Connecting to screen sharing bridge...")
    
    try:
        await interface.start_analysis_loop()
    except KeyboardInterrupt:
        print("\n🛑 Analysis stopped")


if __name__ == "__main__":
    asyncio.run(main())