#!/usr/bin/env python3
"""
Simple test runner for Cognitive OS
"""

import subprocess
import sys
import os
import time

def cleanup_processes():
    """Clean up any existing processes"""
    print("🧹 Cleaning up existing processes...")
    try:
        subprocess.run(['pkill', '-f', 'enhanced_cognitive_daemon'], timeout=5, capture_output=True)
        subprocess.run(['pkill', '-f', 'auto_screen_test'], timeout=5, capture_output=True)
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    time.sleep(1)

def start_daemon():
    """Start the enhanced cognitive daemon"""
    print("🚀 Starting Enhanced Cognitive Daemon...")
    
    # Start daemon in background
    daemon_cmd = [
        sys.executable, 
        '/home/evilbastardxd/cognitive-os-v04/enhanced_cognitive_daemon.py'
    ]
    
    with