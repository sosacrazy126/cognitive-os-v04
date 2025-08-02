#!/usr/bin/env python3

import subprocess
import sys
import os

def run_connection_test():
    """Run the connection test"""
    print("🧬 Running Connection Test...")
    
    # Change to the cognitive OS directory
    os.chdir('/home/evilbastardxd/cognitive-os-v04')
    
    # Run the connection test
    try:
        result = subprocess.run([
            sys.executable, 'test_connection.py'
        ], capture_output=True, text=True, timeout=30)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    run_connection_test()
