#!/usr/bin/env python3
"""
Basic Usage Example for NI Sample Chainer

This example demonstrates how to use the NI Sample Chainer
to process a directory of WAV files and create sample chains.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import process_audio_directory

def main():
    """Example usage of the NI Sample Chainer."""
    
    # Example configuration
    input_directory = "input_audio"
    output_directory = "output_samples"
    
    # Processing parameters
    config = {
        'sample_duration': 2.0,      # 2 second samples
        'overlap': 10,               # 10% overlap
        'crossfade': 100,            # 100ms crossfade
        'quality': 'high',           # High quality preset
        'parallel_processes': 4      # Use 4 parallel processes
    }
    
    print("🎵 NI Sample Chainer - Basic Usage Example")
    print("=" * 50)
    
    # Check if input directory exists
    if not os.path.exists(input_directory):
        print(f"❌ Input directory '{input_directory}' not found.")
        print("Please create it and add some WAV files.")
        return
    
    print(f"📁 Input directory: {input_directory}")
    print(f"📁 Output directory: {output_directory}")
    print(f"⚙️  Configuration: {config}")
    print()
    
    try:
        # Process the audio files
        print("🚀 Starting audio processing...")
        results = process_audio_directory(
            input_directory, 
            output_directory, 
            **config
        )
        
        print("✅ Processing completed successfully!")
        print(f"📊 Results: {results}")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        print("Please check the logs for more details.")

if __name__ == "__main__":
    main()



