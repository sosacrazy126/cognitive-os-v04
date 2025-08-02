# 🚀 Cognitive Operating System v0.4 - Installation Guide

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 100MB for system files
- **Network**: Internet connection for dependencies

### Required Software
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install system dependencies
sudo apt install sqlite3 gnome-terminal firefox -y

# Install window management tools (Linux)
sudo apt install wmctrl xdotool -y
```

## 📦 Python Dependencies

### Install Required Packages
```bash
# Core dependencies
pip3 install --user pillow websockets psutil blessed

# Optional but recommended
pip3 install --user opencv-python numpy

# For development and testing
pip3 install --user pytest asyncio
```

### Verify Installation
```bash
python3 -c "
import PIL, websockets, psutil, blessed
print('✅ All core dependencies installed successfully')
"
```

## 🔧 Quick Installation

### Method 1: Direct Setup
```bash
# 1. Create project directory
mkdir -p ~/cognitive-os-v04
cd ~/cognitive-os-v04

# 2. Copy all project files to this directory
# (Files should already be copied if you followed the folder creation)

# 3. Make scripts executable
chmod +x *.py

# 4. Test installation
python3 -c "import tools; print('✅ Cognitive OS installed successfully')"
```

### Method 2: Automated Setup Script
```bash
# Create automated installer
cat > install_cognitive_os.sh << 'EOF'
#!/bin/bash
echo "🧬 Installing Cognitive Operating System v0.4..."

# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip sqlite3 gnome-terminal firefox wmctrl xdotool

# Install Python packages
pip3 install --user pillow websockets psutil blessed opencv-python

# Verify installation
python3 -c "
import tools
print('✅ Cognitive OS v0.4 installation complete!')
print('🚀 Ready for cognitive fusion!')
"

echo "🎯 Installation complete! Run: python3 -c \"from quick_screen_test import start_full_screen_test; start_full_screen_test()\""
EOF

# Make executable and run
chmod +x install_cognitive_os.sh
./install_cognitive_os.sh
```

## 🧪 Verification Tests

### Test 1: Core System
```bash
python3 -c "
import tools
print('Testing terminal control...')
result = tools.execute_command('echo \"Installation test\"')
print(f'✅ Terminal control: {\"OK\" if result[\"success\"] else \"FAILED\"}')
"
```

### Test 2: Cognitive Features
```bash
python3 -c "
import tools
print('Testing cognitive orchestrator...')
# This will show error if dependencies are missing
try:
    status = tools.cognitive_status()
    print('✅ Cognitive orchestrator: OK')
except Exception as e:
    print(f'❌ Cognitive orchestrator: {e}')
"
```

### Test 3: Screen Capture Dependencies
```bash
python3 -c "
try:
    from PIL import Image
    import websockets
    import asyncio
    print('✅ Screen capture dependencies: OK')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
"
```

### Test 4: Full System Test
```bash
# Run comprehensive test
python3 session_persistence_test.py
```

## 🌐 Browser Setup

### Firefox Configuration (Recommended)
```bash
# Install Firefox if not present
sudo apt install firefox -y

# Test browser screen capture support
firefox enhanced_screen_capture.html
```

### Chrome/Chromium Alternative
```bash
# Install Chromium
sudo apt install chromium-browser -y

# Launch with required flags for screen capture
chromium-browser --enable-features=VaapiVideoDecoder --use-gl=desktop enhanced_screen_capture.html
```

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# Add to ~/.bashrc for persistent settings
echo 'export COGNITIVE_OS_HOME=~/cognitive-os-v04' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:$COGNITIVE_OS_HOME' >> ~/.bashrc
source ~/.bashrc
```

### Database Initialization
```bash
# Initialize cognitive OS databases (automatic on first run)
python3 -c "
import tools
session_mgr = tools.SessionManager()
print('✅ Database initialized')
"
```

## 🚀 First Run

### Quick Start Test
```bash
# Run the automated full test
python3 -c "from quick_screen_test import start_full_screen_test; start_full_screen_test()"
```

This will:
1. ✅ Start the Enhanced Cognitive Daemon
2. 🌐 Open Firefox with the screen capture interface
3. 🎯 Display instructions for screen sharing
4. 👁️ Enable AI vision monitoring

### Manual Start
```bash
# Start cognitive OS manually
python3 -c "import tools; result = tools.start_cognitive_os(); print(result)"

# Check status
python3 -c "import tools; tools.cognitive_status()"

# Stop when done
python3 -c "import tools; tools.stop_cognitive_os()"
```

## 🐛 Troubleshooting Installation

### Common Installation Issues

**Python Import Errors**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check pip installation
pip3 --version

# Reinstall packages
pip3 install --user --upgrade pillow websockets psutil blessed
```

**Permission Errors**
```bash
# Fix file permissions
chmod +x ~/cognitive-os-v04/*.py

# Fix Python path
export PYTHONPATH=$PYTHONPATH:~/cognitive-os-v04
```

**Terminal Not Found**
```bash
# Install alternative terminals
sudo apt install xterm konsole terminator -y

# Check available terminals
which gnome-terminal xterm konsole
```

**Database Errors**
```bash
# Remove and reinitialize database
rm -f terminal_sessions.db
python3 -c "import tools; tools.SessionManager()"
```

### System-Specific Issues

**Ubuntu/Debian**
```bash
# Install additional dependencies
sudo apt install python3-tk python3-dev build-essential -y
```

**Fedora/CentOS**
```bash
# Install dependencies
sudo dnf install python3-pip python3-tkinter sqlite gnome-terminal firefox -y
```

**Arch Linux**
```bash
# Install dependencies
sudo pacman -S python-pip sqlite gnome-terminal firefox wmctrl xdotool -y
```

## 📊 Installation Verification

### Complete System Check
```bash
# Run comprehensive installation check
python3 -c "
print('🧬 COGNITIVE OS v0.4 INSTALLATION VERIFICATION')
print('=' * 60)

# Check Python version
import sys
print(f'Python version: {sys.version}')

# Check core imports
try:
    import tools
    import PIL
    import websockets
    import psutil
    import blessed
    print('✅ All core modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)

# Check tools.py functionality
try:
    result = tools.execute_command('echo \"Test successful\"')
    if result['success']:
        print('✅ Terminal control working')
    else:
        print('❌ Terminal control failed')
except Exception as e:
    print(f'❌ Tools.py error: {e}')

# Check database
try:
    import sqlite3
    conn = sqlite3.connect('test_install.db')
    conn.close()
    import os
    os.remove('test_install.db')
    print('✅ Database functionality working')
except Exception as e:
    print(f'❌ Database error: {e}')

print('\\n🎉 INSTALLATION VERIFICATION COMPLETE')
print('🚀 Ready to run: python3 -c \"from quick_screen_test import start_full_screen_test; start_full_screen_test()\"')
"
```

## 🎯 Next Steps

After successful installation:

1. **Run Quick Test**: `python3 -c "from quick_screen_test import start_full_screen_test; start_full_screen_test()"`
2. **Read Documentation**: Check `README.md` for usage instructions
3. **Explore Examples**: Try different test scripts to understand functionality
4. **Customize Configuration**: Modify settings for your specific use case

## 📚 Additional Resources

- **README.md** - Complete usage documentation
- **session_persistence_test.py** - Database functionality tests
- **live_screen_monitor.py** - Real-time AI vision monitoring
- **cognitive_debug.py** - Comprehensive debugging tools

---

**🧬 Installation Complete! Welcome to the future of human-AI collaboration!**