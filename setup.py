#!/usr/bin/env python3
"""
Setup script for Stream Artifact
Helps users configure the application for first-time use
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("🔧 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine the correct pip executable
    if os.name == 'nt':  # Windows
        pip_executable = os.path.join("venv", "Scripts", "pip.exe")
    else:  # Unix-like systems
        pip_executable = os.path.join("venv", "bin", "pip")
    
    try:
        subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_config_files():
    """Create configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Create .env file from example
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from example")
    
    # Create config directory
    config_dir = Path.home() / ".stream_artifact"
    config_dir.mkdir(exist_ok=True)
    print(f"✅ Created config directory: {config_dir}")
    
    return True

def setup_instructions():
    """Display setup instructions"""
    print("\n🎯 Setup Instructions:")
    print("=" * 50)
    print("1. Edit the .env file with your credentials:")
    print("   - Get Twitch OAuth token from: https://twitchapps.com/tmi/")
    print("   - Get OpenRouter API key from: https://openrouter.ai/")
    print("   - Update TWITCH_TOKEN and OPENROUTER_API_KEY")
    print("   - Set your TWITCH_CHANNEL name")
    print()
    print("2. Run the application:")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\activate")
    else:  # Unix-like systems
        print("   source venv/bin/activate")
    print("   python main.py")
    print()
    print("3. Configure settings through the GUI:")
    print("   - Click the ⚙️ SETTINGS button")
    print("   - Configure Twitch and AI settings")
    print("   - Customize UI appearance")
    print("   - Save settings")
    print()
    print("🎉 You're ready to start streaming with AI!")

def main():
    """Main setup function"""
    print("🌟 Stream Artifact Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not Path("venv").exists():
        if not create_virtual_environment():
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create configuration files
    if not create_config_files():
        sys.exit(1)
    
    # Display setup instructions
    setup_instructions()
    
    print("\n🚀 Setup completed successfully!")
    print("Don't forget to configure your .env file before running the application.")

if __name__ == "__main__":
    main()
