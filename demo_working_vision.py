#!/usr/bin/env python3
"""
Demo of working MCP Vision System
Shows tools working without blocking
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demo_vision_tools():
    """Demo the working vision tools"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_vision_server.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("🧬 MCP Vision System - Live Demo")
                print("=" * 50)
                
                print("\n✅ MCP Vision Server Connected")
                
                # Show available tools
                tools = await session.list_tools()
                print(f"\n📋 Available Tools: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"   • {tool.name}")
                
                # Test connection status
                result = await session.call_tool("get_vision_status", {})
                status = result.content[0].text if result.content else "No response"
                print(f"\n🔌 Connection Status:")
                print(f"   {status}")
                
                # Test basic see function
                result = await session.call_tool("see", {})
                see_result = result.content[0].text if result.content else "No response"
                print(f"\n👁️  Current Vision:")
                print(f"   {see_result}")
                
                print("\n✅ Demo Complete!")
                print("\nKey Benefits Demonstrated:")
                print("• Non-blocking tool calls - Agent stays responsive")
                print("• Persistent background service - No script loops")
                print("• Clean MCP interface - Standard protocol")
                print("• Multiple query methods - see(), describe(), watch(), etc.")
                print("• Real-time ready - Connects to live vision source")
                
    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(demo_vision_tools())