#!/usr/bin/env python3
"""
Vision Tools - Direct tool interface for CLI agents
Simple functions that return immediate, actionable information about screen content
"""

import asyncio
import websockets
import json
from typing import Dict, Any, Optional, Tuple
import time

# Global connection pool for efficiency
_vision_connection = None
_last_analysis = None


async def _ensure_connection():
    """Ensure we have an active connection to vision server"""
    global _vision_connection
    
    if _vision_connection and not _vision_connection.closed:
        return _vision_connection
    
    try:
        _vision_connection = await websockets.connect("ws://localhost:8766")
        # Read handshake
        await _vision_connection.recv()
        return _vision_connection
    except Exception as e:
        return None


async def see() -> Dict[str, Any]:
    """
    See what's currently on screen
    Returns immediate analysis of current screen content
    """
    conn = await _ensure_connection()
    if not conn:
        return {"error": "Cannot connect to vision server", "ui_type": "unknown"}
    
    try:
        # Request current state by asking for history (last frame)
        await conn.send(json.dumps({"type": "get_history"}))
        
        response = await asyncio.wait_for(conn.recv(), timeout=1.0)
        data = json.loads(response)
        
        if data['type'] == 'history' and data['analyses']:
            latest = data['analyses'][-1]
            
            # Simplify for CLI consumption
            return {
                "ui_type": latest['detected_ui_type'],
                "description": _describe_screen(latest),
                "insights": latest['insights'],
                "brightness": latest['brightness'],
                "is_dark": latest['is_dark'],
                "confidence": latest['confidence'],
                "timestamp": latest['timestamp']
            }
        
        # Wait for next live analysis
        response = await asyncio.wait_for(conn.recv(), timeout=2.0)
        data = json.loads(response)
        
        if data['type'] == 'live_analysis':
            analysis = data['analysis']
            return {
                "ui_type": analysis['detected_ui_type'],
                "description": _describe_screen(analysis),
                "insights": analysis['insights'],
                "brightness": analysis['brightness'],
                "is_dark": analysis['is_dark'],
                "confidence": analysis['confidence'],
                "timestamp": analysis['timestamp']
            }
            
    except asyncio.TimeoutError:
        return {"error": "No screen data available", "ui_type": "unknown"}
    except Exception as e:
        return {"error": str(e), "ui_type": "unknown"}


async def watch(duration: int = 5) -> list:
    """
    Watch screen for changes over specified duration
    Returns list of significant changes detected
    """
    conn = await _ensure_connection()
    if not conn:
        return [{"error": "Cannot connect to vision server"}]
    
    changes = []
    start_time = time.time()
    last_ui_type = None
    
    try:
        while time.time() - start_time < duration:
            try:
                response = await asyncio.wait_for(conn.recv(), timeout=1.0)
                data = json.loads(response)
                
                if data['type'] == 'live_analysis':
                    analysis = data['analysis']
                    current_ui = analysis['detected_ui_type']
                    
                    # Detect UI change
                    if last_ui_type and last_ui_type != current_ui:
                        changes.append({
                            "time": time.time() - start_time,
                            "change": f"{last_ui_type} → {current_ui}",
                            "insights": analysis['insights']
                        })
                    
                    # Record significant insights
                    for insight in analysis['insights']:
                        if any(word in insight.lower() for word in ['detected', 'changed', 'switch']):
                            changes.append({
                                "time": time.time() - start_time,
                                "change": insight,
                                "ui_type": current_ui
                            })
                    
                    last_ui_type = current_ui
                    
            except asyncio.TimeoutError:
                continue
                
    except Exception as e:
        changes.append({"error": str(e)})
    
    return changes if changes else [{"info": "No changes detected"}]


async def describe() -> str:
    """
    Get a natural language description of current screen
    Returns a single descriptive sentence
    """
    screen_data = await see()
    
    if "error" in screen_data:
        return f"Cannot see screen: {screen_data['error']}"
    
    return screen_data.get("description", "Screen content unclear")


async def is_terminal() -> bool:
    """Check if current screen shows a terminal"""
    screen = await see()
    return screen.get("ui_type") == "terminal"


async def is_browser() -> bool:
    """Check if current screen shows a browser"""
    screen = await see()
    return screen.get("ui_type") == "browser"


async def is_ide() -> bool:
    """Check if current screen shows an IDE"""
    screen = await see()
    return screen.get("ui_type") == "ide"


async def is_dark_mode() -> bool:
    """Check if screen is in dark mode"""
    screen = await see()
    return screen.get("is_dark", False)


async def get_insights() -> list:
    """Get current actionable insights about screen content"""
    screen = await see()
    return screen.get("insights", [])


def _describe_screen(analysis: Dict[str, Any]) -> str:
    """Generate natural language description of screen"""
    ui_type = analysis['detected_ui_type']
    brightness = analysis['brightness']
    is_dark = analysis['is_dark']
    
    # Base description
    descriptions = {
        "terminal": "Terminal or command line interface",
        "browser": "Web browser window",
        "ide": "Code editor or IDE",
        "document": "Document or text editor",
        "dashboard": "Dashboard or monitoring interface",
        "application": "Desktop application window"
    }
    
    desc = descriptions.get(ui_type, "Unknown application")
    
    # Add theme info
    if is_dark:
        desc = f"Dark-themed {desc.lower()}"
    elif brightness > 0.7:
        desc = f"Light-themed {desc.lower()}"
    
    # Add state info from insights
    if analysis.get('insights'):
        first_insight = analysis['insights'][0].lower()
        if 'loading' in first_insight:
            desc += " in loading state"
        elif 'monitoring' in first_insight:
            desc += " showing monitoring data"
        elif 'editing' in first_insight:
            desc += " with active editing"
    
    return desc


# Synchronous wrappers for easy CLI use
def see_sync() -> Dict[str, Any]:
    """Synchronous version of see()"""
    return asyncio.run(see())


def describe_sync() -> str:
    """Synchronous version of describe()"""
    return asyncio.run(describe())


def watch_sync(duration: int = 5) -> list:
    """Synchronous version of watch()"""
    return asyncio.run(watch(duration))


# Direct CLI testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "see":
            result = see_sync()
            print(json.dumps(result, indent=2))
            
        elif command == "describe":
            print(describe_sync())
            
        elif command == "watch":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            print(f"Watching for {duration} seconds...")
            changes = watch_sync(duration)
            for change in changes:
                print(json.dumps(change, indent=2))
                
        elif command == "terminal":
            print("Is terminal:", asyncio.run(is_terminal()))
            
        elif command == "dark":
            print("Is dark mode:", asyncio.run(is_dark_mode()))
            
        else:
            print("Commands: see, describe, watch [seconds], terminal, dark")
    else:
        # Interactive demo
        print("🔍 Vision Tools Demo")
        print("Current screen:", describe_sync())
        print("\nDetailed view:")
        print(json.dumps(see_sync(), indent=2))