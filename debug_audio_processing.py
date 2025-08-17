#!/usr/bin/env python3
"""
Debug script to investigate audio processing issues.
"""

import sys
from pathlib import Path
import numpy as np
import soundfile as sf

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from audio_processing.audio_processor import AudioProcessor
from audio_processing.sample_chain_builder import SampleChainBuilder
from utils.config import ConfigManager


def debug_audio_processing():
    """Debug the audio processing step by step."""
    
    # Test with a single kick file
    test_file = Path('sample_data/input/samples 2/kick/sample hollow.wav')
    
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return
    
    print("🔍 Debugging Audio Processing")
    print("=" * 50)
    
    # Step 1: Load the original file
    print(f"\n📁 Step 1: Loading original file: {test_file}")
    processor = AudioProcessor()
    
    try:
        audio_data, sample_rate, bit_depth, channels = processor.load_audio_file(test_file)
        print(f"✅ Loaded successfully:")
        print(f"   - Shape: {audio_data.shape}")
        print(f"   - Sample rate: {sample_rate}Hz")
        print(f"   - Bit depth: {bit_depth}bit")
        print(f"   - Channels: {channels}")
        print(f"   - Duration: {len(audio_data) / sample_rate:.3f}s")
        print(f"   - Data type: {audio_data.dtype}")
        print(f"   - Min/Max values: {np.min(audio_data):.6f} / {np.max(audio_data):.6f}")
        print(f"   - RMS: {np.sqrt(np.mean(audio_data**2)):.6f}")
        
        # Check if audio data is actually audible
        if np.max(np.abs(audio_data)) < 0.001:
            print("⚠️  WARNING: Audio data appears to be very quiet or silent!")
        elif np.max(np.abs(audio_data)) > 0.1:
            print("✅ Audio data appears to have normal levels")
        else:
            print("⚠️  Audio data appears to be quiet")
            
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        return
    
    # Step 2: Test the sample chain builder
    print(f"\n🔨 Step 2: Testing sample chain builder")
    
    config_manager = ConfigManager()
    config = config_manager.load_config(Path('config.yaml'))
    audio_config = config.get('audio_processing', {})
    
    builder = SampleChainBuilder(audio_config)
    
    try:
        # Build a chain with just this one file
        chain_data = builder.build_sample_chain([test_file], "debug_test")
        
        print(f"✅ Chain built successfully:")
        print(f"   - Sample count: {chain_data['sample_count']}")
        print(f"   - Sample length: {chain_data['sample_length']}")
        print(f"   - Total duration: {chain_data['total_duration']:.3f}s")
        print(f"   - Audio data shape: {chain_data['audio_data'].shape}")
        print(f"   - Audio data type: {chain_data['audio_data'].dtype}")
        print(f"   - Audio data min/max: {np.min(chain_data['audio_data']):.6f} / {np.max(chain_data['audio_data']):.6f}")
        print(f"   - Audio data RMS: {np.sqrt(np.mean(chain_data['audio_data']**2)):.6f}")
        
        # Check if the chain audio is audible
        if np.max(np.abs(chain_data['audio_data'])) < 0.001:
            print("⚠️  WARNING: Chain audio data appears to be very quiet or silent!")
        elif np.max(np.abs(chain_data['audio_data'])) > 0.1:
            print("✅ Chain audio data appears to have normal levels")
        else:
            print("⚠️  Chain audio data appears to be quiet")
            
    except Exception as e:
        print(f"❌ Failed to build chain: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test saving a small portion
    print(f"\n💾 Step 3: Testing audio export")
    
    try:
        # Save just the first second of the chain
        test_output = Path('debug_test_output.wav')
        first_second = chain_data['audio_data'][:48000]  # First second at 48kHz
        
        sf.write(str(test_output), first_second, 48000)
        print(f"✅ Saved test output: {test_output}")
        print(f"   - Size: {test_output.stat().st_size} bytes")
        print(f"   - Duration: {len(first_second) / 48000:.3f}s")
        
        # Verify the saved file
        info = sf.info(str(test_output))
        print(f"   - File info: {info.samplerate}Hz, {info.channels}ch, {info.duration:.3f}s")
        
        # Load it back to check
        reloaded, sr = sf.read(str(test_output))
        print(f"   - Reloaded: shape={reloaded.shape}, min/max={np.min(reloaded):.6f}/{np.max(reloaded):.6f}")
        
    except Exception as e:
        print(f"❌ Failed to save test output: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    debug_audio_processing()

