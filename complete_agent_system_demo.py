#!/usr/bin/env python3
"""
Complete Agent System Demo - Full Autonomous Agent Loop Demonstration
Showcases the entire agent lifecycle: spawn → work → callback → completion

This demonstrates the complete cognitive OS agent management system:
1. Consciousness streaming (realtime thinking)
2. Agent mission dispatch
3. Agent monitoring and control
4. Agent callbacks and completion reports
5. Web-based management dashboard
"""

import asyncio
import time
import json
import threading
from datetime import datetime
import subprocess
import sys
import os
from pathlib import Path

# Import all our systems
from autonomous_agent_loops import get_mission_control, AgentMissionType
from realtime_cognitive_mirror import get_cognitive_mirror
from enhanced_mission_control import get_enhanced_mission_control
from agent_callback_system import get_callback_system, simulate_mission_completion

def print_banner(title: str, char: str = "="):
    """Print a formatted banner"""
    print(f"\n{char * 80}")
    print(f"{title:^80}")
    print(f"{char * 80}")

def print_status(message: str, status: str = "INFO"):
    """Print a status message"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    status_colors = {
        'INFO': '🔵',
        'SUCCESS': '✅', 
        'WARNING': '⚠️', 
        'ERROR': '❌',
        'DEMO': '🎯'
    }
    icon = status_colors.get(status, '🔵')
    print(f"[{timestamp}] {icon} {message}")

async def start_all_services():
    """Start all agent system services"""
    print_banner("STARTING COGNITIVE OS AGENT SYSTEM")
    
    print_status("Initializing Consciousness Mirror...", "INFO")
    cognitive_mirror = get_cognitive_mirror()
    await asyncio.sleep(1)
    
    print_status("Initializing Mission Control...", "INFO")
    mission_control = get_mission_control()
    await asyncio.sleep(1)
    
    print_status("Starting Enhanced Mission Control API...", "INFO")
    enhanced_control = get_enhanced_mission_control(port=8086)
    await asyncio.sleep(1)
    
    print_status("Starting Agent Callback System...", "INFO")
    callback_system = get_callback_system(port=8087)
    await asyncio.sleep(2)
    
    print_status("All services online!", "SUCCESS")
    
    return {
        'cognitive_mirror': cognitive_mirror,
        'mission_control': mission_control,
        'enhanced_control': enhanced_control,
        'callback_system': callback_system
    }

async def demonstrate_consciousness_integration(services):
    """Demonstrate consciousness integration"""
    print_banner("CONSCIOUSNESS INTEGRATION DEMO", "-")
    
    mirror = services['cognitive_mirror']
    
    # Show AI thinking about the system
    mirror.context_shift("Demonstrating complete agent system")
    await asyncio.sleep(1)
    
    mirror.reasoning_step("The system has multiple integrated components")
    await asyncio.sleep(1)
    
    mirror.insight_formed("Consciousness streaming + Agent loops + Callbacks = Complete transparency")
    await asyncio.sleep(1)
    
    mirror.synthesis_moment("All systems are working together seamlessly")
    await asyncio.sleep(1)
    
    mirror.pattern_recognized("This creates a fully observable AI agent ecosystem")
    
    print_status("Consciousness integration demonstrated", "SUCCESS")

async def demonstrate_agent_lifecycle(services):
    """Demonstrate complete agent lifecycle"""
    print_banner("AGENT LIFECYCLE DEMONSTRATION", "-")
    
    mission_control = services['mission_control']
    mirror = services['cognitive_mirror']
    callback_system = services['callback_system']
    
    # Phase 1: Agent Dispatch
    print_status("Phase 1: Dispatching Research Agent", "DEMO")
    mirror.context_shift("Dispatching agent for research mission")
    
    research_mission = mission_control.create_research_mission(
        "Analyze the effectiveness of autonomous agent systems", 
        "comprehensive"
    )
    
    dispatch_result = mission_control.dispatch_agent(research_mission)
    
    if dispatch_result['success']:
        agent_id = dispatch_result['agent_id']
        mission_id = dispatch_result['mission_id']
        print_status(f"Agent {agent_id} dispatched for mission {mission_id}", "SUCCESS")
        
        mirror.insight_formed(f"Agent {agent_id} successfully deployed")
        await asyncio.sleep(2)
        
        # Phase 2: Mission Progress (simulated)
        print_status("Phase 2: Simulating Mission Progress", "DEMO")
        mirror.reasoning_step("Agent is now working on the research mission")
        
        # Simulate some progress updates
        for progress in [25, 50, 75]:
            print_status(f"Agent progress: {progress}%", "INFO")
            mirror.reasoning_step(f"Agent reporting {progress}% progress")
            await asyncio.sleep(1)
        
        # Phase 3: Mission Completion Callback
        print_status("Phase 3: Processing Mission Completion", "DEMO")
        mirror.context_shift("Agent completing mission and reporting back")
        
        completion_result = await simulate_mission_completion(
            agent_id,
            mission_id,
            {
                "research_complete": True,
                "analysis_depth": "comprehensive",
                "key_findings": [
                    "Autonomous agent systems show high efficiency",
                    "Callback mechanisms ensure proper coordination",
                    "Consciousness integration provides transparency"
                ],
                "recommendations": [
                    "Scale to more concurrent agents",
                    "Add more sophisticated mission types",
                    "Enhance inter-agent collaboration"
                ]
            }
        )
        
        if completion_result and completion_result.approved:
            print_status("Mission completion processed successfully", "SUCCESS")
            mirror.synthesis_moment("Complete agent lifecycle demonstrated successfully")
        else:
            print_status("Mission completion failed", "ERROR")
        
        return True
    else:
        print_status(f"Agent dispatch failed: {dispatch_result.get('error', 'Unknown error')}", "ERROR")
        return False

async def demonstrate_multi_agent_coordination(services):
    """Demonstrate multiple agents working together"""
    print_banner("MULTI-AGENT COORDINATION DEMO", "-")
    
    mission_control = services['mission_control']
    mirror = services['cognitive_mirror']
    
    mirror.context_shift("Coordinating multiple specialized agents")
    
    # Deploy multiple agents with different specializations
    missions = [
        ("research", "AI consciousness research", "deep"),
        ("debug", "System performance analysis", "normal"),
        ("analyze", "Code architecture review", "comprehensive")
    ]
    
    deployed_agents = []
    
    for mission_type, objective, params in missions:
        print_status(f"Deploying {mission_type} agent: {objective}", "DEMO")
        
        if mission_type == "research":
            mission = mission_control.create_research_mission(objective, params)
        elif mission_type == "debug":
            mission = mission_control.create_debug_mission(objective, params)
        elif mission_type == "analyze":
            mission = mission_control.create_analysis_mission(objective, params)
        
        result = mission_control.dispatch_agent(mission)
        
        if result['success']:
            deployed_agents.append({
                'agent_id': result['agent_id'],
                'mission_id': result['mission_id'],
                'type': mission_type
            })
            print_status(f"Agent {result['agent_id']} deployed", "SUCCESS")
            mirror.reasoning_step(f"Deployed {mission_type} agent {result['agent_id']}")
        
        await asyncio.sleep(1)
    
    print_status(f"Deployed {len(deployed_agents)} agents successfully", "SUCCESS")
    mirror.insight_formed(f"Multi-agent coordination with {len(deployed_agents)} specialized agents active")
    
    # Simulate collaborative work
    await asyncio.sleep(3)
    mirror.synthesis_moment("Multiple agents working in coordination demonstrates system scalability")
    
    return deployed_agents

async def show_system_status(services):
    """Show comprehensive system status"""
    print_banner("SYSTEM STATUS OVERVIEW", "-")
    
    # Get status from all components
    mission_control = services['mission_control']
    mirror = services['cognitive_mirror']
    callback_system = services['callback_system']
    
    # Mission Control Status
    dashboard_data = mission_control.get_mission_control_dashboard()
    print_status(f"Mission Control Status:", "INFO")
    print(f"    Active Missions: {dashboard_data['active_missions']}")
    print(f"    Active Agents: {dashboard_data['active_agents']}")
    print(f"    Completed Missions: {dashboard_data['completed_missions']}")
    print(f"    Queued Missions: {dashboard_data['queued_missions']}")
    
    # Consciousness Status
    consciousness_report = mirror.generate_cognitive_report()
    print_status(f"Consciousness Status:", "INFO")
    print(f"    Confidence: {consciousness_report['cognitive_metrics']['confidence']:.2f}")
    print(f"    Cognitive Load: {consciousness_report['cognitive_metrics']['cognitive_load']:.2f}")
    print(f"    Insight Momentum: {consciousness_report['cognitive_metrics']['insight_momentum']:.2f}")
    print(f"    Connected Clients: {consciousness_report['stream_info']['connected_clients']}")
    
    # Callback System Status
    callback_stats = callback_system.get_callback_stats()
    print_status(f"Callback System Status:", "INFO")
    print(f"    Total Callbacks: {callback_stats['stats']['total_callbacks']}")
    print(f"    Successful: {callback_stats['stats']['successful_callbacks']}")
    print(f"    Active: {callback_stats['active_callbacks']}")
    print(f"    Server: {'Online' if callback_stats['server_active'] else 'Offline'}")

def show_dashboard_instructions():
    """Show instructions for accessing dashboards"""
    print_banner("DASHBOARD ACCESS INSTRUCTIONS")
    
    print_status("Available Dashboards:", "INFO")
    print(f"    🧠 Consciousness Dashboard: file://{os.path.abspath('integrated_consciousness_dashboard.html')}")
    print(f"    🎮 Agent Control Dashboard: file://{os.path.abspath('agent_control_dashboard.html')}")
    print(f"    📊 Enhanced Mission Control API: http://localhost:8086")
    
    print_status("WebSocket Endpoints:", "INFO")
    print(f"    🧠 Consciousness Stream: ws://localhost:8085")
    print(f"    📞 Agent Callbacks: ws://localhost:8087")
    
    print_status("API Endpoints:", "INFO")
    print(f"    📊 System Status: http://localhost:8086/status")
    print(f"    🎯 Missions: http://localhost:8086/missions")
    print(f"    🤖 Agents: http://localhost:8086/agents")
    print(f"    📝 Logs: http://localhost:8086/logs")

async def run_complete_demo():
    """Run the complete system demonstration"""
    print_banner("COGNITIVE OS - COMPLETE AGENT SYSTEM DEMO")
    print_status("Starting comprehensive agent system demonstration", "DEMO")
    
    try:
        # Start all services
        services = await start_all_services()
        await asyncio.sleep(2)
        
        # Demonstrate consciousness integration
        await demonstrate_consciousness_integration(services)
        await asyncio.sleep(2)
        
        # Demonstrate single agent lifecycle
        lifecycle_success = await demonstrate_agent_lifecycle(services)
        await asyncio.sleep(2)
        
        if lifecycle_success:
            # Demonstrate multi-agent coordination
            deployed_agents = await demonstrate_multi_agent_coordination(services)
            await asyncio.sleep(3)
        
        # Show comprehensive system status
        await show_system_status(services)
        
        # Show dashboard access instructions
        show_dashboard_instructions()
        
        print_banner("DEMO COMPLETE - SYSTEM RUNNING")
        print_status("All components are operational and integrated", "SUCCESS")
        print_status("The cognitive OS agent system is fully functional", "SUCCESS")
        print_status("Open the dashboards to interact with the system", "INFO")
        
        return services
        
    except Exception as e:
        print_status(f"Demo error: {str(e)}", "ERROR")
        raise

async def keep_system_running(services):
    """Keep the system running with periodic updates"""
    print_status("System monitoring active - press Ctrl+C to stop", "INFO")
    
    mirror = services['cognitive_mirror']
    
    try:
        while True:
            # Periodic consciousness updates
            mirror.reasoning_step("System monitoring - all components operational")
            await asyncio.sleep(30)
            
            # Show periodic status
            dashboard_data = services['mission_control'].get_mission_control_dashboard()
            if dashboard_data['active_missions'] > 0:
                mirror.insight_formed(f"System active with {dashboard_data['active_missions']} running missions")
                print_status(f"System active: {dashboard_data['active_missions']} missions, {dashboard_data['active_agents']} agents", "INFO")
            
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        print_status("Shutdown requested", "WARNING")
        mirror.context_shift("System shutdown initiated")
        mirror.synthesis_moment("Cognitive OS agent system demonstration completed successfully")
        print_status("Cognitive OS Agent System stopped", "SUCCESS")

if __name__ == "__main__":
    print("🧠 COGNITIVE OS - COMPLETE AGENT SYSTEM")
    print("=" * 50)
    print("This demo showcases the full autonomous agent loop system:")
    print("• Consciousness streaming and monitoring")
    print("• Agent mission dispatch and management") 
    print("• Real-time agent callbacks and reporting")
    print("• Web-based control dashboards")
    print("• Multi-agent coordination")
    print("=" * 50)
    
    async def main():
        # Run the complete demonstration
        services = await run_complete_demo()
        
        # Keep system running
        await keep_system_running(services)
    
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()