#!/usr/bin/env python3
"""
Simple test runner for Cognitive OS v0.4
Following the README instructions exactly
"""

import os
import sys
import subprocess
import time

def main():
    print("🧬 Cognitive Operating System v0.4 - Test Runner")
    print("=" * 60)
    
    # Change to the correct directory
    cognitive_dir = "/home/evilbastardxd/cognitive-os-v04"
    os.chdir(cognitive_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Add current directory to Python path
    sys.path.insert(0, cognitive_dir)
    
    print("\n🚀 Starting Method 1: Automatic Full Test")
    print("Following README instructions exactly...")
    
    try:
        # Method 1 from README: Automatic Full Test
        print("\n🔧 Executing: python -c \"from quick_screen_test import start_full_screen_test; start_full_screen_test()\"")
        
        # Import and run the function directly
        from quick_screen_test import start_full_screen_test
        start_full_screen_test()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔍 Let's check what files exist:")
        files = os.listdir(cognitive_dir)
        for f in sorted(files):
            if f.endswith('.py'):
                print(f"  ✅ {f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Try to provide more debugging info
        print("\n🔍 Debugging information:")
        print(f"Python path: {sys.path[:3]}")
        print(f"Current working directory: {os.getcwd()}")
        
        # Check if the quick_screen_test.py file exists and is readable
        test_file = os.path.join(cognitive_dir, "quick_screen_test.py")
        if os.path.exists(test_file):
            print(f"✅ {test_file} exists")
            try:
                with open(test_file, 'r') as f:
                    first_lines = f.readlines()[:5]
                print("📄 First few lines of quick_screen_test.py:")
                for i, line in enumerate(first_lines, 1):
                    print(f"  {i}: {line.rstrip()}")
            except Exception as read_error:
                print(f"❌ Cannot read file: {read_error}")
        else:
            print(f"❌ {test_file} does not exist")

if __name__ == "__main__":
    main()
