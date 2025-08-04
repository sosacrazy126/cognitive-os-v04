#!/usr/bin/env python3
"""
Quick Cognitive Prompt - Enter a single prompt with automatic sleep mode
"""

import sys
import time
from session_prompt_handler import SessionPromptHandler

def quick_prompt_with_sleep(prompt_text: str = None, sleep_seconds: int = 5):
    """Process a quick prompt and enter sleep mode"""
    
    print("🧬 COGNITIVE OS - QUICK PROMPT MODE")
    print("=" * 50)
    
    # Get prompt from command line or user input
    if not prompt_text:
        if len(sys.argv) > 1:
            prompt_text = " ".join(sys.argv[1:])
        else:
            prompt_text = input("🧠 Enter your cognitive prompt: ").strip()
    
    if not prompt_text:
        print("❌ No prompt provided")
        return
    
    # Process the prompt
    print(f"\n📝 Processing: {prompt_text}")
    print("🧠 Analyzing context and intent...")
    time.sleep(1)
    
    # Generate response (simplified version)
    prompt_lower = prompt_text.lower()
    
    if any(word in prompt_lower for word in ['error', 'bug', 'debug']):
        response = "🔍 Debug analysis initiated. I'll examine error patterns and suggest solutions."
    elif any(word in prompt_lower for word in ['test', 'testing']):
        response = "🧪 Test generation mode activated. Creating comprehensive test coverage."
    elif any(word in prompt_lower for word in ['refactor', 'improve']):
        response = "🔧 Refactoring assistant engaged. Analyzing code for improvement opportunities."
    elif any(word in prompt_lower for word in ['screen', 'visual', 'see']):
        response = "👁️  Screen analysis active. Processing visual context for relevant assistance."
    else:
        response = f"🤖 Cognitive processing complete. Ready to assist with: '{prompt_text}'"
    
    print(f"🤖 Response: {response}")
    
    # Enter sleep mode
    print(f"\n😴 Entering sleep mode for {sleep_seconds} seconds...")
    print("💤 System will be in low-power cognitive state")
    
    for i in range(sleep_seconds, 0, -1):
        print(f"💤 Sleep mode: {i}s remaining", end='\r')
        time.sleep(1)
    
    print("🌅 Awakening from sleep mode!        ")
    print("✅ Cognitive OS ready for next interaction")

if __name__ == "__main__":
    # Check for sleep duration argument
    sleep_duration = 5
    args = sys.argv[1:]
    
    # Look for --sleep argument
    if '--sleep' in args:
        sleep_idx = args.index('--sleep')
        if sleep_idx + 1 < len(args):
            try:
                sleep_duration = int(args[sleep_idx + 1])
                # Remove sleep args from prompt
                args = args[:sleep_idx] + args[sleep_idx + 2:]
            except ValueError:
                print("❌ Invalid sleep duration, using 5 seconds")
                args = args[:sleep_idx] + args[sleep_idx + 2:]
    
    prompt = " ".join(args) if args else None
    quick_prompt_with_sleep(prompt, sleep_duration)