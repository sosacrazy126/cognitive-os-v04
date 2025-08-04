#!/usr/bin/env python3
"""Vision Pipeline Launcher"""

import asyncio
import sys
from core_vision_stream import create_vision_stream
from vision_tool_interface import CLIAgent
import json

async def main():
    # Load config
    with open('vision_config.json', 'r') as f:
        config = json.load(f)
    
    # Start vision stream
    print("Starting vision stream...")
    stream = create_vision_stream(
        fps=config['vision']['fps'],
        quality=config['vision']['quality']
    )
    
    # Start stream server
    stream_task = asyncio.create_task(
        stream.start_server(port=config['vision']['websocket_port'])
    )
    
    # Wait a moment for server to start
    await asyncio.sleep(1)
    
    # Start CLI agent
    print("Starting CLI agent...")
    agent = CLIAgent(name="vision_cli_agent")
    
    if await agent.initialize():
        print("✓ Agent initialized")
        print(f"Vision stream: ws://localhost:{config['vision']['websocket_port']}")
        print("Press Ctrl+C to stop")
        
        try:
            await agent.think_act_loop()
        except KeyboardInterrupt:
            print("\nShutting down...")
            agent.stop()
            stream.stop()
    else:
        print("✗ Failed to initialize agent")
        stream.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
