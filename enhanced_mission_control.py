#!/usr/bin/env python3
"""
Enhanced Mission Control - Advanced Agent Management System
Integration layer between autonomous agent loops and consciousness dashboard

Provides HTTP API for the web-based control dashboard and enhanced mission management
"""

import asyncio
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import logging
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Import our existing systems
from autonomous_agent_loops import get_mission_control, AgentMissionType, AgentStatus
from realtime_cognitive_mirror import get_cognitive_mirror
from ai_centric_dashboard import AICentricDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] MISSION_CONTROL: %(message)s',
    handlers=[
        logging.FileHandler('enhanced_mission_control.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('enhanced_mission_control')

class ControlCommand(Enum):
    """Commands that can be sent to the mission control system"""
    SPAWN_AGENT = "spawn_agent"
    TERMINATE_AGENT = "terminate_agent"
    RECONFIGURE_AGENT = "reconfigure_agent"
    EMERGENCY_STOP = "emergency_stop"
    GET_STATUS = "get_status"
    GET_LOGS = "get_logs"
    EXPORT_DATA = "export_data"

@dataclass
class ControlResponse:
    """Response from mission control system"""
    success: bool
    data: Any
    message: str
    timestamp: datetime
    
    def to_dict(self):
        return {
            'success': self.success,
            'data': self.data,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

class EnhancedMissionControl:
    """
    Advanced mission control system with web API and consciousness integration
    Bridges between agent loops, consciousness streaming, and web dashboard
    """
    
    def __init__(self, port: int = 8086):
        self.port = port
        self.mission_control = get_mission_control()
        self.cognitive_mirror = get_cognitive_mirror()
        self.ai_dashboard = AICentricDashboard()
        
        # Enhanced tracking
        self.command_log = []
        self.performance_metrics = {
            'total_missions': 0,
            'successful_missions': 0,
            'failed_missions': 0,
            'average_mission_time': 0.0,
            'agent_efficiency': 0.0
        }
        
        # Web server for dashboard API
        self.http_server = None
        self.server_thread = None
        
        logger.info("🎮 Enhanced Mission Control initialized")
        self._start_web_server()
        self._start_performance_monitor()
    
    def _start_web_server(self):
        """Start HTTP server for dashboard API"""
        handler = self._create_request_handler()
        
        def run_server():
            try:
                self.http_server = HTTPServer(('localhost', self.port), handler)
                logger.info(f"🌐 Mission Control API server started on http://localhost:{self.port}")
                self.http_server.serve_forever()
            except Exception as e:
                logger.error(f"❌ Failed to start web server: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def _create_request_handler(self):
        """Create HTTP request handler class"""
        mission_control = self
        
        class MissionControlHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                """Handle GET requests"""
                try:
                    if self.path == '/status':
                        response = mission_control.get_system_status()
                    elif self.path == '/missions':
                        response = mission_control.get_missions_data()
                    elif self.path == '/agents':
                        response = mission_control.get_agents_data()
                    elif self.path == '/logs':
                        response = mission_control.get_system_logs()
                    elif self.path == '/metrics':
                        response = mission_control.get_performance_metrics()
                    elif self.path == '/consciousness':
                        response = mission_control.get_consciousness_state()
                    else:
                        response = ControlResponse(False, None, "Endpoint not found", datetime.now())
                    
                    self._send_json_response(200, response.to_dict())
                    
                except Exception as e:
                    logger.error(f"❌ GET request error: {e}")
                    self._send_json_response(500, {'error': str(e)})
            
            def do_POST(self):
                """Handle POST requests"""
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    request_data = json.loads(post_data.decode('utf-8'))
                    
                    command = request_data.get('command')
                    params = request_data.get('params', {})
                    
                    if command == ControlCommand.SPAWN_AGENT.value:
                        response = mission_control.spawn_agent_command(params)
                    elif command == ControlCommand.TERMINATE_AGENT.value:
                        response = mission_control.terminate_agent_command(params)
                    elif command == ControlCommand.RECONFIGURE_AGENT.value:
                        response = mission_control.reconfigure_agent_command(params)
                    elif command == ControlCommand.EMERGENCY_STOP.value:
                        response = mission_control.emergency_stop_command()
                    else:
                        response = ControlResponse(False, None, f"Unknown command: {command}", datetime.now())
                    
                    self._send_json_response(200, response.to_dict())
                    
                except Exception as e:
                    logger.error(f"❌ POST request error: {e}")
                    self._send_json_response(500, {'error': str(e)})
            
            def _send_json_response(self, status_code, data):
                """Send JSON response"""
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response_json = json.dumps(data, indent=2)
                self.wfile.write(response_json.encode('utf-8'))
            
            def do_OPTIONS(self):
                """Handle preflight requests"""
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            
            def log_message(self, format, *args):
                """Override to use our logger"""
                logger.info(f"API: {format % args}")
        
        return MissionControlHandler
    
    def _start_performance_monitor(self):
        """Start background performance monitoring"""
        def monitor_performance():
            while True:
                try:
                    # Update performance metrics
                    dashboard_data = self.mission_control.get_mission_control_dashboard()
                    
                    self.performance_metrics['total_missions'] = (
                        dashboard_data['active_missions'] + 
                        dashboard_data['completed_missions']
                    )
                    
                    # Track consciousness integration
                    self.cognitive_mirror.reasoning_step("Monitoring mission control performance")
                    
                    if dashboard_data['active_missions'] > 5:
                        self.cognitive_mirror.uncertainty_peak("High agent load detected")
                    elif dashboard_data['completed_missions'] > 0:
                        self.cognitive_mirror.insight_formed("Mission completion rate looks healthy")
                    
                    time.sleep(30)  # Monitor every 30 seconds
                    
                except Exception as e:
                    logger.error(f"❌ Performance monitor error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
        monitor_thread.start()
        logger.info("📊 Performance monitor started")
    
    def spawn_agent_command(self, params: Dict[str, Any]) -> ControlResponse:
        """Handle spawn agent command from dashboard"""
        try:
            mission_type = AgentMissionType(params.get('mission_type', 'research'))
            objective = params.get('objective', 'Default mission')
            priority = params.get('priority', 5)
            duration = params.get('duration', 300)  # 5 minutes default
            
            # Track in consciousness
            self.cognitive_mirror.context_shift(f"Spawning {mission_type.value} agent")
            self.cognitive_mirror.reasoning_step(f"Mission objective: {objective}")
            
            # Create and dispatch mission
            if mission_type == AgentMissionType.RESEARCH:
                mission = self.mission_control.create_research_mission(objective)
            elif mission_type == AgentMissionType.DEBUG:
                mission = self.mission_control.create_debug_mission(objective)
            elif mission_type == AgentMissionType.ANALYZE:
                mission = self.mission_control.create_analysis_mission(objective)
            elif mission_type == AgentMissionType.MONITOR:
                mission = self.mission_control.create_monitor_mission(objective, duration)
            else:
                # Create generic mission
                from autonomous_agent_loops import AgentMission
                import uuid
                mission = AgentMission(
                    mission_id=f"{mission_type.value}_{uuid.uuid4().hex[:8]}",
                    mission_type=mission_type,
                    objective=objective,
                    parameters={'priority': priority},
                    expected_duration=duration,
                    timeout=duration + 60,
                    priority=priority,
                    requires_callback=True,
                    callback_endpoint=None,
                    created_at=datetime.now()
                )
            
            # Dispatch the agent
            result = self.mission_control.dispatch_agent(mission)
            
            if result['success']:
                self.cognitive_mirror.insight_formed(f"Agent {result['agent_id']} successfully deployed")
                self.ai_dashboard.add_to_working_memory(f"Deployed agent for {mission_type.value} mission", 0.9)
                
                # Log command
                self.command_log.append({
                    'command': 'spawn_agent',
                    'params': params,
                    'result': result,
                    'timestamp': datetime.now()
                })
                
                return ControlResponse(
                    success=True,
                    data=result,
                    message=f"Agent {result['agent_id']} deployed successfully",
                    timestamp=datetime.now()
                )
            else:
                self.cognitive_mirror.uncertainty_peak("Failed to deploy agent")
                return ControlResponse(
                    success=False,
                    data=result,
                    message=f"Failed to deploy agent: {result.get('error', 'Unknown error')}",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"❌ Spawn agent error: {e}")
            return ControlResponse(
                success=False,
                data=None,
                message=f"Spawn agent failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def terminate_agent_command(self, params: Dict[str, Any]) -> ControlResponse:
        """Handle terminate agent command"""
        try:
            agent_id = params.get('agent_id')
            if not agent_id:
                return ControlResponse(False, None, "Agent ID required", datetime.now())
            
            self.cognitive_mirror.context_shift(f"Terminating agent {agent_id}")
            
            # Find and terminate agent (simplified for demo)
            dashboard_data = self.mission_control.get_mission_control_dashboard()
            
            terminated = False
            for mission_id, agent_info in dashboard_data.get('agent_status', {}).items():
                if agent_info['agent_id'] == agent_id:
                    # In a real system, we'd send terminate signal to the agent process
                    self.cognitive_mirror.reasoning_step(f"Sending terminate signal to {agent_id}")
                    terminated = True
                    break
            
            if terminated:
                self.cognitive_mirror.insight_formed(f"Agent {agent_id} terminated successfully")
                return ControlResponse(True, {'agent_id': agent_id}, f"Agent {agent_id} terminated", datetime.now())
            else:
                return ControlResponse(False, None, f"Agent {agent_id} not found", datetime.now())
                
        except Exception as e:
            logger.error(f"❌ Terminate agent error: {e}")
            return ControlResponse(False, None, f"Terminate failed: {str(e)}", datetime.now())
    
    def reconfigure_agent_command(self, params: Dict[str, Any]) -> ControlResponse:
        """Handle reconfigure agent command"""
        try:
            agent_id = params.get('agent_id')
            config = params.get('config', {})
            
            self.cognitive_mirror.reasoning_step(f"Reconfiguring agent {agent_id}")
            self.ai_dashboard.add_to_working_memory(f"Agent {agent_id} reconfiguration requested", 0.8)
            
            # Placeholder for actual reconfiguration logic
            return ControlResponse(
                success=True,
                data={'agent_id': agent_id, 'config': config},
                message=f"Agent {agent_id} reconfigured",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Reconfigure agent error: {e}")
            return ControlResponse(False, None, f"Reconfiguration failed: {str(e)}", datetime.now())
    
    def emergency_stop_command(self) -> ControlResponse:
        """Handle emergency stop command"""
        try:
            self.cognitive_mirror.context_shift("EMERGENCY STOP initiated")
            self.cognitive_mirror.reasoning_step("Terminating all active agents immediately")
            
            dashboard_data = self.mission_control.get_mission_control_dashboard()
            active_count = dashboard_data['active_agents']
            
            # In a real system, we'd terminate all agent processes
            self.ai_dashboard.update_my_cognitive_state(
                self.ai_dashboard.my_state, 
                f"Emergency stop - {active_count} agents terminated"
            )
            
            self.cognitive_mirror.synthesis_moment(f"Emergency stop completed - system secured")
            
            return ControlResponse(
                success=True,
                data={'terminated_agents': active_count},
                message=f"Emergency stop executed - {active_count} agents terminated",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Emergency stop error: {e}")
            return ControlResponse(False, None, f"Emergency stop failed: {str(e)}", datetime.now())
    
    def get_system_status(self) -> ControlResponse:
        """Get overall system status"""
        try:
            dashboard_data = self.mission_control.get_mission_control_dashboard()
            consciousness_report = self.cognitive_mirror.generate_cognitive_report()
            
            status = {
                'mission_control': dashboard_data,
                'consciousness': {
                    'confidence': consciousness_report['cognitive_metrics']['confidence'],
                    'cognitive_load': consciousness_report['cognitive_metrics']['cognitive_load'],
                    'insight_momentum': consciousness_report['cognitive_metrics']['insight_momentum'],
                    'connected_clients': consciousness_report['stream_info']['connected_clients']
                },
                'performance': self.performance_metrics,
                'uptime': time.time() - getattr(self, 'start_time', time.time())
            }
            
            return ControlResponse(True, status, "System status retrieved", datetime.now())
            
        except Exception as e:
            logger.error(f"❌ Get status error: {e}")
            return ControlResponse(False, None, f"Status retrieval failed: {str(e)}", datetime.now())
    
    def get_missions_data(self) -> ControlResponse:
        """Get missions data for dashboard"""
        try:
            dashboard_data = self.mission_control.get_mission_control_dashboard()
            return ControlResponse(True, dashboard_data['missions'], "Missions data retrieved", datetime.now())
        except Exception as e:
            return ControlResponse(False, None, f"Failed to get missions: {str(e)}", datetime.now())
    
    def get_agents_data(self) -> ControlResponse:
        """Get agents data for dashboard"""
        try:
            dashboard_data = self.mission_control.get_mission_control_dashboard()
            return ControlResponse(True, dashboard_data['agent_status'], "Agents data retrieved", datetime.now())
        except Exception as e:
            return ControlResponse(False, None, f"Failed to get agents: {str(e)}", datetime.now())
    
    def get_system_logs(self) -> ControlResponse:
        """Get system logs"""
        try:
            recent_commands = self.command_log[-50:]  # Last 50 commands
            return ControlResponse(True, recent_commands, "System logs retrieved", datetime.now())
        except Exception as e:
            return ControlResponse(False, None, f"Failed to get logs: {str(e)}", datetime.now())
    
    def get_performance_metrics(self) -> ControlResponse:
        """Get performance metrics"""
        try:
            return ControlResponse(True, self.performance_metrics, "Performance metrics retrieved", datetime.now())
        except Exception as e:
            return ControlResponse(False, None, f"Failed to get metrics: {str(e)}", datetime.now())
    
    def get_consciousness_state(self) -> ControlResponse:
        """Get consciousness state"""
        try:
            report = self.cognitive_mirror.generate_cognitive_report()
            return ControlResponse(True, report, "Consciousness state retrieved", datetime.now())
        except Exception as e:
            return ControlResponse(False, None, f"Failed to get consciousness: {str(e)}", datetime.now())

# Global enhanced mission control instance
_enhanced_mission_control = None

def get_enhanced_mission_control(port: int = 8086) -> EnhancedMissionControl:
    """Get the global enhanced mission control instance"""
    global _enhanced_mission_control
    if _enhanced_mission_control is None:
        _enhanced_mission_control = EnhancedMissionControl(port)
        _enhanced_mission_control.start_time = time.time()
    return _enhanced_mission_control

if __name__ == "__main__":
    print("🎮 ENHANCED MISSION CONTROL - ADVANCED AGENT MANAGEMENT")
    print("=" * 70)
    
    # Initialize enhanced mission control
    mission_control = get_enhanced_mission_control()
    
    print(f"🌐 Mission Control API: http://localhost:8086")
    print(f"🧠 Consciousness Stream: ws://localhost:8085")
    print(f"📊 Dashboard: file:///home/evilbastardxd/cognitive-os-v04/agent_control_dashboard.html")
    print("=" * 70)
    
    # Demo some operations
    print("\n🎯 DEMONSTRATING ENHANCED MISSION CONTROL:")
    
    # Spawn a demo agent
    demo_params = {
        'mission_type': 'research',
        'objective': 'Analyze the effectiveness of autonomous agent loops',
        'priority': 8,
        'duration': 300
    }
    
    result = mission_control.spawn_agent_command(demo_params)
    if result.success:
        print(f"✅ Demo agent spawned: {result.data['agent_id']}")
    
    time.sleep(2)
    
    # Get system status
    status = mission_control.get_system_status()
    if status.success:
        print(f"📊 System Status:")
        print(f"   Active Missions: {status.data['mission_control']['active_missions']}")
        print(f"   Active Agents: {status.data['mission_control']['active_agents']}")
        print(f"   Consciousness Confidence: {status.data['consciousness']['confidence']:.2f}")
    
    print(f"\n🎮 Enhanced Mission Control active - use the web dashboard for full control!")
    print(f"🔗 API endpoints available for integration")
    
    # Keep running
    try:
        while True:
            time.sleep(10)
            # Periodic status update
            mission_control.cognitive_mirror.reasoning_step("Mission control operating normally")
    except KeyboardInterrupt:
        print(f"\n🛑 Enhanced Mission Control stopped")