#!/usr/bin/env python3
"""
Comprehensive Test Suite for Cognitive OS v0.4
Tests all components thoroughly before any commits
"""

import time
import sys
import subprocess
import json
import os
from typing import Dict, List, Any
import threading
import signal

class CognitiveOSTestSuite:
    """Comprehensive testing for all Cognitive OS components"""
    
    def __init__(self):
        self.test_results: List[Dict] = []
        self.daemon_pid: int = None
        self.test_session_id: str = None
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧬 COGNITIVE OS v0.4 - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print("Testing all components before commit...")
        print()
        
        try:
            # Core system tests
            self.test_imports()
            self.test_basic_functionality()
            self.test_terminal_control()
            self.test_session_persistence()
            
            # WebSocket and daemon tests
            self.test_daemon_startup()
            self.test_websocket_connection()
            
            # Prompt system tests
            self.test_prompt_system()
            self.test_interactive_session()
            
            # Integration tests
            self.test_tool_integration()
            self.test_error_handling()
            
            # Performance tests
            self.test_performance()
            
            # Cleanup
            self.cleanup_test_environment()
            
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            self.cleanup_test_environment()
        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
            self.cleanup_test_environment()
        finally:
            self.print_test_summary()
    
    def test_imports(self):
        """Test all module imports"""
        print("1️⃣ Testing module imports...")
        
        try:
            import tools
            self.log_test("tools.py import", True, "Main module imported successfully")
            
            from session_prompt_handler import SessionPromptHandler
            self.log_test("session_prompt_handler import", True, "Prompt handler imported")
            
            from cognitive_prompt import quick_prompt_with_sleep
            self.log_test("cognitive_prompt import", True, "Quick prompt imported")
            
            import cognitive_tool_integration
            self.log_test("cognitive_tool_integration import", True, "Tool integration imported")
            
        except Exception as e:
            self.log_test("imports", False, f"Import error: {e}")
    
    def test_basic_functionality(self):
        """Test basic system functionality"""
        print("2️⃣ Testing basic functionality...")
        
        try:
            import tools
            
            # Test system info
            info = tools.get_terminal_info()
            self.log_test("get_terminal_info", 
                         info.get('platform') is not None, 
                         f"Platform: {info.get('platform', 'unknown')}")
            
            # Test available terminals
            terminals = tools.get_available_terminals()
            self.log_test("get_available_terminals", 
                         len(terminals) > 0, 
                         f"Found {len(terminals)} terminals")
            
            # Test command execution
            result = tools.execute_command("echo 'Test command'")
            self.log_test("execute_command", 
                         result.get('success', False), 
                         f"Output: {result.get('output', 'None')[:50]}")
            
        except Exception as e:
            self.log_test("basic_functionality", False, f"Error: {e}")
    
    def test_terminal_control(self):
        """Test terminal spawning and control"""
        print("3️⃣ Testing terminal control...")
        
        try:
            import tools
            
            # Test terminal spawning
            terminal = tools.spawn_terminal(
                title="Test Terminal",
                command="echo 'Terminal test' && sleep 2"
            )
            
            success = 'pid' in terminal
            self.log_test("spawn_terminal", success, 
                         f"PID: {terminal.get('pid', 'None')}")
            
            if success:
                # Wait a moment then check if process exists
                time.sleep(1)
                try:
                    os.kill(terminal['pid'], 0)  # Check if process exists
                    self.log_test("terminal_process_running", True, "Process active")
                except OSError:
                    self.log_test("terminal_process_running", False, "Process not found")
            
        except Exception as e:
            self.log_test("terminal_control", False, f"Error: {e}")
    
    def test_session_persistence(self):
        """Test session persistence functionality"""
        print("4️⃣ Testing session persistence...")
        
        try:
            import tools
            
            # Test session manager
            session_mgr = tools.SessionManager()
            self.log_test("session_manager_init", True, "SessionManager initialized")
            
            # Test database schema
            sessions = session_mgr.list_sessions()
            self.log_test("list_sessions", True, f"Found {len(sessions)} sessions")
            
            # Test cognitive status
            status = tools.cognitive_status()
            self.log_test("cognitive_status", 
                         'active_sessions' in status, 
                         f"Active sessions: {status.get('active_sessions', 0)}")
            
        except Exception as e:
            self.log_test("session_persistence", False, f"Error: {e}")
    
    def test_daemon_startup(self):
        """Test daemon startup and management"""
        print("5️⃣ Testing daemon startup...")
        
        try:
            # Check if daemon is already running
            result = subprocess.run(['pgrep', '-f', 'enhanced_cognitive_daemon'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                self.daemon_pid = int(result.stdout.strip().split('\n')[0])
                self.log_test("daemon_already_running", True, f"PID: {self.daemon_pid}")
            else:
                # Start daemon for testing
                proc = subprocess.Popen([
                    sys.executable, 'enhanced_cognitive_daemon.py'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                time.sleep(3)  # Wait for startup
                
                if proc.poll() is None:  # Still running
                    self.daemon_pid = proc.pid
                    self.log_test("daemon_startup", True, f"Started PID: {self.daemon_pid}")
                else:
                    self.log_test("daemon_startup", False, "Failed to start")
            
        except Exception as e:
            self.log_test("daemon_startup", False, f"Error: {e}")
    
    def test_websocket_connection(self):
        """Test WebSocket connectivity"""
        print("6️⃣ Testing WebSocket connection...")
        
        try:
            import websockets
            import asyncio
            
            async def test_ws():
                try:
                    async with websockets.connect('ws://localhost:8084/ws') as ws:
                        # Send test message
                        test_msg = json.dumps({
                            'type': 'test',
                            'message': 'Test suite connection'
                        })
                        await ws.send(test_msg)
                        
                        # Wait for response
                        response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        return json.loads(response)
                except Exception as e:
                    return {'error': str(e)}
            
            # Run async test
            response = asyncio.run(test_ws())
            
            if 'error' not in response:
                self.log_test("websocket_connection", True, f"Connected: {response.get('type', 'unknown')}")
            else:
                self.log_test("websocket_connection", False, f"Error: {response['error']}")
                
        except Exception as e:
            self.log_test("websocket_connection", False, f"Error: {e}")
    
    def test_prompt_system(self):
        """Test the new prompt system"""
        print("7️⃣ Testing prompt system...")
        
        try:
            import tools
            
            # Test quick prompt
            result = tools.enter_cognitive_prompt("test prompt for system validation", 1)
            self.log_test("quick_prompt", 
                         result.get('success', False), 
                         result.get('message', 'No message'))
            
            # Test different prompt types
            prompts = [
                ("debug error analysis", "debug"),
                ("generate unit tests", "test"),
                ("refactor code structure", "refactor"),
                ("screen content analysis", "screen")
            ]
            
            for prompt_text, prompt_type in prompts:
                result = tools.enter_cognitive_prompt(prompt_text, 1)
                self.log_test(f"prompt_type_{prompt_type}", 
                             result.get('success', False),
                             f"Processed {prompt_type} prompt")
            
        except Exception as e:
            self.log_test("prompt_system", False, f"Error: {e}")
    
    def test_interactive_session(self):
        """Test interactive session functionality"""
        print("8️⃣ Testing interactive session...")
        
        try:
            # Test session handler creation
            from session_prompt_handler import SessionPromptHandler
            handler = SessionPromptHandler()
            self.log_test("session_handler_init", True, "Handler created")
            
            # Test session data structures
            self.log_test("session_data_structures", 
                         hasattr(handler, 'prompt_history') and hasattr(handler, 'session_active'),
                         "Data structures present")
            
        except Exception as e:
            self.log_test("interactive_session", False, f"Error: {e}")
    
    def test_tool_integration(self):
        """Test tool integration functionality"""
        print("9️⃣ Testing tool integration...")
        
        try:
            import cognitive_tool_integration
            
            # Test integration initialization
            integration = cognitive_tool_integration.CognitiveToolIntegration()
            self.log_test("tool_integration_init", True, "Integration initialized")
            
            # Test enhanced read simulation
            result = integration.enhanced_read_file("test_file.py")
            self.log_test("enhanced_read", 
                         'content' in result,
                         f"Analysis: {result.get('context_analysis', {})}")
            
        except Exception as e:
            self.log_test("tool_integration", False, f"Error: {e}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("🔟 Testing error handling...")
        
        try:
            import tools
            
            # Test invalid command
            result = tools.execute_command("nonexistent_command_12345")
            self.log_test("invalid_command_handling", 
                         not result.get('success', True),
                         "Invalid command properly handled")
            
            # Test empty prompt
            result = tools.enter_cognitive_prompt("", 1)
            self.log_test("empty_prompt_handling", 
                         not result.get('success', True),
                         "Empty prompt handled gracefully")
            
            # Test invalid sleep duration
            try:
                from cognitive_prompt import quick_prompt_with_sleep
                # This should handle negative sleep gracefully
                quick_prompt_with_sleep("test", -1)
                self.log_test("negative_sleep_handling", True, "Handled negative sleep duration")
            except Exception:
                self.log_test("negative_sleep_handling", False, "Failed to handle negative sleep")
            
        except Exception as e:
            self.log_test("error_handling", False, f"Error: {e}")
    
    def test_performance(self):
        """Test system performance"""
        print("1️⃣1️⃣ Testing performance...")
        
        try:
            import tools
            
            # Test command execution speed
            start_time = time.time()
            for i in range(5):
                tools.execute_command(f"echo 'Performance test {i}'")
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 5
            self.log_test("command_execution_speed", 
                         avg_time < 1.0,
                         f"Average: {avg_time:.3f}s per command")
            
            # Test prompt processing speed
            start_time = time.time()
            for i in range(3):
                tools.enter_cognitive_prompt(f"performance test prompt {i}", 0)
            end_time = time.time()
            
            avg_prompt_time = (end_time - start_time) / 3
            self.log_test("prompt_processing_speed",
                         avg_prompt_time < 2.0,
                         f"Average: {avg_prompt_time:.3f}s per prompt")
            
        except Exception as e:
            self.log_test("performance", False, f"Error: {e}")
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        
        # Clean up any test session logs
        import glob
        for log_file in glob.glob("cognitive_session_*.json"):
            if "test" in log_file.lower():
                try:
                    os.remove(log_file)
                    print(f"   Removed test log: {log_file}")
                except:
                    pass
        
        print("✅ Cleanup complete")
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}: {details}")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🧬 COMPREHENSIVE TEST SUITE RESULTS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n🎯 COMMIT READINESS ASSESSMENT:")
        if failed_tests == 0:
            print("✅ ALL TESTS PASSED - READY FOR COMMIT! 🚀")
        elif failed_tests <= 2:
            print("⚠️  MOSTLY READY - Review failed tests before commit")
        else:
            print("❌ NOT READY - Fix failing tests before commit")
        
        # Save detailed results
        results_file = f"test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': passed_tests/total_tests*100
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved: {results_file}")

def main():
    """Run the comprehensive test suite"""
    test_suite = CognitiveOSTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()