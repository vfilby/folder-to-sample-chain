#!/bin/bash

# NI Sample Chainer Launcher Script
# Usage: ./run_chainer.sh [input_dir] [output_dir] [options]

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
python3 -c "import soundfile, librosa, numpy, scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Required packages not installed. Run: pip install -r requirements.txt"
    exit 1
fi

# Run the application with provided arguments
echo "🎵 NI Sample Chainer"
echo "=================================================="
python3 src/main.py "$@"
