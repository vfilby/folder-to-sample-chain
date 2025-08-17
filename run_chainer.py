#!/usr/bin/env python3
"""
NI Sample Chainer - Simple Entry Point
Run this script directly to launch the application
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()
