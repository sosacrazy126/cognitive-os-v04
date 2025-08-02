#!/usr/bin/env python3
"""
Session Prompt Handler - Interactive prompt system for Cognitive OS
Allows entering prompts into the session with sleep mode functionality
"""

import time
import sys
import threading
from typing import Dict, Any, Optional
import json
from datetime import datetime

class SessionPromptHandler:
    """
    Handles interactive prompts and session management for Cognitive OS
    """
    
    def __init__(self):
        self.session_active = False
        self.sleep_mode = False
        self.prompt_history = []
        self.session_start_time = None
        self.last_activity = None
        
    def start_prompt_session(self):
        """Start interactive prompt session"""
        print("🧬 COGNITIVE OS v0.4 - INTERACTIVE PROMPT SESSION")
        print("=" * 60)
        print("🎯 Commands:")
        print("  /sleep <seconds> - Enter sleep mode")
        print("  /status - Show session status")
        print("  /history - Show prompt history")
        print("  /clear - Clear screen")
        print("  /exit - Exit session")
        print("  <any text> - Process as cognitive prompt")
        print("=" * 60)
        
        self.session_active = True
        self.session_start_time = datetime.now()
        self.last_activity = datetime.now()
        
        try:
            while self.session_active:
                if not self.sleep_mode:
                    self._handle_prompt_input()
                else:
                    time.sleep(0.1)  # Brief sleep while in sleep mode
        except KeyboardInterrupt:
            print("\n🛑 Session interrupted by user")
        finally:
            self._end_session()
    
    def _handle_prompt_input(self):
        """Handle user prompt input"""
        try:
            prompt = input("\n🧠 cognitive> ").strip()
            
            if not prompt:
                return
            
            self.last_activity = datetime.now()
            
            # Handle commands
            if prompt.startswith('/'):
                self._process_command(prompt)
            else:
                self._process_cognitive_prompt(prompt)
                
        except EOFError:
            print("\n🛑 EOF received, ending session")
            self.session_active = False
    
    def _process_command(self, command: str):
        """Process session commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == '/sleep':
            seconds = 5  # default
            if len(parts) > 1:
                try:
                    seconds = int(parts[1])
                except ValueError:
                    print("❌ Invalid sleep duration, using 5 seconds")
            
            self._enter_sleep_mode(seconds)
            
        elif cmd == '/status':
            self._show_session_status()
            
        elif cmd == '/history':
            self._show_prompt_history()
            
        elif cmd == '/clear':
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
            
        elif cmd == '/exit':
            print("👋 Ending cognitive session...")
            self.session_active = False
            
        else:
            print(f"❌ Unknown command: {cmd}")
            print("💡 Try /sleep, /status, /history, /clear, or /exit")
    
    def _process_cognitive_prompt(self, prompt: str):
        """Process a cognitive prompt"""
        timestamp = datetime.now()
        
        print(f"\n📝 Processing cognitive prompt...")
        print(f"🎯 Input: {prompt}")
        
        # Store in history
        prompt_entry = {
            'timestamp': timestamp.isoformat(),
            'prompt': prompt,
            'type': 'cognitive',
            'processed': True
        }
        self.prompt_history.append(prompt_entry)
        
        # Simulate cognitive processing
        print("🧠 Analyzing context and intent...")
        time.sleep(1)
        
        # Mock response based on prompt content
        response = self._generate_mock_response(prompt)
        print(f"🤖 Response: {response}")
        
        # Update prompt entry with response
        prompt_entry['response'] = response
        
        print("✅ Prompt processed and integrated into cognitive session")
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock cognitive response"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['error', 'bug', 'problem', 'issue']):
            return "I can help debug this issue. Let me analyze the error patterns and suggest solutions."
            
        elif any(word in prompt_lower for word in ['test', 'testing', 'spec']):
            return "I'll generate comprehensive tests for this functionality and optimize coverage."
            
        elif any(word in prompt_lower for word in ['refactor', 'improve', 'optimize']):
            return "I can suggest refactoring approaches to improve code quality and maintainability."
            
        elif any(word in prompt_lower for word in ['document', 'docs', 'explain']):
            return "I'll create clear documentation and explanations for this code or concept."
            
        elif any(word in prompt_lower for word in ['screen', 'visual', 'see']):
            return "I'm analyzing the screen content to understand the current context and provide relevant assistance."
            
        else:
            return f"I understand you want help with: '{prompt}'. I'm ready to assist with cognitive analysis and solution generation."
    
    def _enter_sleep_mode(self, seconds: int):
        """Enter sleep mode for specified duration"""
        print(f"😴 Entering sleep mode for {seconds} seconds...")
        print("🔄 Session will resume automatically")
        
        self.sleep_mode = True
        
        # Show countdown
        for i in range(seconds, 0, -1):
            print(f"💤 Sleep mode: {i}s remaining", end='\r')
            time.sleep(1)
        
        print("🌅 Waking up from sleep mode!           ")
        self.sleep_mode = False
        print("✅ Session resumed - ready for prompts")
    
    def _show_session_status(self):
        """Show current session status"""
        uptime = datetime.now() - self.session_start_time
        last_activity_ago = datetime.now() - self.last_activity
        
        print("\n📊 COGNITIVE SESSION STATUS")
        print("=" * 40)
        print(f"🕐 Session uptime: {uptime}")
        print(f"⚡ Last activity: {last_activity_ago.seconds}s ago")
        print(f"📝 Prompts processed: {len(self.prompt_history)}")
        print(f"😴 Sleep mode: {'Active' if self.sleep_mode else 'Inactive'}")
        print(f"🧬 Session state: {'Active' if self.session_active else 'Inactive'}")
    
    def _show_prompt_history(self):
        """Show prompt history"""
        if not self.prompt_history:
            print("📝 No prompts in history yet")
            return
        
        print(f"\n📚 PROMPT HISTORY ({len(self.prompt_history)} entries)")
        print("=" * 50)
        
        for i, entry in enumerate(self.prompt_history[-10:], 1):  # Show last 10
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%H:%M:%S")
            print(f"{i}. [{timestamp}] {entry['prompt'][:50]}{'...' if len(entry['prompt']) > 50 else ''}")
    
    def _end_session(self):
        """End the session and cleanup"""
        end_time = datetime.now()
        session_duration = end_time - self.session_start_time
        
        print("\n🏁 COGNITIVE SESSION ENDED")
        print("=" * 40)
        print(f"📊 Session duration: {session_duration}")
        print(f"📝 Total prompts processed: {len(self.prompt_history)}")
        
        # Save session log
        if self.prompt_history:
            log_filename = f"cognitive_session_{end_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_filename, 'w') as f:
                session_data = {
                    'session_start': self.session_start_time.isoformat(),
                    'session_end': end_time.isoformat(),
                    'duration_seconds': session_duration.total_seconds(),
                    'prompt_count': len(self.prompt_history),
                    'prompts': self.prompt_history
                }
                json.dump(session_data, f, indent=2)
            
            print(f"💾 Session log saved: {log_filename}")
        
        print("👋 Thank you for using Cognitive OS!")

def start_interactive_session():
    """Start an interactive cognitive prompt session"""
    handler = SessionPromptHandler()
    handler.start_prompt_session()

if __name__ == "__main__":
    start_interactive_session()