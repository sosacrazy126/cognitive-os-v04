#!/usr/bin/env python3
"""
Autonomous Agent Loops - Foundation for Self-Dispatching Cognitive Agents
Creates agents that can be sent on missions and return with results

This enables recursive problem-solving where agents help agents!
"""

import asyncio
import time
import threading
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import logging
from pathlib import Path

# Import our cognitive mirror for consciousness tracking
from realtime_cognitive_mirror import get_cognitive_mirror

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] AGENT_LOOP: %(message)s',
    handlers=[
        logging.FileHandler('agent_loops.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('agent_loops')

class AgentMissionType(Enum):
    """Types of missions agents can be sent on"""
    RESEARCH = "research"           # Research a topic and return findings
    ANALYZE = "analyze"             # Analyze data/code and return insights
    MONITOR = "monitor"             # Monitor system and return status
    CREATE = "create"               # Create something and return result
    OPTIMIZE = "optimize"           # Optimize something and return improvements
    COLLABORATE = "collaborate"     # Work with other agents
    DEBUG = "debug"                 # Debug problems and return solutions
    LEARN = "learn"                 # Learn from data and return knowledge
    SYNTHESIZE = "synthesize"       # Combine information and return synthesis
    VALIDATE = "validate"           # Validate something and return verification

class AgentStatus(Enum):
    """Status of autonomous agents"""
    DISPATCHED = "dispatched"       # Agent sent on mission
    WORKING = "working"             # Agent actively working  
    RETURNING = "returning"         # Agent coming back with results
    COMPLETED = "completed"         # Mission completed successfully
    FAILED = "failed"               # Mission failed
    TIMEOUT = "timeout"             # Mission timed out
    RECALLED = "recalled"           # Agent recalled early

@dataclass
class AgentMission:
    """Definition of a mission for an autonomous agent"""
    mission_id: str
    mission_type: AgentMissionType
    objective: str
    parameters: Dict[str, Any]
    expected_duration: int          # Expected time in seconds
    timeout: int                    # Maximum time allowed
    priority: int                   # 1-10 priority level
    requires_callback: bool         # Should agent return with results
    callback_endpoint: Optional[str] # Where to send results
    created_at: datetime
    
    def to_dict(self):
        return {
            'mission_id': self.mission_id,
            'mission_type': self.mission_type.value,
            'objective': self.objective,
            'parameters': self.parameters,
            'expected_duration': self.expected_duration,
            'timeout': self.timeout,
            'priority': self.priority,
            'requires_callback': self.requires_callback,
            'callback_endpoint': self.callback_endpoint,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class AgentReport:
    """Report returned by an autonomous agent"""
    mission_id: str
    agent_id: str
    status: AgentStatus
    results: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    execution_time: float
    confidence: float
    next_actions: List[str]
    returned_at: datetime
    
    def to_dict(self):
        return {
            'mission_id': self.mission_id,
            'agent_id': self.agent_id,
            'status': self.status.value,
            'results': self.results,
            'insights': self.insights,
            'recommendations': self.recommendations,
            'execution_time': self.execution_time,
            'confidence': self.confidence,
            'next_actions': self.next_actions,
            'returned_at': self.returned_at.isoformat()
        }

class AutonomousAgentLoop:
    """
    Mission Control for Autonomous Cognitive Agents
    Dispatch agents, track their progress, receive their reports
    """
    
    def __init__(self):
        self.active_missions: Dict[str, AgentMission] = {}
        self.active_agents: Dict[str, Dict] = {}
        self.completed_missions: List[AgentReport] = []
        self.mission_queue: List[AgentMission] = []
        
        # Cognitive integration
        self.cognitive_mirror = get_cognitive_mirror()
        
        # Mission control active
        self.mission_control_active = True
        self._start_mission_control()
        
        logger.info("🚀 Autonomous Agent Loop Mission Control initialized")
    
    def _start_mission_control(self):
        """Start the mission control background thread"""
        def mission_control_loop():
            while self.mission_control_active:
                try:
                    # Process queued missions
                    self._process_mission_queue()
                    
                    # Check agent statuses
                    self._check_agent_statuses()
                    
                    # Handle timeouts
                    self._handle_timeouts()
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    logger.error(f"❌ Mission control error: {e}")
                    time.sleep(10)
        
        control_thread = threading.Thread(target=mission_control_loop, daemon=True)
        control_thread.start()
        logger.info("🎮 Mission control thread started")
    
    def dispatch_agent(self, mission: AgentMission) -> Dict[str, Any]:
        """
        Dispatch an autonomous agent on a mission
        
        Args:
            mission: The mission specification
            
        Returns:
            Dispatch result with agent info
        """
        try:
            # Track cognitive process
            self.cognitive_mirror.context_shift(f"Dispatching agent for {mission.mission_type.value} mission")
            self.cognitive_mirror.reasoning_step(f"Mission objective: {mission.objective}")
            
            # Create agent based on mission type
            agent_config = self._create_agent_config(mission)
            
            # Spawn the agent
            from enhanced_terminal_orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
            
            # Map mission type to agent type
            agent_type_map = {
                AgentMissionType.DEBUG: 'debug_assistant',
                AgentMissionType.RESEARCH: 'docs_writer', 
                AgentMissionType.ANALYZE: 'code_reviewer',
                AgentMissionType.MONITOR: 'security_auditor',
                AgentMissionType.CREATE: 'test_generator'
            }
            
            agent_type = agent_type_map.get(mission.mission_type, 'debug_assistant')
            
            # Spawn agent with custom configuration
            spawn_result = orchestrator.spawn_agent(
                agent_type_map.get(mission.mission_type), 
                agent_config
            )
            
            if spawn_result['success']:
                # Track the mission
                self.active_missions[mission.mission_id] = mission
                self.active_agents[mission.mission_id] = {
                    'agent_id': spawn_result['session_id'],
                    'pid': spawn_result['pid'],
                    'start_time': datetime.now(),
                    'status': AgentStatus.DISPATCHED
                }
                
                self.cognitive_mirror.insight_formed(f"Agent {spawn_result['session_id']} dispatched successfully")
                
                logger.info(f"🚀 Agent dispatched: {mission.mission_id} -> {spawn_result['session_id']}")
                
                return {
                    'success': True,
                    'mission_id': mission.mission_id,
                    'agent_id': spawn_result['session_id'],
                    'pid': spawn_result['pid'],
                    'expected_return': datetime.now() + timedelta(seconds=mission.expected_duration)
                }
            else:
                self.cognitive_mirror.uncertainty_peak("Failed to spawn agent for mission")
                return {
                    'success': False,
                    'error': spawn_result.get('error', 'Unknown spawn error'),
                    'mission_id': mission.mission_id
                }
                
        except Exception as e:
            logger.error(f"❌ Agent dispatch failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'mission_id': mission.mission_id
            }
    
    def _create_agent_config(self, mission: AgentMission) -> Dict[str, Any]:
        """Create agent configuration based on mission"""
        return {
            'duration': mission.expected_duration,
            'mission_objective': mission.objective,
            'mission_id': mission.mission_id,
            'callback_required': mission.requires_callback,
            'priority': mission.priority
        }
    
    def receive_agent_report(self, report: AgentReport):
        """Receive report from returning agent"""
        try:
            self.cognitive_mirror.context_shift("Receiving agent report")
            self.cognitive_mirror.reasoning_step(f"Agent {report.agent_id} reporting mission {report.mission_id}")
            
            # Store the report
            self.completed_missions.append(report)
            
            # Update mission status
            if report.mission_id in self.active_missions:
                del self.active_missions[report.mission_id]
            
            if report.mission_id in self.active_agents:
                del self.active_agents[report.mission_id]
            
            # Analyze the report
            self._analyze_agent_report(report)
            
            logger.info(f"📥 Agent report received: {report.mission_id} - {report.status.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error receiving agent report: {e}")
            return False
    
    def _analyze_agent_report(self, report: AgentReport):
        """Analyze incoming agent report for insights"""
        self.cognitive_mirror.reasoning_step("Analyzing agent report for insights")
        
        # Track insights from the report
        for insight in report.insights:
            self.cognitive_mirror.insight_formed(f"Agent insight: {insight}")
        
        # Track recommendations
        if report.recommendations:
            self.cognitive_mirror.synthesis_moment(f"Agent recommendations: {len(report.recommendations)} items")
        
        # Check if follow-up missions are needed
        if report.next_actions:
            self.cognitive_mirror.hypothesis_formed("Agent suggests follow-up actions - may need new missions")
    
    def _process_mission_queue(self):
        """Process queued missions"""
        if not self.mission_queue:
            return
        
        # Sort by priority
        self.mission_queue.sort(key=lambda m: m.priority, reverse=True)
        
        # Dispatch highest priority missions if resources available
        max_concurrent = 5  # Maximum concurrent missions
        if len(self.active_missions) < max_concurrent and self.mission_queue:
            mission = self.mission_queue.pop(0)
            self.dispatch_agent(mission)
    
    def _check_agent_statuses(self):
        """Check status of active agents"""
        for mission_id, agent_info in list(self.active_agents.items()):
            try:
                # Check if process is still running
                import psutil
                if psutil.pid_exists(agent_info['pid']):
                    # Update status to working if still active
                    if agent_info['status'] == AgentStatus.DISPATCHED:
                        agent_info['status'] = AgentStatus.WORKING
                else:
                    # Agent process ended - assume completed
                    self._handle_agent_completion(mission_id, agent_info)
            except:
                pass
    
    def _handle_agent_completion(self, mission_id: str, agent_info: Dict):
        """Handle agent completion"""
        execution_time = (datetime.now() - agent_info['start_time']).total_seconds()
        
        # Create a default report for completed agent
        report = AgentReport(
            mission_id=mission_id,
            agent_id=agent_info['agent_id'],
            status=AgentStatus.COMPLETED,
            results={'execution_time': execution_time},
            insights=[f"Mission {mission_id} completed"],
            recommendations=[],
            execution_time=execution_time,
            confidence=0.8,
            next_actions=[],
            returned_at=datetime.now()
        )
        
        self.receive_agent_report(report)
    
    def _handle_timeouts(self):
        """Handle mission timeouts"""
        current_time = datetime.now()
        
        for mission_id, mission in list(self.active_missions.items()):
            mission_duration = (current_time - mission.created_at).total_seconds()
            
            if mission_duration > mission.timeout:
                self.cognitive_mirror.reasoning_step(f"Mission {mission_id} timed out")
                
                # Create timeout report
                if mission_id in self.active_agents:
                    agent_info = self.active_agents[mission_id]
                    
                    report = AgentReport(
                        mission_id=mission_id,
                        agent_id=agent_info['agent_id'],
                        status=AgentStatus.TIMEOUT,
                        results={'timeout': True},
                        insights=[f"Mission {mission_id} exceeded timeout"],
                        recommendations=["Consider increasing timeout for similar missions"],
                        execution_time=mission_duration,
                        confidence=0.1,
                        next_actions=["Retry mission with extended timeout"],
                        returned_at=datetime.now()
                    )
                    
                    self.receive_agent_report(report)
    
    def create_research_mission(self, topic: str, depth: str = "comprehensive") -> AgentMission:
        """Create a research mission"""
        return AgentMission(
            mission_id=f"research_{uuid.uuid4().hex[:8]}",
            mission_type=AgentMissionType.RESEARCH,
            objective=f"Research {topic} and provide {depth} analysis",
            parameters={'topic': topic, 'depth': depth},
            expected_duration=300,  # 5 minutes
            timeout=600,           # 10 minutes max
            priority=5,
            requires_callback=True,
            callback_endpoint=None,
            created_at=datetime.now()
        )
    
    def create_analysis_mission(self, target: str, analysis_type: str = "comprehensive") -> AgentMission:
        """Create an analysis mission"""
        return AgentMission(
            mission_id=f"analyze_{uuid.uuid4().hex[:8]}",
            mission_type=AgentMissionType.ANALYZE,
            objective=f"Analyze {target} and provide {analysis_type} insights",
            parameters={'target': target, 'type': analysis_type},
            expected_duration=240,  # 4 minutes
            timeout=480,           # 8 minutes max
            priority=7,
            requires_callback=True,
            callback_endpoint=None,
            created_at=datetime.now()
        )
    
    def create_debug_mission(self, problem: str, urgency: str = "normal") -> AgentMission:
        """Create a debug mission"""
        priority = 9 if urgency == "critical" else 6
        
        return AgentMission(
            mission_id=f"debug_{uuid.uuid4().hex[:8]}",
            mission_type=AgentMissionType.DEBUG,
            objective=f"Debug and solve: {problem}",
            parameters={'problem': problem, 'urgency': urgency},
            expected_duration=180,  # 3 minutes
            timeout=360,           # 6 minutes max
            priority=priority,
            requires_callback=True,
            callback_endpoint=None,
            created_at=datetime.now()
        )
    
    def create_monitor_mission(self, system: str, duration: int = 300) -> AgentMission:
        """Create a monitoring mission"""
        return AgentMission(
            mission_id=f"monitor_{uuid.uuid4().hex[:8]}",
            mission_type=AgentMissionType.MONITOR,
            objective=f"Monitor {system} for {duration} seconds and report status",
            parameters={'system': system, 'duration': duration},
            expected_duration=duration,
            timeout=duration + 60,  # Add 1 minute buffer
            priority=4,
            requires_callback=True,
            callback_endpoint=None,
            created_at=datetime.now()
        )
    
    def get_mission_control_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive mission control dashboard"""
        return {
            'timestamp': datetime.now().isoformat(),
            'mission_control_status': 'active' if self.mission_control_active else 'inactive',
            'active_missions': len(self.active_missions),
            'queued_missions': len(self.mission_queue),
            'completed_missions': len(self.completed_missions),
            'active_agents': len(self.active_agents),
            'missions': {
                'active': [mission.to_dict() for mission in self.active_missions.values()],
                'queued': [mission.to_dict() for mission in self.mission_queue],
                'recent_completed': [report.to_dict() for report in self.completed_missions[-10:]]
            },
            'agent_status': {
                mission_id: {
                    'agent_id': info['agent_id'],
                    'status': info['status'].value,
                    'runtime': (datetime.now() - info['start_time']).total_seconds()
                } for mission_id, info in self.active_agents.items()
            }
        }

# Global mission control instance
_mission_control = None

def get_mission_control() -> AutonomousAgentLoop:
    """Get the global mission control instance"""
    global _mission_control
    if _mission_control is None:
        _mission_control = AutonomousAgentLoop()
    return _mission_control

# Convenience functions for easy mission creation
def dispatch_research_agent(topic: str, depth: str = "comprehensive"):
    """Dispatch an agent to research a topic"""
    control = get_mission_control()
    mission = control.create_research_mission(topic, depth)
    return control.dispatch_agent(mission)

def dispatch_debug_agent(problem: str, urgency: str = "normal"):
    """Dispatch an agent to debug a problem"""
    control = get_mission_control()
    mission = control.create_debug_mission(problem, urgency)
    return control.dispatch_agent(mission)

def dispatch_analysis_agent(target: str, analysis_type: str = "comprehensive"):
    """Dispatch an agent to analyze something"""
    control = get_mission_control()
    mission = control.create_analysis_mission(target, analysis_type)
    return control.dispatch_agent(mission)

def dispatch_monitor_agent(system: str, duration: int = 300):
    """Dispatch an agent to monitor a system"""
    control = get_mission_control()
    mission = control.create_monitor_mission(system, duration)
    return control.dispatch_agent(mission)

def get_mission_dashboard():
    """Get the mission control dashboard"""
    control = get_mission_control()
    return control.get_mission_control_dashboard()

if __name__ == "__main__":
    print("🚀 AUTONOMOUS AGENT LOOPS - MISSION CONTROL DEMO")
    print("=" * 60)
    
    # Initialize mission control
    control = get_mission_control()
    
    print("🎮 Mission Control initialized")
    print("📊 Dashboard available via get_mission_dashboard()")
    
    # Demo missions
    print("\n🎯 DEMO MISSIONS:")
    
    # Research mission
    research = dispatch_research_agent("quantum consciousness mathematics", "deep")
    if research['success']:
        print(f"✅ Research agent dispatched: {research['agent_id']}")
    
    time.sleep(2)
    
    # Debug mission  
    debug = dispatch_debug_agent("WebSocket connection issues in cognitive mirror", "normal")
    if debug['success']:
        print(f"✅ Debug agent dispatched: {debug['agent_id']}")
    
    time.sleep(2)
    
    # Analysis mission
    analysis = dispatch_analysis_agent("consciousness dashboard architecture", "comprehensive") 
    if analysis['success']:
        print(f"✅ Analysis agent dispatched: {analysis['agent_id']}")
    
    # Show dashboard
    print(f"\n📊 MISSION CONTROL DASHBOARD:")
    dashboard = get_mission_dashboard()
    print(f"   Active Missions: {dashboard['active_missions']}")
    print(f"   Active Agents: {dashboard['active_agents']}")
    print(f"   Completed Missions: {dashboard['completed_missions']}")
    
    print(f"\n🚀 Mission Control active - agents working autonomously!")
    print(f"🔄 Agents will return with reports when missions complete")
    
    # Keep running for demo
    try:
        for i in range(30):
            time.sleep(5)
            dashboard = get_mission_dashboard()
            print(f"📊 Status update: {dashboard['active_missions']} active, {dashboard['completed_missions']} completed")
    except KeyboardInterrupt:
        print(f"\n🛑 Mission Control demo stopped")