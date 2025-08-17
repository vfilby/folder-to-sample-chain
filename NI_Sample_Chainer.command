#!/bin/bash

# NI Sample Chainer - Double-click to run
# This file opens Terminal and runs the application

# Get the directory where this file is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if we're in a virtual environment or need to activate one
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the application
echo "🎵 NI Sample Chainer"
echo "=================================================="
echo "Processing audio files..."
echo ""

# Check if arguments were passed
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_directory> <output_directory> [options]"
    echo ""
    echo "Examples:"
    echo "  $0 'sample_data/input/samples 2' 'output' --verbose"
    echo "  $0 'my_audio_folder' 'my_output' --dry-run"
    echo ""
    echo "Press Enter to exit..."
    read
else
    python src/main.py "$@"
    echo ""
    echo "Press Enter to exit..."
    read
fi
