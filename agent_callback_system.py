#!/usr/bin/env python3
"""
Agent Callback System - Mission Completion Response Handler
Implements sophisticated callback mechanisms for agents returning from missions

This creates the "return" part of the agent loop - when agents complete missions,
they use this system to report back with results, insights, and recommendations.
"""

import asyncio
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import logging
from pathlib import Path
import uuid
import websockets

# Import our existing systems
from autonomous_agent_loops import AgentReport, AgentStatus, get_mission_control
from realtime_cognitive_mirror import get_cognitive_mirror
from enhanced_mission_control import get_enhanced_mission_control

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] CALLBACK: %(message)s',
    handlers=[
        logging.FileHandler('agent_callbacks.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('agent_callbacks')

class CallbackType(Enum):
    """Types of callbacks agents can make"""
    MISSION_COMPLETE = "mission_complete"
    PROGRESS_UPDATE = "progress_update"
    REQUEST_ASSISTANCE = "request_assistance"
    REPORT_INSIGHT = "report_insight"
    ESCALATE_ISSUE = "escalate_issue"
    REQUEST_EXTENSION = "request_extension"
    COLLABORATIVE_SYNC = "collaborative_sync"

@dataclass
class CallbackMessage:
    """Message structure for agent callbacks"""
    callback_id: str
    agent_id: str
    mission_id: str
    callback_type: CallbackType
    content: Dict[str, Any]
    timestamp: datetime
    urgency: int  # 1-10 scale
    requires_response: bool
    response_timeout: Optional[int]  # seconds
    
    def to_dict(self):
        return {
            'callback_id': self.callback_id,
            'agent_id': self.agent_id,
            'mission_id': self.mission_id,
            'callback_type': self.callback_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'urgency': self.urgency,
            'requires_response': self.requires_response,
            'response_timeout': self.response_timeout
        }

@dataclass
class CallbackResponse:
    """Response to agent callback"""
    callback_id: str
    response_type: str
    instructions: Dict[str, Any]
    approved: bool
    message: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            'callback_id': self.callback_id,
            'response_type': self.response_type,
            'instructions': self.instructions,
            'approved': self.approved,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

class AgentCallbackSystem:
    """
    Advanced callback system for agents returning from missions
    Handles mission completion reports, progress updates, and collaborative requests
    """
    
    def __init__(self, port: int = 8087):
        self.port = port
        self.mission_control = get_mission_control()
        self.cognitive_mirror = get_cognitive_mirror()
        self.enhanced_control = get_enhanced_mission_control()
        
        # Callback tracking
        self.active_callbacks = {}
        self.callback_history = []
        self.callback_handlers = {}
        self.response_queue = {}
        
        # Performance metrics
        self.callback_stats = {
            'total_callbacks': 0,
            'successful_callbacks': 0,
            'failed_callbacks': 0,
            'average_response_time': 0.0,
            'callback_types': {}
        }
        
        # WebSocket server for agent callbacks
        self.callback_server = None
        self.server_active = False
        
        self._register_default_handlers()
        self._start_callback_server()
        
        logger.info("📞 Agent Callback System initialized")
    
    def _register_default_handlers(self):
        """Register default callback handlers"""
        self.callback_handlers[CallbackType.MISSION_COMPLETE] = self._handle_mission_complete
        self.callback_handlers[CallbackType.PROGRESS_UPDATE] = self._handle_progress_update
        self.callback_handlers[CallbackType.REQUEST_ASSISTANCE] = self._handle_assistance_request
        self.callback_handlers[CallbackType.REPORT_INSIGHT] = self._handle_insight_report
        self.callback_handlers[CallbackType.ESCALATE_ISSUE] = self._handle_issue_escalation
        self.callback_handlers[CallbackType.REQUEST_EXTENSION] = self._handle_extension_request
        self.callback_handlers[CallbackType.COLLABORATIVE_SYNC] = self._handle_collaborative_sync
        
        logger.info("🔧 Default callback handlers registered")
    
    def _start_callback_server(self):
        """Start WebSocket server for agent callbacks"""
        async def handle_callback_connection(websocket, path):
            """Handle incoming agent callback connections"""
            agent_id = None
            try:
                logger.info(f"📞 Agent callback connection: {websocket.remote_address}")
                
                async for message in websocket:
                    try:
                        callback_data = json.loads(message)
                        agent_id = callback_data.get('agent_id')
                        
                        # Process the callback
                        response = await self._process_callback(callback_data, websocket)
                        
                        # Send response back to agent
                        if response:
                            await websocket.send(json.dumps(response.to_dict()))
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Invalid callback JSON from {agent_id}: {e}")
                        await websocket.send(json.dumps({
                            'error': 'Invalid JSON format',
                            'timestamp': datetime.now().isoformat()
                        }))
                    except Exception as e:
                        logger.error(f"❌ Callback processing error from {agent_id}: {e}")
                        await websocket.send(json.dumps({
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        }))
                        
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"📞 Agent {agent_id} callback connection closed")
            except Exception as e:
                logger.error(f"❌ Callback connection error: {e}")
        
        def run_callback_server():
            """Run the callback server"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                start_server = websockets.serve(handle_callback_connection, "localhost", self.port)
                logger.info(f"📞 Agent Callback Server started on ws://localhost:{self.port}")
                
                self.server_active = True
                loop.run_until_complete(start_server)
                loop.run_forever()
                
            except Exception as e:
                logger.error(f"❌ Callback server error: {e}")
                self.server_active = False
        
        server_thread = threading.Thread(target=run_callback_server, daemon=True)
        server_thread.start()
    
    async def _process_callback(self, callback_data: Dict[str, Any], websocket) -> Optional[CallbackResponse]:
        """Process incoming agent callback"""
        try:
            # Create callback message
            callback = CallbackMessage(
                callback_id=callback_data.get('callback_id', str(uuid.uuid4())),
                agent_id=callback_data.get('agent_id', 'unknown'),
                mission_id=callback_data.get('mission_id', 'unknown'),
                callback_type=CallbackType(callback_data.get('callback_type', 'mission_complete')),
                content=callback_data.get('content', {}),
                timestamp=datetime.now(),
                urgency=callback_data.get('urgency', 5),
                requires_response=callback_data.get('requires_response', False),
                response_timeout=callback_data.get('response_timeout', 30)
            )
            
            # Track callback
            self.active_callbacks[callback.callback_id] = {
                'callback': callback,
                'websocket': websocket,
                'received_at': datetime.now()
            }
            
            # Update consciousness
            self.cognitive_mirror.context_shift(f"Received {callback.callback_type.value} from agent {callback.agent_id}")
            self.cognitive_mirror.reasoning_step(f"Processing callback for mission {callback.mission_id}")
            
            # Route to appropriate handler
            handler = self.callback_handlers.get(callback.callback_type)
            if handler:
                response = await handler(callback)
                
                # Update stats
                self.callback_stats['total_callbacks'] += 1
                self.callback_stats['successful_callbacks'] += 1
                callback_type_key = callback.callback_type.value
                self.callback_stats['callback_types'][callback_type_key] = (
                    self.callback_stats['callback_types'].get(callback_type_key, 0) + 1
                )
                
                # Move to history
                self.callback_history.append(callback)
                if callback.callback_id in self.active_callbacks:
                    del self.active_callbacks[callback.callback_id]
                
                return response
            else:
                logger.error(f"❌ No handler for callback type: {callback.callback_type}")
                self.callback_stats['failed_callbacks'] += 1
                return CallbackResponse(
                    callback_id=callback.callback_id,
                    response_type='error',
                    instructions={},
                    approved=False,
                    message=f"No handler for {callback.callback_type.value}",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"❌ Callback processing error: {e}")
            self.callback_stats['failed_callbacks'] += 1
            return CallbackResponse(
                callback_id=callback_data.get('callback_id', 'unknown'),
                response_type='error',
                instructions={},
                approved=False,
                message=f"Processing error: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _handle_mission_complete(self, callback: CallbackMessage) -> CallbackResponse:
        """Handle mission completion callback"""
        try:
            content = callback.content
            
            # Create agent report
            report = AgentReport(
                mission_id=callback.mission_id,
                agent_id=callback.agent_id,
                status=AgentStatus(content.get('status', 'completed')),
                results=content.get('results', {}),
                insights=content.get('insights', []),
                recommendations=content.get('recommendations', []),
                execution_time=content.get('execution_time', 0.0),
                confidence=content.get('confidence', 0.8),
                next_actions=content.get('next_actions', []),
                returned_at=datetime.now()
            )
            
            # Submit report to mission control
            success = self.mission_control.receive_agent_report(report)
            
            # Update consciousness
            if success:
                self.cognitive_mirror.insight_formed(f"Mission {callback.mission_id} completed successfully")
                self.cognitive_mirror.synthesis_moment(f"Agent {callback.agent_id} returned with valuable insights")
                
                # Process insights
                for insight in report.insights:
                    self.cognitive_mirror.pattern_recognized(f"Agent insight: {insight}")
                
                # Process recommendations
                if report.recommendations:
                    self.cognitive_mirror.hypothesis_formed(f"Agent suggests {len(report.recommendations)} follow-up actions")
            else:
                self.cognitive_mirror.uncertainty_peak("Failed to process mission completion report")
            
            logger.info(f"✅ Mission completion processed: {callback.mission_id} by {callback.agent_id}")
            
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='mission_complete_ack',
                instructions={'status': 'acknowledged', 'can_terminate': True},
                approved=True,
                message="Mission completion acknowledged - agent may terminate",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Mission complete handler error: {e}")
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='error',
                instructions={},
                approved=False,
                message=f"Error processing completion: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _handle_progress_update(self, callback: CallbackMessage) -> CallbackResponse:
        """Handle progress update callback"""
        try:
            progress = callback.content.get('progress', 0)
            status = callback.content.get('status', 'working')
            current_task = callback.content.get('current_task', 'Unknown task')
            
            self.cognitive_mirror.reasoning_step(f"Agent {callback.agent_id} progress: {progress}% - {current_task}")
            
            logger.info(f"📊 Progress update: {callback.agent_id} - {progress}% - {status}")
            
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='progress_ack',
                instructions={'continue': True, 'status': 'acknowledged'},
                approved=True,
                message="Progress update received - continue mission",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Progress update handler error: {e}")
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='error',
                instructions={},
                approved=False,
                message=f"Error processing progress: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _handle_assistance_request(self, callback: CallbackMessage) -> CallbackResponse:
        """Handle assistance request callback"""
        try:
            problem = callback.content.get('problem', 'Unknown problem')
            assistance_type = callback.content.get('assistance_type', 'general')
            
            self.cognitive_mirror.context_shift(f"Agent {callback.agent_id} requesting assistance")
            self.cognitive_mirror.reasoning_step(f"Problem: {problem}")
            self.cognitive_mirror.hypothesis_formed("May need to dispatch helper agent or provide guidance")
            
            # Analyze the request and provide assistance
            assistance_response = {
                'guidance': f"Analyzing problem: {problem}",
                'suggested_approach': "Break down the problem into smaller components",
                'resources': ["Check system logs", "Review mission parameters"],
                'escalate': assistance_type == 'critical'
            }
            
            logger.info(f"🤝 Assistance request: {callback.agent_id} - {problem}")
            
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='assistance_provided',
                instructions=assistance_response,
                approved=True,
                message="Assistance provided - continue with guidance",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Assistance request handler error: {e}")
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='error',
                instructions={},
                approved=False,
                message=f"Error processing assistance request: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _handle_insight_report(self, callback: CallbackMessage) -> CallbackResponse:
        """Handle insight report callback"""
        try:
            insights = callback.content.get('insights', [])
            confidence = callback.content.get('confidence', 0.8)
            
            # Process each insight
            for insight in insights:
                self.cognitive_mirror.insight_formed(f"Agent insight: {insight}")
                self.cognitive_mirror.pattern_recognized(insight)
            
            logger.info(f"💡 Insights reported by {callback.agent_id}: {len(insights)} insights")
            
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='insight_acknowledged',
                instructions={'status': 'insights_processed', 'continue': True},
                approved=True,
                message=f"Received {len(insights)} insights - continue mission",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Insight report handler error: {e}")
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='error',
                instructions={},
                approved=False,
                message=f"Error processing insights: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _handle_issue_escalation(self, callback: CallbackMessage) -> CallbackResponse:
        """Handle issue escalation callback"""
        try:
            issue = callback.content.get('issue', 'Unknown issue')
            severity = callback.content.get('severity', 'medium')
            
            self.cognitive_mirror.uncertainty_peak(f"Agent {callback.agent_id} escalating issue: {issue}")
            self.cognitive_mirror.reasoning_step("Need to analyze escalated issue and determine response")
            
            # Handle escalation based on severity
            if severity == 'critical':
                self.cognitive_mirror.context_shift("CRITICAL ISSUE - immediate attention required")
                response_instructions = {
                    'action': 'pause_mission',
                    'await_instructions': True,
                    'report_interval': 30  # Report every 30 seconds
                }
            else:
                response_instructions = {
                    'action': 'continue_with_caution',
                    'monitoring_increased': True,
                    'report_interval': 60
                }
            
            logger.warning(f"⚠️ Issue escalated by {callback.agent_id}: {issue} (severity: {severity})")
            
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='escalation_handled',
                instructions=response_instructions,
                approved=True,
                message=f"Issue escalation processed - {response_instructions['action']}",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Issue escalation handler error: {e}")
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='error',
                instructions={},
                approved=False,
                message=f"Error processing escalation: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _handle_extension_request(self, callback: CallbackMessage) -> CallbackResponse:
        """Handle mission extension request callback"""
        try:
            current_progress = callback.content.get('progress', 0)
            additional_time = callback.content.get('additional_time', 300)  # 5 minutes default
            reason = callback.content.get('reason', 'More time needed')
            
            self.cognitive_mirror.reasoning_step(f"Agent {callback.agent_id} requesting {additional_time}s extension")
            self.cognitive_mirror.hypothesis_formed("Agent needs more time - evaluate if extension is justified")
            
            # Evaluate extension request
            extension_approved = current_progress > 0.3  # Approve if >30% progress
            
            if extension_approved:
                self.cognitive_mirror.insight_formed("Extension approved - agent making good progress")
                instructions = {
                    'extension_granted': True,
                    'additional_time': additional_time,
                    'new_deadline': (datetime.now() + timedelta(seconds=additional_time)).isoformat()
                }
                message = f"Extension granted: {additional_time} seconds"
            else:
                self.cognitive_mirror.uncertainty_peak("Extension denied - insufficient progress")
                instructions = {
                    'extension_granted': False,
                    'reason': 'Insufficient progress made',
                    'wrap_up_time': 60
                }
                message = "Extension denied - prepare to wrap up mission"
            
            logger.info(f"⏰ Extension request from {callback.agent_id}: {'APPROVED' if extension_approved else 'DENIED'}")
            
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='extension_response',
                instructions=instructions,
                approved=extension_approved,
                message=message,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Extension request handler error: {e}")
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='error',
                instructions={},
                approved=False,
                message=f"Error processing extension request: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _handle_collaborative_sync(self, callback: CallbackMessage) -> CallbackResponse:
        """Handle collaborative synchronization callback"""
        try:
            sync_type = callback.content.get('sync_type', 'status_sync')
            data = callback.content.get('data', {})
            
            self.cognitive_mirror.synthesis_moment(f"Agent {callback.agent_id} synchronizing: {sync_type}")
            
            # Process collaborative sync
            sync_response = {
                'sync_acknowledged': True,
                'system_status': 'operational',
                'other_agents': len(self.active_callbacks),
                'shared_insights': ['System performance is stable', 'Mission queue is processing normally']
            }
            
            logger.info(f"🔄 Collaborative sync from {callback.agent_id}: {sync_type}")
            
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='sync_response',
                instructions=sync_response,
                approved=True,
                message="Collaborative sync completed",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Collaborative sync handler error: {e}")
            return CallbackResponse(
                callback_id=callback.callback_id,
                response_type='error',
                instructions={},
                approved=False,
                message=f"Error processing sync: {str(e)}",
                timestamp=datetime.now()
            )
    
    def get_callback_stats(self) -> Dict[str, Any]:
        """Get callback system statistics"""
        return {
            'stats': self.callback_stats,
            'active_callbacks': len(self.active_callbacks),
            'callback_history_size': len(self.callback_history),
            'server_active': self.server_active,
            'recent_callbacks': [
                {
                    'agent_id': cb.agent_id,
                    'mission_id': cb.mission_id,
                    'type': cb.callback_type.value,
                    'timestamp': cb.timestamp.isoformat(),
                    'urgency': cb.urgency
                }
                for cb in self.callback_history[-10:]  # Last 10 callbacks
            ]
        }

# Global callback system instance
_callback_system = None

def get_callback_system(port: int = 8087) -> AgentCallbackSystem:
    """Get the global callback system instance"""
    global _callback_system
    if _callback_system is None:
        _callback_system = AgentCallbackSystem(port)
    return _callback_system

# Convenience functions for simulating agent callbacks
async def simulate_mission_completion(agent_id: str, mission_id: str, results: Dict[str, Any]):
    """Simulate an agent completing a mission"""
    callback_system = get_callback_system()
    
    callback_data = {
        'callback_id': str(uuid.uuid4()),
        'agent_id': agent_id,
        'mission_id': mission_id,
        'callback_type': 'mission_complete',
        'content': {
            'status': 'completed',
            'results': results,
            'insights': ['Mission completed successfully', 'No issues encountered'],
            'recommendations': ['Consider similar missions in the future'],
            'execution_time': 180.5,
            'confidence': 0.95,
            'next_actions': []
        },
        'urgency': 5,
        'requires_response': True
    }
    
    # Create a mock websocket for simulation
    class MockWebSocket:
        async def send(self, message):
            print(f"📞 Mock callback response: {json.loads(message)['message']}")
    
    mock_ws = MockWebSocket()
    return await callback_system._process_callback(callback_data, mock_ws)

if __name__ == "__main__":
    print("📞 AGENT CALLBACK SYSTEM - MISSION COMPLETION HANDLER")
    print("=" * 60)
    
    # Initialize callback system
    callback_system = get_callback_system()
    
    print(f"📞 Agent Callback Server: ws://localhost:8087")
    print(f"🔧 Callback handlers registered: {len(callback_system.callback_handlers)}")
    print("=" * 60)
    
    # Demo callback processing
    print("\n🎯 DEMONSTRATING CALLBACK PROCESSING:")
    
    async def run_demo():
        # Simulate mission completion
        result = await simulate_mission_completion(
            "demo_agent_001",
            "research_12345",
            {"analysis_complete": True, "findings": ["Key insight 1", "Key insight 2"]}
        )
        
        if result and result.approved:
            print(f"✅ Demo callback processed successfully")
        
        # Show stats
        stats = callback_system.get_callback_stats()
        print(f"\n📊 CALLBACK STATISTICS:")
        print(f"   Total Callbacks: {stats['stats']['total_callbacks']}")
        print(f"   Successful: {stats['stats']['successful_callbacks']}")
        print(f"   Active: {stats['active_callbacks']}")
        print(f"   Server Status: {'Online' if stats['server_active'] else 'Offline'}")
    
    # Run demo
    asyncio.run(run_demo())
    
    print(f"\n📞 Agent Callback System active - agents can now report back!")
    print(f"💡 Agents connect to ws://localhost:8087 to send callbacks")
    
    # Keep running
    try:
        while True:
            time.sleep(10)
            # Periodic status check
            if callback_system.server_active:
                callback_system.cognitive_mirror.reasoning_step("Callback system monitoring active")
    except KeyboardInterrupt:
        print(f"\n🛑 Agent Callback System stopped")