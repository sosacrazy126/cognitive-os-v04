#!/bin/bash

echo "🧬 Cognitive Operating System v0.4 - Test Runner"
echo "============================================================"

cd /home/evilbastardxd/cognitive-os-v04

echo "📁 Working directory: $(pwd)"
echo "🔍 Checking Python files:"
ls -la *.py | head -10

echo ""
echo "🚀 Starting Method 1: Automatic Full Test"
echo "Following README instructions exactly..."

# Try to run the test
python3 -c "from quick_screen_test import start_full_screen_test; start_full_screen_test()" 2>&1

echo ""
echo "✅ Test execution completed"
