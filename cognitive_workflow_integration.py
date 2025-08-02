#!/usr/bin/env python3
"""
Cognitive OS Workflow Integration - Inline operation with parallel agent management
This integrates screen sharing into the development workflow for context-aware assistance
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import tools
import subprocess
import os

class AgentType(Enum):
    """Types of specialized agents that can be spawned"""
    CODE_ANALYZER = "code_analyzer"
    DOCUMENTATION_WRITER = "doc_writer"
    TEST_GENERATOR = "test_gen"
    REFACTORING = "refactoring"
    DEBUGGING = "debugger"
    UI_REVIEWER = "ui_reviewer"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class ScreenContext:
    """Current screen context detected from shared screen"""
    content_type: str  # code, terminal, browser, documentation
    active_file: Optional[str] = None
    detected_language: Optional[str] = None
    ui_elements: List[str] = None
    error_indicators: List[str] = None
    terminal_output: Optional[str] = None
    timestamp: float = None

@dataclass
class AgentTask:
    """Task definition for parallel agents"""
    agent_type: AgentType
    priority: int
    context: ScreenContext
    specific_task: str
    callback: Optional[Callable] = None
    status: str = "pending"  # pending, running, completed, failed

class CognitiveWorkflowIntegration:
    """
    Integrates Cognitive OS screen sharing into development workflow
    Manages parallel agents based on screen context
    """
    
    def __init__(self):
        self.screen_context_queue = queue.Queue()
        self.agent_task_queue = queue.Queue()
        self.active_agents: Dict[str, Dict] = {}
        self.screen_context: Optional[ScreenContext] = None
        self.workflow_active = False
        self.context_analyzer_thread = None
        self.agent_manager_thread = None
        
        # WebSocket connection to Cognitive OS
        self.websocket_url = 'ws://localhost:8084/ws'
        self.ws_connection = None
        
        # Context patterns for detection
        self.context_patterns = {
            'code_editing': ['def ', 'class ', 'import ', 'function', 'const ', 'let '],
            'terminal': ['$', '>', 'npm', 'python', 'git', 'cd ', 'ls'],
            'error': ['Error:', 'Exception', 'Failed', 'TypeError', 'undefined'],
            'testing': ['test', 'describe', 'it(', 'expect', 'assert'],
            'documentation': ['README', '##', 'markdown', '.md', 'docs/']
        }
        
    async def start_workflow(self):
        """Start the cognitive workflow integration"""
        print("🧬 COGNITIVE WORKFLOW INTEGRATION STARTING")
        print("=" * 60)
        
        # Ensure Cognitive OS is running
        if not self._check_cognitive_os():
            print("⚠️  Starting Cognitive OS first...")
            self._start_cognitive_os()
            await asyncio.sleep(3)
        
        # Start workflow components
        self.workflow_active = True
        
        # Start context analyzer thread
        self.context_analyzer_thread = threading.Thread(
            target=self._context_analyzer_loop,
            daemon=True
        )
        self.context_analyzer_thread.start()
        
        # Start agent manager thread
        self.agent_manager_thread = threading.Thread(
            target=self._agent_manager_loop,
            daemon=True
        )
        self.agent_manager_thread.start()
        
        # Connect to WebSocket for screen data
        await self._connect_to_screen_stream()
        
        print("\n✅ Workflow integration active!")
        print("📋 Monitoring screen for context changes...")
        print("🤖 Agents ready for parallel execution")
        
    def _check_cognitive_os(self) -> bool:
        """Check if Cognitive OS is running"""
        try:
            status = tools.cognitive_status()
            return status.get('active_sessions', 0) > 0
        except:
            return False
    
    def _start_cognitive_os(self):
        """Start Cognitive OS if not running"""
        subprocess.Popen([
            'python3', 
            os.path.join(os.path.dirname(__file__), 'start_cognitive_silent.py')
        ])
    
    async def _connect_to_screen_stream(self):
        """Connect to Cognitive OS WebSocket for screen data"""
        import websockets
        
        try:
            self.ws_connection = await websockets.connect(self.websocket_url)
            print(f"🔗 Connected to Cognitive OS WebSocket")
            
            # Listen for screen frames
            async for message in self.ws_connection:
                try:
                    data = json.loads(message)
                    if data.get('type') == 'screen_frame':
                        # Process screen frame
                        context = self._analyze_screen_frame(data)
                        if context:
                            self.screen_context_queue.put(context)
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    def _analyze_screen_frame(self, frame_data: Dict) -> Optional[ScreenContext]:
        """Analyze screen frame to determine context"""
        # In real implementation, this would use OCR or AI vision
        # For now, simulate based on frame metadata
        
        context = ScreenContext(
            content_type="code",  # Would be detected from actual frame
            timestamp=time.time()
        )
        
        # Simulate context detection (in reality, would analyze actual frame)
        # This is where AI vision would identify what's on screen
        
        return context
    
    def _context_analyzer_loop(self):
        """Continuously analyze screen context and spawn appropriate agents"""
        print("🔍 Context analyzer started")
        
        while self.workflow_active:
            try:
                # Get latest screen context
                context = self.screen_context_queue.get(timeout=1)
                self.screen_context = context
                
                # Determine what agents would be helpful
                suggested_agents = self._suggest_agents_for_context(context)
                
                # Queue agent tasks
                for agent_type, task_desc in suggested_agents:
                    task = AgentTask(
                        agent_type=agent_type,
                        priority=self._calculate_priority(agent_type, context),
                        context=context,
                        specific_task=task_desc
                    )
                    self.agent_task_queue.put(task)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Context analyzer error: {e}")
    
    def _suggest_agents_for_context(self, context: ScreenContext) -> List[tuple]:
        """Suggest which agents would be helpful for current context"""
        suggestions = []
        
        # Context-based agent suggestions
        if context.content_type == "code":
            if context.detected_language:
                suggestions.append((
                    AgentType.CODE_ANALYZER,
                    f"Analyze {context.detected_language} code for improvements"
                ))
                suggestions.append((
                    AgentType.TEST_GENERATOR,
                    f"Generate tests for visible {context.detected_language} code"
                ))
        
        if context.error_indicators:
            suggestions.append((
                AgentType.DEBUGGING,
                f"Debug errors: {', '.join(context.error_indicators)}"
            ))
        
        if context.content_type == "terminal" and context.terminal_output:
            if "test" in context.terminal_output.lower():
                suggestions.append((
                    AgentType.TEST_GENERATOR,
                    "Analyze test results and suggest improvements"
                ))
        
        return suggestions
    
    def _calculate_priority(self, agent_type: AgentType, context: ScreenContext) -> int:
        """Calculate priority for agent task based on context"""
        # Higher number = higher priority
        base_priority = 5
        
        # Boost priority for errors
        if context.error_indicators:
            base_priority += 3
        
        # Boost priority for debugging agents when errors present
        if agent_type == AgentType.DEBUGGING and context.error_indicators:
            base_priority += 2
        
        return base_priority
    
    def _agent_manager_loop(self):
        """Manage parallel agent execution"""
        print("🤖 Agent manager started")
        max_parallel_agents = 4
        
        while self.workflow_active:
            try:
                # Check if we can spawn more agents
                if len(self.active_agents) < max_parallel_agents:
                    # Get highest priority task
                    task = self.agent_task_queue.get(timeout=1)
                    
                    # Spawn agent in separate terminal
                    agent_id = f"{task.agent_type.value}_{int(time.time())}"
                    self._spawn_agent(agent_id, task)
                
                # Monitor active agents
                self._monitor_active_agents()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Agent manager error: {e}")
    
    def _spawn_agent(self, agent_id: str, task: AgentTask):
        """Spawn an agent in a separate terminal"""
        print(f"🚀 Spawning {task.agent_type.value} agent: {agent_id}")
        
        # Create agent script
        agent_script = self._generate_agent_script(agent_id, task)
        script_path = f"/tmp/agent_{agent_id}.py"
        
        with open(script_path, 'w') as f:
            f.write(agent_script)
        
        # Spawn in terminal
        terminal = tools.spawn_terminal(
            title=f"Agent: {task.agent_type.value}",
            command=f"python3 {script_path}"
        )
        
        if terminal['success']:
            self.active_agents[agent_id] = {
                'task': task,
                'terminal_pid': terminal['pid'],
                'start_time': time.time(),
                'status': 'running'
            }
            task.status = 'running'
    
    def _generate_agent_script(self, agent_id: str, task: AgentTask) -> str:
        """Generate Python script for agent execution"""
        return f'''#!/usr/bin/env python3
"""
Auto-generated agent: {agent_id}
Type: {task.agent_type.value}
Task: {task.specific_task}
"""

import time
import json

def main():
    print("🤖 Agent {agent_id} starting...")
    print("📋 Task: {task.specific_task}")
    print("🎯 Context: {task.context.content_type}")
    
    # Simulate agent work
    print("\\n⚙️  Processing...")
    time.sleep(5)  # Simulate work
    
    # In real implementation, agent would:
    # 1. Analyze the context
    # 2. Perform its specialized task
    # 3. Report results back
    
    result = {{
        "agent_id": "{agent_id}",
        "task": "{task.specific_task}",
        "status": "completed",
        "recommendations": [
            "Example recommendation 1",
            "Example recommendation 2"
        ]
    }}
    
    print("\\n✅ Task completed!")
    print(f"📊 Results: {{json.dumps(result, indent=2)}}")
    
    # Save results
    with open(f"/tmp/agent_{agent_id}_results.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
'''
    
    def _monitor_active_agents(self):
        """Monitor and clean up completed agents"""
        completed = []
        
        for agent_id, agent_info in self.active_agents.items():
            # Check if terminal is still running
            pid = agent_info['terminal_pid']
            try:
                # Check if process exists
                os.kill(pid, 0)
            except OSError:
                # Process has ended
                completed.append(agent_id)
                print(f"✅ Agent completed: {agent_id}")
                
                # Check for results
                results_file = f"/tmp/agent_{agent_id}_results.json"
                if os.path.exists(results_file):
                    with open(results_file, 'r') as f:
                        results = json.load(f)
                        self._process_agent_results(agent_id, results)
        
        # Clean up completed agents
        for agent_id in completed:
            del self.active_agents[agent_id]
    
    def _process_agent_results(self, agent_id: str, results: Dict):
        """Process results from completed agent"""
        print(f"📊 Processing results from {agent_id}")
        # In real implementation, would integrate results into workflow
        
    def get_workflow_status(self) -> Dict:
        """Get current workflow status"""
        return {
            'active': self.workflow_active,
            'current_context': self.screen_context.content_type if self.screen_context else None,
            'active_agents': len(self.active_agents),
            'queued_tasks': self.agent_task_queue.qsize(),
            'agents': [
                {
                    'id': agent_id,
                    'type': info['task'].agent_type.value,
                    'task': info['task'].specific_task,
                    'runtime': time.time() - info['start_time']
                }
                for agent_id, info in self.active_agents.items()
            ]
        }

# Convenience functions for integration
_workflow_integration = None

def start_cognitive_workflow():
    """Start the cognitive workflow integration"""
    global _workflow_integration
    _workflow_integration = CognitiveWorkflowIntegration()
    
    # Run in asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_workflow_integration.start_workflow())
    
    return _workflow_integration

def get_workflow_status():
    """Get current workflow status"""
    if _workflow_integration:
        return _workflow_integration.get_workflow_status()
    return {'active': False, 'error': 'Workflow not started'}

def spawn_custom_agent(agent_type: AgentType, task_description: str, priority: int = 5):
    """Manually spawn a custom agent"""
    if not _workflow_integration:
        return {'error': 'Workflow not active'}
    
    task = AgentTask(
        agent_type=agent_type,
        priority=priority,
        context=_workflow_integration.screen_context or ScreenContext(content_type="manual"),
        specific_task=task_description
    )
    
    _workflow_integration.agent_task_queue.put(task)
    return {'success': True, 'task_queued': task_description}

if __name__ == "__main__":
    # Example usage
    print("🧬 COGNITIVE WORKFLOW INTEGRATION DEMO")
    print("This system monitors your screen and spawns helpful agents")
    workflow = start_cognitive_workflow()