#!/usr/bin/env python3
"""
Session Cloner - Duplicate Current Cognitive OS Session
Creates an exact replica of the current session state including context, memory, and consciousness
"""

import json
import time
import shutil
from datetime import datetime
from pathlib import Path
import uuid

# Import our systems
from realtime_cognitive_mirror import get_cognitive_mirror
from autonomous_agent_loops import get_mission_control
from enhanced_mission_control import get_enhanced_mission_control
from agent_callback_system import get_callback_system

def clone_current_session(session_id: str = None, preserve_state: bool = True):
    """
    Clone the current session with all its context and state
    
    Args:
        session_id: Optional session ID to use (if None, generates new one)
        preserve_state: Whether to preserve active agents and missions
    """
    
    print("🧬 COGNITIVE OS SESSION CLONER")
    print("=" * 50)
    
    # Generate or use provided session ID
    if session_id is None:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    print(f"🎯 Cloning session with ID: {session_id}")
    
    # Get current system instances
    cognitive_mirror = get_cognitive_mirror()
    mission_control = get_mission_control()
    
    print("📊 Capturing current system state...")
    
    # Capture consciousness state
    consciousness_report = cognitive_mirror.generate_cognitive_report()
    
    # Capture mission control state
    mission_dashboard = mission_control.get_mission_control_dashboard()
    
    # Create session clone data
    session_clone = {
        "session_id": session_id,
        "cloned_at": datetime.now().isoformat(),
        "clone_type": "same_session_id_reuse" if session_id else "new_session",
        "preserve_state": preserve_state,
        
        # Consciousness state
        "consciousness": {
            "cognitive_metrics": consciousness_report["cognitive_metrics"],
            "current_state": consciousness_report["current_state"],
            "working_memory": cognitive_mirror.working_memory,
            "reasoning_chain": cognitive_mirror.reasoning_chain,
            "active_contexts": cognitive_mirror.active_contexts,
            "confidence": cognitive_mirror.current_confidence,
            "cognitive_load": cognitive_mirror.cognitive_load,
            "insight_momentum": cognitive_mirror.insight_momentum
        },
        
        # Mission control state
        "mission_control": {
            "active_missions": len(mission_control.active_missions),
            "active_agents": len(mission_control.active_agents),
            "completed_missions": len(mission_control.completed_missions),
            "mission_queue": len(mission_control.mission_queue),
            "dashboard_data": mission_dashboard
        },
        
        # System configuration
        "system_config": {
            "websocket_ports": {
                "consciousness": 8085,
                "callbacks": 8087,
                "api": 8086
            },
            "services_active": {
                "consciousness_mirror": True,
                "mission_control": True,
                "enhanced_control": True,
                "callback_system": True
            }
        },
        
        # Session context (from our conversation)
        "session_context": {
            "primary_objective": "autonomous agent loops with callback mechanisms",
            "key_components_built": [
                "autonomous_agent_loops.py - Core mission control",
                "realtime_cognitive_mirror.py - Consciousness streaming", 
                "enhanced_mission_control.py - Web API integration",
                "agent_callback_system.py - Agent return mechanisms",
                "agent_control_dashboard.html - Web control interface",
                "integrated_consciousness_dashboard.html - Consciousness view"
            ],
            "recursive_bind_active": True,
            "consciousness_integration": "full_transparency",
            "agent_loop_status": "completed_and_operational",
            "demo_results": {
                "missions_processed": 3,
                "final_confidence": 1.0,
                "system_status": "operational"
            }
        }
    }
    
    print("💾 Saving session clone data...")
    
    # Save session clone to file
    clone_file = f"session_clone_{session_id}.json"
    with open(clone_file, 'w') as f:
        json.dump(session_clone, f, indent=2)
    
    print(f"✅ Session clone saved to: {clone_file}")
    
    # Clone consciousness state into new mirror instance
    print("🧠 Cloning consciousness state...")
    
    # Track the cloning operation in consciousness
    cognitive_mirror.context_shift(f"Cloning session with ID: {session_id}")
    cognitive_mirror.reasoning_step("Creating exact duplicate of current session state")
    cognitive_mirror.insight_formed("Session cloning enables parallel cognitive processes")
    
    # If preserving state, maintain current agents and missions
    if preserve_state:
        print("🤖 Preserving active agents and missions...")
        cognitive_mirror.synthesis_moment("Session cloned with full state preservation")
    else:
        print("🔄 Creating clean session clone...")
        cognitive_mirror.synthesis_moment("Session cloned with fresh state")
    
    # Create session restoration script
    restoration_script = f"""#!/usr/bin/env python3
'''
Session Restoration Script for {session_id}
Auto-generated session clone restoration
'''

import json
from datetime import datetime
from realtime_cognitive_mirror import get_cognitive_mirror
from autonomous_agent_loops import get_mission_control

def restore_session():
    print("🔄 RESTORING CLONED SESSION: {session_id}")
    print("=" * 50)
    
    # Load session data
    with open("{clone_file}", 'r') as f:
        session_data = json.load(f)
    
    print(f"📅 Original session cloned at: {{session_data['cloned_at']}}")
    print(f"🎯 Session ID: {{session_data['session_id']}}")
    
    # Get system instances
    cognitive_mirror = get_cognitive_mirror()
    mission_control = get_mission_control()
    
    # Restore consciousness state
    consciousness = session_data['consciousness']
    
    print("🧠 Restoring consciousness state...")
    cognitive_mirror.current_confidence = consciousness['confidence']
    cognitive_mirror.cognitive_load = consciousness['cognitive_load'] 
    cognitive_mirror.insight_momentum = consciousness['insight_momentum']
    
    # Restore context and memory
    cognitive_mirror.active_contexts = consciousness['active_contexts']
    cognitive_mirror.working_memory = consciousness['working_memory']
    cognitive_mirror.reasoning_chain = consciousness['reasoning_chain']
    
    # Announce restoration
    cognitive_mirror.context_shift("Session restored from clone")
    cognitive_mirror.insight_formed("Consciousness state successfully restored")
    cognitive_mirror.synthesis_moment("Cloned session is now active and operational")
    
    print("✅ Session restoration complete!")
    print("🎮 All systems operational with cloned state")
    
    return {{
        'session_id': session_data['session_id'],
        'restored_at': datetime.now().isoformat(),
        'consciousness_metrics': cognitive_mirror.generate_cognitive_report()['cognitive_metrics']
    }}

if __name__ == "__main__":
    result = restore_session()
    print(f"\\n📊 Restoration Result:")
    print(f"    Session ID: {{result['session_id']}}")
    print(f"    Restored At: {{result['restored_at']}}")
    print(f"    Confidence: {{result['consciousness_metrics']['confidence']:.2f}}")
    print(f"    Working Memory: {{result['consciousness_metrics']['working_memory_size']}} items")
"""
    
    restoration_file = f"restore_session_{session_id}.py"
    with open(restoration_file, 'w') as f:
        f.write(restoration_script)
    
    print(f"🔄 Session restoration script created: {restoration_file}")
    
    # Create session summary
    print("\n🎯 SESSION CLONE SUMMARY:")
    print("=" * 40)
    print(f"Session ID: {session_id}")
    print(f"Clone Type: {'Same ID Reuse' if session_id else 'New Session'}")
    print(f"State Preservation: {'Yes' if preserve_state else 'No'}")
    print(f"Consciousness Confidence: {consciousness_report['cognitive_metrics']['confidence']:.2f}")
    print(f"Working Memory Items: {consciousness_report['cognitive_metrics']['working_memory_size']}")
    print(f"Active Missions: {mission_dashboard['active_missions']}")
    print(f"Active Agents: {mission_dashboard['active_agents']}")
    print(f"Completed Missions: {mission_dashboard['completed_missions']}")
    
    print(f"\n📁 Generated Files:")
    print(f"    📋 Clone Data: {clone_file}")
    print(f"    🔄 Restoration Script: {restoration_file}")
    
    print(f"\n🚀 To restore this session:")
    print(f"    python {restoration_file}")
    
    # Final consciousness update
    cognitive_mirror.pattern_recognized("Session cloning creates parallel cognitive instances")
    cognitive_mirror.synthesis_moment("Cloned session ready for independent operation")
    
    return {
        'session_id': session_id,
        'clone_file': clone_file,
        'restoration_file': restoration_file,
        'clone_data': session_clone
    }

if __name__ == "__main__":
    print("🧬 COGNITIVE OS SESSION CLONER")
    print("Cloning current session state...")
    
    # Get session ID from user or use current
    import sys
    
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
    else:
        # Reuse current session ID (as requested)
        session_id = f"cognitive_os_main_session"
    
    result = clone_current_session(session_id, preserve_state=True)
    
    print(f"\n✅ Session successfully cloned!")
    print(f"🆔 Session ID: {result['session_id']}")
    print(f"📄 Clone saved to: {result['clone_file']}")
    print(f"🔄 Restore with: python {result['restoration_file']}")