#!/usr/bin/env python3
"""
Test the MCP Vision Server
Shows how CLI agents can use vision without blocking
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_vision_tools():
    """Test vision tools through MCP"""
    
    # Connect to MCP vision server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_vision_server.py"],
        env={}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            print("🧬 MCP Vision Server Test")
            print("=" * 50)
            
            # List available tools
            tools = await session.list_tools()
            print("\nAvailable vision tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test 1: Get vision status
            print("\n1. Testing get_vision_status:")
            result = await session.call_tool("get_vision_status", {})
            print(f"   Status: {result.content[0].text}")
            
            # Test 2: See current screen
            print("\n2. Testing see:")
            result = await session.call_tool("see", {})
            print(f"   Result: {result.content[0].text}")
            
            # Test 3: Get description
            print("\n3. Testing describe:")
            result = await session.call_tool("describe", {})
            print(f"   Description: {result.content[0].text}")
            
            # Test 4: Check UI type
            print("\n4. Testing UI type checks:")
            
            result = await session.call_tool("is_terminal", {})
            print(f"   Is terminal? {result.content[0].text}")
            
            result = await session.call_tool("is_browser", {})
            print(f"   Is browser? {result.content[0].text}")
            
            result = await session.call_tool("is_dark_mode", {})
            print(f"   Is dark mode? {result.content[0].text}")
            
            # Test 5: Watch for changes
            print("\n5. Testing watch_for_changes (3 seconds):")
            result = await session.call_tool("watch_for_changes", {"duration": 3})
            print(f"   Changes: {result.content[0].text}")
            
            print("\n✅ MCP Vision Server test complete!")
            print("\nThis demonstrates how CLI agents can:")
            print("- Call vision tools without blocking")
            print("- Get real-time screen analysis")
            print("- Watch for changes over time")
            print("- All through a persistent background service")


if __name__ == "__main__":
    asyncio.run(test_vision_tools())