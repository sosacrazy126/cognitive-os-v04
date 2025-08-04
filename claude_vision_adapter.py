#!/usr/bin/env python3
"""
Claude Vision Adapter - Bridge between Vision Pipeline and Claude Code
Converts visual data to structured text for Claude's consumption
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64
import io
from PIL import Image
import numpy as np


class ClaudeVisionAdapter:
    """Adapts vision data for Claude Code/CLI agents without native vision"""
    
    def __init__(self):
        self.frame_history = []
        self.max_history = 10
        self.scene_description = ""
        self.last_significant_change = None
        
    async def process_frame_for_claude(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert visual frame to Claude-readable format"""
        
        # Extract frame metadata
        timestamp = frame_data.get('timestamp', datetime.utcnow().isoformat())
        width = frame_data.get('width', 0)
        height = frame_data.get('height', 0)
        
        # Process visual analysis
        analysis = frame_data.get('analysis', {})
        brightness = analysis.get('brightness', 0.5)
        
        # Decode and analyze frame
        frame_description = await self._analyze_frame_content(frame_data)
        
        # Detect changes
        change_detection = self._detect_changes(frame_description)
        
        # Build structured output for Claude
        claude_data = {
            "vision_context": {
                "timestamp": timestamp,
                "screen_dimensions": f"{width}x{height}",
                "brightness_level": self._describe_brightness(brightness),
                "scene_description": frame_description['scene'],
                "detected_elements": frame_description['elements'],
                "text_visible": frame_description['text'],
                "changes": change_detection,
                "actionable_items": self._extract_actionable_items(frame_description)
            },
            "suggested_tools": self._suggest_tools(frame_description),
            "frame_metadata": {
                "fps": frame_data.get('fps', 5),
                "format": frame_data.get('format', 'jpeg')
            }
        }
        
        # Update history
        self._update_history(claude_data)
        
        return claude_data
    
    async def _analyze_frame_content(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze frame content and create descriptions"""
        
        # This is a simplified version - in production, you'd use OCR and object detection
        # For now, we'll create structured descriptions based on frame analysis
        
        try:
            # Decode frame
            img_data = base64.b64decode(frame_data['frame'])
            img = Image.open(io.BytesIO(img_data))
            
            # Convert to numpy for analysis
            img_array = np.array(img)
            
            # Simple zone analysis
            height, width = img_array.shape[:2]
            zones = {
                'top': img_array[:height//3],
                'middle': img_array[height//3:2*height//3],
                'bottom': img_array[2*height//3:]
            }
            
            # Analyze dominant colors per zone
            zone_info = {}
            for zone_name, zone_data in zones.items():
                avg_color = np.mean(zone_data.reshape(-1, 3), axis=0)
                zone_info[zone_name] = {
                    'dominant_color': self._describe_color(avg_color),
                    'brightness': np.mean(avg_color) / 255
                }
            
            # Build description
            description = {
                'scene': self._generate_scene_description(zone_info),
                'elements': self._detect_ui_elements(img_array),
                'text': self._extract_text_regions(img_array),
                'zones': zone_info
            }
            
            return description
            
        except Exception as e:
            return {
                'scene': 'Unable to analyze frame content',
                'elements': [],
                'text': [],
                'error': str(e)
            }
    
    def _describe_brightness(self, brightness: float) -> str:
        """Convert brightness value to descriptive text"""
        if brightness < 0.2:
            return "very dark"
        elif brightness < 0.4:
            return "dark"
        elif brightness < 0.6:
            return "normal"
        elif brightness < 0.8:
            return "bright"
        else:
            return "very bright"
    
    def _describe_color(self, rgb: np.ndarray) -> str:
        """Convert RGB values to color description"""
        r, g, b = rgb
        
        # Simple color classification
        if r > 200 and g > 200 and b > 200:
            return "white/light"
        elif r < 50 and g < 50 and b < 50:
            return "black/dark"
        elif r > g and r > b:
            return "reddish"
        elif g > r and g > b:
            return "greenish"
        elif b > r and b > g:
            return "bluish"
        else:
            return "neutral/gray"
    
    def _generate_scene_description(self, zone_info: Dict[str, Any]) -> str:
        """Generate natural language scene description"""
        
        # Build description based on zones
        descriptions = []
        
        if zone_info['top']['dominant_color'] in ['black/dark', 'neutral/gray']:
            descriptions.append("dark header or terminal area at top")
        elif zone_info['top']['dominant_color'] == 'white/light':
            descriptions.append("bright header or menu bar at top")
            
        if zone_info['middle']['brightness'] > 0.5:
            descriptions.append("main content area is well-lit")
        else:
            descriptions.append("main content area is dimmed")
            
        if zone_info['bottom']['dominant_color'] in ['black/dark', 'neutral/gray']:
            descriptions.append("dark footer or status bar at bottom")
            
        return "Screen shows: " + ", ".join(descriptions) if descriptions else "Standard desktop view"
    
    def _detect_ui_elements(self, img_array: np.ndarray) -> List[str]:
        """Detect common UI elements (simplified)"""
        
        elements = []
        height, width = img_array.shape[:2]
        
        # Check for common patterns
        # Terminal detection (dark background)
        if np.mean(img_array) < 50:
            elements.append("terminal or console window")
            
        # Window detection (bright areas)
        bright_regions = np.sum(img_array > 200) / img_array.size
        if bright_regions > 0.3:
            elements.append("application window")
            
        # Edge detection for buttons/borders (simplified)
        edges = self._simple_edge_detection(img_array)
        if edges > 1000:
            elements.append("multiple UI elements or buttons")
            
        return elements
    
    def _simple_edge_detection(self, img_array: np.ndarray) -> int:
        """Simple edge detection to count UI elements"""
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array
            
        # Simple gradient
        dx = np.abs(np.diff(gray, axis=1))
        dy = np.abs(np.diff(gray, axis=0))
        
        # Count significant edges
        edge_threshold = 30
        edge_count = np.sum(dx > edge_threshold) + np.sum(dy > edge_threshold)
        
        return edge_count
    
    def _extract_text_regions(self, img_array: np.ndarray) -> List[str]:
        """Identify potential text regions (placeholder for OCR)"""
        
        # In production, you'd use actual OCR here
        # For now, return placeholder based on image characteristics
        
        regions = []
        
        # Check for text-like patterns (high contrast areas)
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array
            
        contrast = np.std(gray)
        
        if contrast > 50:
            regions.append("high contrast areas suggesting text")
        
        if np.mean(gray) < 100:
            regions.append("light text on dark background (terminal-like)")
        elif np.mean(gray) > 150:
            regions.append("dark text on light background (document-like)")
            
        return regions
    
    def _detect_changes(self, current_description: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes from previous frames"""
        
        if not self.frame_history:
            return {"status": "first_frame", "changes": []}
            
        last_frame = self.frame_history[-1]
        changes = []
        
        # Compare scene descriptions
        if current_description['scene'] != self.scene_description:
            changes.append(f"Scene changed: {current_description['scene']}")
            self.scene_description = current_description['scene']
            
        # Compare elements
        current_elements = set(current_description['elements'])
        last_elements = set(last_frame.get('vision_context', {}).get('detected_elements', []))
        
        new_elements = current_elements - last_elements
        removed_elements = last_elements - current_elements
        
        if new_elements:
            changes.append(f"New elements: {', '.join(new_elements)}")
        if removed_elements:
            changes.append(f"Removed elements: {', '.join(removed_elements)}")
            
        # Determine significance
        is_significant = len(changes) > 0
        
        if is_significant:
            self.last_significant_change = datetime.utcnow()
            
        return {
            "status": "changed" if is_significant else "stable",
            "changes": changes,
            "time_since_last_change": (
                (datetime.utcnow() - self.last_significant_change).total_seconds()
                if self.last_significant_change else None
            )
        }
    
    def _extract_actionable_items(self, description: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract items that might require action"""
        
        actionable = []
        
        # Check for error indicators
        if any('error' in elem.lower() for elem in description['elements']):
            actionable.append({
                "type": "error",
                "description": "Possible error message detected",
                "suggested_action": "system.execute",
                "priority": "high"
            })
            
        # Check for terminal
        if 'terminal' in ' '.join(description['elements']).lower():
            actionable.append({
                "type": "terminal",
                "description": "Terminal window detected",
                "suggested_action": "terminal.read_output",
                "priority": "medium"
            })
            
        # Check for dialogs
        if 'dialog' in ' '.join(description['elements']).lower():
            actionable.append({
                "type": "dialog",
                "description": "Dialog box detected",
                "suggested_action": "vision.capture_region",
                "priority": "high"
            })
            
        return actionable
    
    def _suggest_tools(self, description: Dict[str, Any]) -> List[str]:
        """Suggest relevant tools based on screen content"""
        
        suggestions = []
        
        elements_text = ' '.join(description['elements'] + description['text']).lower()
        
        if 'terminal' in elements_text or 'console' in elements_text:
            suggestions.extend(['terminal.read_output', 'terminal.send_keys'])
            
        if 'error' in elements_text:
            suggestions.extend(['system.execute', 'system.read_file'])
            
        if 'dialog' in elements_text or 'button' in elements_text:
            suggestions.extend(['vision.capture_region', 'terminal.send_keys'])
            
        if not suggestions:
            suggestions = ['vision.analyze_frame', 'system.list_directory']
            
        return list(set(suggestions))  # Remove duplicates
    
    def _update_history(self, claude_data: Dict[str, Any]):
        """Update frame history"""
        self.frame_history.append(claude_data)
        
        # Keep only recent frames
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of recent visual context"""
        
        if not self.frame_history:
            return {"status": "no_history"}
            
        recent_changes = []
        recent_elements = set()
        
        for frame in self.frame_history[-5:]:
            context = frame.get('vision_context', {})
            changes = context.get('changes', {}).get('changes', [])
            recent_changes.extend(changes)
            
            elements = context.get('detected_elements', [])
            recent_elements.update(elements)
            
        return {
            "recent_changes": recent_changes[-5:],  # Last 5 changes
            "persistent_elements": list(recent_elements),
            "current_scene": self.scene_description,
            "stability": "stable" if not recent_changes else "changing",
            "frame_count": len(self.frame_history)
        }


# Integration with Claude Code
class ClaudeVisionBridge:
    """Bridge to make vision data accessible to Claude Code"""
    
    def __init__(self):
        self.adapter = ClaudeVisionAdapter()
        self.vision_interface = None
        
    async def connect(self, vision_ws_url: str = "ws://localhost:8765"):
        """Connect to vision stream"""
        from vision_tool_interface import VisionToolInterface
        
        self.vision_interface = VisionToolInterface(vision_ws_url)
        await self.vision_interface.connect_vision()
        
    async def get_vision_context(self) -> str:
        """Get current vision context as Claude-readable text"""
        
        if not self.vision_interface:
            return "Vision not connected. Use 'connect' first."
            
        # Get current frame
        frame_result = await self.vision_interface.get_current_frame()
        if not frame_result.success:
            return f"Failed to get frame: {frame_result.error}"
            
        # Process for Claude
        claude_data = await self.adapter.process_frame_for_claude(frame_result.data)
        
        # Format as readable text
        context = claude_data['vision_context']
        
        text_output = f"""
Current Visual Context:
- Time: {context['timestamp']}
- Screen: {context['screen_dimensions']} ({context['brightness_level']})
- Scene: {context['scene_description']}
- Elements: {', '.join(context['detected_elements']) if context['detected_elements'] else 'none detected'}
- Text regions: {', '.join(context['text_visible']) if context['text_visible'] else 'none detected'}
- Changes: {context['changes']['status']} - {'; '.join(context['changes']['changes']) if context['changes']['changes'] else 'no changes'}

Suggested tools: {', '.join(claude_data['suggested_tools'])}
"""
        
        # Add actionable items if any
        if context['actionable_items']:
            text_output += "\nActionable items detected:\n"
            for item in context['actionable_items']:
                text_output += f"- [{item['priority']}] {item['description']} (use: {item['suggested_action']})\n"
                
        return text_output
    
    async def monitor_changes(self, callback: Optional[callable] = None):
        """Monitor for significant changes"""
        
        while True:
            try:
                context = await self.get_vision_context()
                summary = self.adapter.get_context_summary()
                
                if summary.get('stability') == 'changing':
                    if callback:
                        await callback(context, summary)
                    else:
                        print(f"Change detected: {context}")
                        
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(5)


# Example usage for Claude Code
async def claude_vision_example():
    """Example of using vision with Claude Code"""
    
    bridge = ClaudeVisionBridge()
    await bridge.connect()
    
    # Get current context
    context = await bridge.get_vision_context()
    print(context)
    
    # Example: Monitor for changes
    async def on_change(context, summary):
        print(f"Visual change detected!")
        print(f"Recent changes: {summary['recent_changes']}")
        print(f"Context: {context}")
        
    # Start monitoring
    await bridge.monitor_changes(callback=on_change)


if __name__ == "__main__":
    asyncio.run(claude_vision_example())