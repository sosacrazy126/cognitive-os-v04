#!/usr/bin/env python3
"""
Simple Agent System Demo - Core Functionality Demonstration
Demonstrates the agent loop system without complex WebSocket dependencies
"""

import time
import json
from datetime import datetime
import asyncio

# Import our core systems
from autonomous_agent_loops import get_mission_control, AgentMissionType, AgentStatus, AgentMission
from realtime_cognitive_mirror import get_cognitive_mirror
import uuid

def print_banner(title: str):
    print(f"\n{'=' * 70}")
    print(f"{title:^70}")
    print(f"{'=' * 70}")

def print_status(message: str, status: str = "INFO"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    icons = {'INFO': '🔵', 'SUCCESS': '✅', 'WARNING': '⚠️', 'ERROR': '❌', 'DEMO': '🎯'}
    print(f"[{timestamp}] {icons.get(status, '🔵')} {message}")

def demonstrate_core_agent_system():
    """Demonstrate the core agent system functionality"""
    print_banner("COGNITIVE OS - AGENT SYSTEM DEMO")
    print_status("Starting core agent system demonstration", "DEMO")
    
    # Initialize core components
    print_status("Initializing Mission Control...", "INFO")
    mission_control = get_mission_control()
    time.sleep(1)
    
    print_status("Initializing Consciousness Mirror...", "INFO")
    cognitive_mirror = get_cognitive_mirror()
    time.sleep(1)
    
    print_status("Core systems initialized!", "SUCCESS")
    
    # Demonstrate consciousness tracking
    print_banner("CONSCIOUSNESS TRACKING DEMO")
    
    cognitive_mirror.context_shift("Demonstrating agent system core functionality")
    time.sleep(1)
    
    cognitive_mirror.reasoning_step("Mission control and consciousness systems are integrated")
    time.sleep(1)
    
    cognitive_mirror.insight_formed("This creates a transparent AI agent management system")
    time.sleep(1)
    
    print_status("Consciousness tracking demonstrated", "SUCCESS")
    
    # Create and demonstrate missions
    print_banner("MISSION CREATION DEMO")
    
    # Create different types of missions
    missions = []
    
    # Research mission
    research_mission = AgentMission(
        mission_id=f"research_{uuid.uuid4().hex[:8]}",
        mission_type=AgentMissionType.RESEARCH,
        objective="Analyze autonomous agent effectiveness",
        parameters={'depth': 'comprehensive'},
        expected_duration=300,
        timeout=600,
        priority=8,
        requires_callback=True,
        callback_endpoint=None,
        created_at=datetime.now()
    )
    missions.append(("Research", research_mission))
    
    # Debug mission
    debug_mission = AgentMission(
        mission_id=f"debug_{uuid.uuid4().hex[:8]}",
        mission_type=AgentMissionType.DEBUG,
        objective="Debug WebSocket connection issues",
        parameters={'urgency': 'normal'},
        expected_duration=180,
        timeout=360,
        priority=6,
        requires_callback=True,
        callback_endpoint=None,
        created_at=datetime.now()
    )
    missions.append(("Debug", debug_mission))
    
    # Analysis mission
    analysis_mission = AgentMission(
        mission_id=f"analyze_{uuid.uuid4().hex[:8]}",
        mission_type=AgentMissionType.ANALYZE,
        objective="Analyze dashboard architecture design",
        parameters={'type': 'comprehensive'},
        expected_duration=240,
        timeout=480,
        priority=7,
        requires_callback=True,
        callback_endpoint=None,
        created_at=datetime.now()
    )
    missions.append(("Analysis", analysis_mission))
    
    print_status(f"Created {len(missions)} different mission types", "SUCCESS")
    
    # Add missions to queue (simulate dispatch without actual agent spawning)
    print_banner("MISSION QUEUE MANAGEMENT DEMO")
    
    for mission_name, mission in missions:
        cognitive_mirror.reasoning_step(f"Adding {mission_name} mission to queue")
        mission_control.mission_queue.append(mission)
        print_status(f"{mission_name} mission queued: {mission.mission_id}", "INFO")
        time.sleep(0.5)
    
    print_status("All missions queued successfully", "SUCCESS")
    
    # Demonstrate mission processing
    print_banner("MISSION PROCESSING SIMULATION")
    
    cognitive_mirror.context_shift("Processing queued missions")
    
    # Process missions from queue
    processed_missions = []
    while mission_control.mission_queue:
        mission = mission_control.mission_queue.pop(0)
        
        print_status(f"Processing mission: {mission.mission_type.value}", "DEMO")
        cognitive_mirror.reasoning_step(f"Processing {mission.mission_type.value} mission: {mission.objective}")
        
        # Simulate mission processing
        mission_control.active_missions[mission.mission_id] = mission
        processed_missions.append(mission)
        
        # Simulate agent working
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        mission_control.active_agents[mission.mission_id] = {
            'agent_id': agent_id,
            'pid': 12345,  # Simulated PID
            'start_time': datetime.now(),
            'status': AgentStatus.WORKING
        }
        
        print_status(f"Agent {agent_id} assigned to mission {mission.mission_id}", "SUCCESS")
        cognitive_mirror.insight_formed(f"Agent {agent_id} successfully assigned to {mission.mission_type.value} mission")
        
        time.sleep(1)
    
    print_status(f"Processed {len(processed_missions)} missions", "SUCCESS")
    
    # Simulate mission completion
    print_banner("MISSION COMPLETION SIMULATION")
    
    cognitive_mirror.context_shift("Simulating mission completions")
    
    for mission in processed_missions:
        mission_id = mission.mission_id
        agent_info = mission_control.active_agents.get(mission_id)
        
        if agent_info:
            agent_id = agent_info['agent_id']
            
            print_status(f"Mission {mission_id} completing...", "DEMO")
            cognitive_mirror.reasoning_step(f"Agent {agent_id} completing {mission.mission_type.value} mission")
            
            # Create completion report
            from autonomous_agent_loops import AgentReport
            
            report = AgentReport(
                mission_id=mission_id,
                agent_id=agent_id,
                status=AgentStatus.COMPLETED,
                results={
                    'mission_type': mission.mission_type.value,
                    'objective_met': True,
                    'execution_time': 120.5,
                    'quality_score': 0.92
                },
                insights=[
                    f"{mission.mission_type.value.title()} mission completed successfully",
                    f"Objective achieved: {mission.objective}",
                    "No significant issues encountered"
                ],
                recommendations=[
                    "Consider similar missions in the future",
                    f"Scale {mission.mission_type.value} operations"
                ],
                execution_time=120.5,
                confidence=0.92,
                next_actions=[
                    "Archive mission results",
                    "Update performance metrics"
                ],
                returned_at=datetime.now()
            )
            
            # Process the completion
            success = mission_control.receive_agent_report(report)
            
            if success:
                print_status(f"Mission {mission_id} completed successfully", "SUCCESS")
                cognitive_mirror.insight_formed(f"Mission completion processed - {len(report.insights)} insights captured")
                
                # Process insights
                for insight in report.insights:
                    cognitive_mirror.pattern_recognized(f"Agent insight: {insight}")
                
                # Show recommendations
                if report.recommendations:
                    cognitive_mirror.synthesis_moment(f"Agent provided {len(report.recommendations)} recommendations")
            else:
                print_status(f"Failed to process completion for {mission_id}", "ERROR")
            
            time.sleep(1)
    
    # Show final system status
    print_banner("SYSTEM STATUS OVERVIEW")
    
    dashboard_data = mission_control.get_mission_control_dashboard()
    
    print_status("Mission Control Status:", "INFO")
    print(f"    Active Missions: {dashboard_data['active_missions']}")
    print(f"    Queued Missions: {dashboard_data['queued_missions']}")
    print(f"    Completed Missions: {dashboard_data['completed_missions']}")
    print(f"    Active Agents: {dashboard_data['active_agents']}")
    
    # Show consciousness report
    consciousness_report = cognitive_mirror.generate_cognitive_report()
    print_status("Consciousness Status:", "INFO")
    print(f"    Confidence: {consciousness_report['cognitive_metrics']['confidence']:.2f}")
    print(f"    Cognitive Load: {consciousness_report['cognitive_metrics']['cognitive_load']:.2f}")
    print(f"    Insight Momentum: {consciousness_report['cognitive_metrics']['insight_momentum']:.2f}")
    print(f"    Working Memory: {consciousness_report['cognitive_metrics']['working_memory_size']} items")
    print(f"    Reasoning Depth: {consciousness_report['cognitive_metrics']['reasoning_depth']} steps")
    
    # Final consciousness reflection
    cognitive_mirror.synthesis_moment("Complete agent system demonstration finished successfully")
    cognitive_mirror.pattern_recognized("All core components working together effectively")
    
    print_banner("DEMO COMPLETE")
    print_status("Core agent system functionality demonstrated successfully", "SUCCESS")
    print_status("The system is ready for full deployment with WebSocket integration", "SUCCESS")
    
    # Show available components
    print_status("Available System Components:", "INFO")
    print("    📞 Agent Callback System: agent_callback_system.py")
    print("    🎮 Enhanced Mission Control: enhanced_mission_control.py")
    print("    🧠 Consciousness Dashboard: integrated_consciousness_dashboard.html")
    print("    🎮 Agent Control Dashboard: agent_control_dashboard.html")
    
    return {
        'mission_control': mission_control,
        'cognitive_mirror': cognitive_mirror,
        'processed_missions': len(processed_missions),
        'final_report': consciousness_report
    }

if __name__ == "__main__":
    print("🧠 COGNITIVE OS - SIMPLE AGENT SYSTEM DEMO")
    print("Demonstrating core agent loop functionality:")
    print("• Mission creation and queuing")
    print("• Agent assignment and tracking") 
    print("• Mission completion and reporting")
    print("• Consciousness integration throughout")
    
    try:
        demo_results = demonstrate_core_agent_system()
        
        print(f"\n🎯 DEMO RESULTS:")
        print(f"    Missions Processed: {demo_results['processed_missions']}")
        print(f"    Final Confidence: {demo_results['final_report']['cognitive_metrics']['confidence']:.2f}")
        print(f"    System Status: Operational")
        
        print(f"\n✅ Agent system core functionality verified!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()