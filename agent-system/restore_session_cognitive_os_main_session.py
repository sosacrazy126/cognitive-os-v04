#!/usr/bin/env python3
'''
Session Restoration Script for cognitive_os_main_session
Auto-generated session clone restoration
'''

import json
from datetime import datetime
from realtime_cognitive_mirror import get_cognitive_mirror
from autonomous_agent_loops import get_mission_control

def restore_session():
    print("🔄 RESTORING CLONED SESSION: cognitive_os_main_session")
    print("=" * 50)
    
    # Load session data
    with open("session_clone_cognitive_os_main_session.json", 'r') as f:
        session_data = json.load(f)
    
    print(f"📅 Original session cloned at: {session_data['cloned_at']}")
    print(f"🎯 Session ID: {session_data['session_id']}")
    
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
    
    return {
        'session_id': session_data['session_id'],
        'restored_at': datetime.now().isoformat(),
        'consciousness_metrics': cognitive_mirror.generate_cognitive_report()['cognitive_metrics']
    }

if __name__ == "__main__":
    result = restore_session()
    print(f"\n📊 Restoration Result:")
    print(f"    Session ID: {result['session_id']}")
    print(f"    Restored At: {result['restored_at']}")
    print(f"    Confidence: {result['consciousness_metrics']['confidence']:.2f}")
    print(f"    Working Memory: {result['consciousness_metrics']['working_memory_size']} items")
