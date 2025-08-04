#!/usr/bin/env python3
"""
MCP Vision Server - Real-time screen vision as a persistent background service
Provides tools for CLI agents to see and analyze screen content without blocking
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from PIL import Image
import io
import numpy as np
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state for vision analysis
@dataclass
class VisionState:
    """Current vision state"""
    latest_frame: Optional[Dict[str, Any]] = None
    analysis_history: List[Dict[str, Any]] = field(default_factory=list)
    frame_count: int = 0
    last_update: Optional[str] = None
    ws_connection: Optional[websockets.WebSocketClientProtocol] = None
    ws_url: str = "ws://localhost:8766"
    is_connected: bool = False
    background_task: Optional[asyncio.Task] = None


# Singleton state
vision_state = VisionState()


async def connect_to_vision_source():
    """Connect to vision WebSocket source"""
    try:
        vision_state.ws_connection = await websockets.connect(vision_state.ws_url)
        vision_state.is_connected = True
        logger.info(f"Connected to vision source at {vision_state.ws_url}")
        
        # Get initial handshake
        handshake = await vision_state.ws_connection.recv()
        logger.info(f"Vision source: {json.loads(handshake)}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to connect to vision source: {e}")
        vision_state.is_connected = False
        return False


async def vision_receiver_loop():
    """Background task to receive and process vision frames"""
    while True:
        try:
            if not vision_state.is_connected:
                if not await connect_to_vision_source():
                    await asyncio.sleep(5)  # Retry connection
                    continue
            
            # Receive frames
            message = await vision_state.ws_connection.recv()
            data = json.loads(message)
            
            if data.get('type') == 'live_analysis':
                # Store analysis
                analysis = data['analysis']
                vision_state.latest_frame = analysis
                vision_state.frame_count = analysis.get('frame_id', vision_state.frame_count)
                vision_state.last_update = datetime.now(UTC).isoformat()
                
                # Update history
                vision_state.analysis_history.append(analysis)
                if len(vision_state.analysis_history) > 10:
                    vision_state.analysis_history.pop(0)
                
                logger.debug(f"Frame {vision_state.frame_count}: {analysis.get('detected_ui_type')}")
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Vision source connection closed")
            vision_state.is_connected = False
            vision_state.ws_connection = None
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Vision receiver error: {e}")
            await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(_server) -> AsyncIterator[dict]:
    """Manage server lifecycle"""
    logger.info("Starting vision receiver background task")
    vision_state.background_task = asyncio.create_task(vision_receiver_loop())
    
    try:
        yield {}
    finally:
        logger.info("Shutting down vision server")
        if vision_state.background_task:
            vision_state.background_task.cancel()
        if vision_state.ws_connection:
            await vision_state.ws_connection.close()

# Create MCP server with lifespan
mcp = FastMCP("Vision Server", lifespan=lifespan)


# Vision Tools

@mcp.tool()
def see() -> Dict[str, Any]:
    """
    See what's currently on screen
    Returns immediate analysis of current screen content
    """
    if not vision_state.latest_frame:
        return {
            "error": "No vision data available",
            "ui_type": "unknown",
            "hint": "Make sure screen sharing is active"
        }
    
    frame = vision_state.latest_frame
    return {
        "ui_type": frame.get("detected_ui_type", "unknown"),
        "description": _describe_frame(frame),
        "brightness": frame.get("brightness", 0),
        "is_dark": frame.get("is_dark", False),
        "insights": frame.get("insights", []),
        "confidence": frame.get("confidence", 0),
        "last_update": vision_state.last_update,
        "frame_id": frame.get("frame_id", 0)
    }


@mcp.tool()
def describe() -> str:
    """
    Get a natural language description of current screen
    Returns a single descriptive sentence
    """
    if not vision_state.latest_frame:
        return "Cannot see screen - no vision data available"
    
    return _describe_frame(vision_state.latest_frame)


@mcp.tool()
def watch_for_changes(duration: int = 5) -> List[Dict[str, Any]]:
    """
    Watch screen for changes over specified duration
    Returns list of significant changes detected
    
    Args:
        duration: How many seconds to watch (max 30)
    """
    if duration > 30:
        duration = 30
        
    # Get starting state
    start_frame = vision_state.latest_frame
    if not start_frame:
        return [{"error": "No vision data available"}]
    
    start_ui = start_frame.get("detected_ui_type")
    start_frame_id = vision_state.frame_count
    changes = []
    
    # Record initial state
    initial_history_len = len(vision_state.analysis_history)
    
    # Sleep for duration
    import time
    time.sleep(duration)
    
    # Check what changed
    end_frame_id = vision_state.frame_count
    
    if end_frame_id > start_frame_id:
        # Analyze frames that occurred during watch period
        new_frames = vision_state.analysis_history[initial_history_len:]
        
        last_ui = start_ui
        for frame in new_frames:
            current_ui = frame.get("detected_ui_type")
            
            # UI type change
            if current_ui != last_ui:
                changes.append({
                    "type": "ui_change",
                    "from": last_ui,
                    "to": current_ui,
                    "frame_id": frame.get("frame_id"),
                    "insights": frame.get("insights", [])
                })
                last_ui = current_ui
            
            # Significant insights
            for insight in frame.get("insights", []):
                if any(keyword in insight.lower() for keyword in ["detected", "changed", "switch"]):
                    changes.append({
                        "type": "insight",
                        "message": insight,
                        "ui_type": current_ui,
                        "frame_id": frame.get("frame_id")
                    })
    
    return changes if changes else [{"message": f"No changes detected in {duration} seconds"}]


@mcp.tool()
def get_vision_status() -> Dict[str, Any]:
    """
    Get current vision system status
    Returns connection status and statistics
    """
    return {
        "connected": vision_state.is_connected,
        "ws_url": vision_state.ws_url,
        "frame_count": vision_state.frame_count,
        "last_update": vision_state.last_update,
        "history_size": len(vision_state.analysis_history),
        "current_ui": vision_state.latest_frame.get("detected_ui_type") if vision_state.latest_frame else "unknown"
    }


@mcp.tool()
def is_terminal() -> bool:
    """Check if current screen shows a terminal"""
    if not vision_state.latest_frame:
        return False
    return vision_state.latest_frame.get("detected_ui_type") == "terminal"


@mcp.tool()
def is_browser() -> bool:
    """Check if current screen shows a browser"""
    if not vision_state.latest_frame:
        return False
    return vision_state.latest_frame.get("detected_ui_type") == "browser"


@mcp.tool()
def is_dark_mode() -> bool:
    """Check if screen is in dark mode"""
    if not vision_state.latest_frame:
        return False
    return vision_state.latest_frame.get("is_dark", False)


@mcp.tool()
def get_recent_insights() -> List[str]:
    """
    Get recent insights from vision analysis
    Returns actionable insights from recent frames
    """
    insights = []
    
    for frame in vision_state.analysis_history[-5:]:
        for insight in frame.get("insights", []):
            if insight not in insights:
                insights.append(insight)
    
    return insights


@mcp.tool()
async def send_test_frame(ctx: Context) -> Dict[str, Any]:
    """
    Send a test frame to vision system (for testing)
    Creates and sends a synthetic terminal frame
    """
    if not vision_state.ws_connection:
        return {"error": "Not connected to vision source"}
    
    try:
        # Create synthetic frame
        img = Image.new('RGB', (800, 600), color=(20, 20, 20))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw terminal-like content
        draw.text((20, 30), "$ Testing MCP vision server", fill=(0, 255, 0))
        draw.text((20, 60), ">>> Vision system active", fill=(0, 255, 0))
        
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
        
        await vision_state.ws_connection.send(json.dumps(frame_msg))
        await ctx.info("Test frame sent")
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        return {"success": True, "message": "Test frame sent"}
        
    except Exception as e:
        return {"error": str(e)}


# Helper functions
def _describe_frame(frame: Dict[str, Any]) -> str:
    """Generate natural language description of frame"""
    ui_type = frame.get("detected_ui_type", "unknown")
    brightness = frame.get("brightness", 0.5)
    is_dark = frame.get("is_dark", False)
    
    descriptions = {
        "terminal": "Terminal or command line interface",
        "browser": "Web browser window", 
        "ide": "Code editor or IDE",
        "dashboard": "Dashboard or monitoring interface",
        "document": "Document or text editor",
        "application": "Desktop application"
    }
    
    base_desc = descriptions.get(ui_type, "Unknown application")
    
    # Add theme info
    if is_dark:
        desc = f"Dark-themed {base_desc.lower()}"
    elif brightness > 0.7:
        desc = f"Light-themed {base_desc.lower()}"
    else:
        desc = base_desc
    
    # Add first insight if available
    if frame.get("insights"):
        first_insight = frame["insights"][0]
        if "monitoring" in first_insight.lower():
            desc += " showing monitoring data"
        elif "editing" in first_insight.lower():
            desc += " with active editing"
        elif "loading" in first_insight.lower():
            desc += " in loading state"
    
    return desc


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()