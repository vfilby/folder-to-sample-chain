#!/usr/bin/env python3
"""
Development Setup Script for NI Sample Chainer

This script helps set up the development environment for the project.
Run this script to install dependencies and set up the development environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install project dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing project dependencies"):
        return False
    
    return True

def create_directories():
    """Create necessary directories if they don't exist."""
    print("\n📁 Creating project directories...")
    
    directories = [
        "logs",
        "temp",
        "tests/audio_samples",
        "tests/fixtures",
        "docs",
        "examples"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def run_tests():
    """Run the test suite to verify setup."""
    print("\n🧪 Running tests to verify setup...")
    
    if not run_command("python -m pytest tests/ -v", "Running test suite"):
        print("⚠️  Tests failed, but setup can continue")
        return True
    
    return True

def create_sample_config():
    """Create a sample configuration file for development."""
    print("\n⚙️  Creating development configuration...")
    
    dev_config = """# Development Configuration for NI Sample Chainer
# This file contains development-specific settings

# Development settings
development:
  debug_mode: true
  log_level: DEBUG
  enable_profiling: true
  
# Override defaults for development
defaults:
  sample_duration: 0.5      # Shorter samples for faster testing
  quality: fast             # Fast processing for development
  parallel_processes: 2     # Fewer processes for development

# Development paths
paths:
  test_audio: tests/audio_samples/
  temp_directory: temp/
  log_directory: logs/
"""
    
    config_path = Path("config.dev.yaml")
    if not config_path.exists():
        with open(config_path, 'w') as f:
            f.write(dev_config)
        print("✅ Created development configuration: config.dev.yaml")
    else:
        print("ℹ️  Development configuration already exists")
    
    return True

def main():
    """Main setup function."""
    print("🎵 NI Sample Chainer - Development Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create development configuration
    if not create_sample_config():
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    print("\n🎉 Development environment setup completed!")
    print("\n📋 Next steps:")
    print("   1. Add some WAV files to tests/audio_samples/ for testing")
    print("   2. Run 'python src/main.py --help' to see available options")
    print("   3. Check the documentation in docs/ folder")
    print("   4. Review AI_RULES.md for development guidelines")
    print("\n🚀 Happy coding!")

if __name__ == "__main__":
    main()



