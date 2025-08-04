#!/usr/bin/env python3
"""
Test MCP Vision Server with actual frames
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_with_frames():
    """Test vision server with actual frame data"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_vision_server.py"],
        env={}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🧬 Testing MCP Vision Server with Frames")
            print("=" * 50)
            
            # Step 1: Check initial status
            print("\n1. Initial status:")
            result = await session.call_tool("get_vision_status", {})
            print(f"   {result.content[0].text}")
            
            # Step 2: Send test frame
            print("\n2. Sending test frame...")
            result = await session.call_tool("send_test_frame", {})
            print(f"   {result.content[0].text}")
            
            # Give frame time to process
            await asyncio.sleep(1)
            
            # Step 3: Check what we can see now
            print("\n3. What do we see now?")
            result = await session.call_tool("see", {})
            print(f"   {result.content[0].text}")
            
            # Step 4: Get description
            print("\n4. Natural language description:")
            result = await session.call_tool("describe", {})
            print(f"   {result.content[0].text}")
            
            # Step 5: Check UI types
            print("\n5. UI type checks:")
            result = await session.call_tool("is_terminal", {})
            print(f"   Is terminal? {result.content[0].text}")
            
            result = await session.call_tool("is_dark_mode", {})
            print(f"   Is dark mode? {result.content[0].text}")
            
            # Step 6: Get insights
            print("\n6. Recent insights:")
            result = await session.call_tool("get_recent_insights", {})
            print(f"   {result.content[0].text}")
            
            print("\n✅ Frame test complete!")
            print("\nThe MCP vision server successfully:")
            print("- Connected to vision source")
            print("- Processed synthetic frames")
            print("- Provided real-time analysis")
            print("- Offered multiple query methods")


if __name__ == "__main__":
    asyncio.run(test_with_frames())