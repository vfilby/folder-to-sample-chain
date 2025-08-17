#!/usr/bin/env python3
"""
Demo script for audio processing functionality.

This script demonstrates how to use the audio processing modules to create
evenly spaced sample chains from audio files.
"""

import sys
from pathlib import Path
import numpy as np
import soundfile as sf

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from audio_processing.audio_processor import AudioProcessor
from audio_processing.audio_converter import AudioConverter
from audio_processing.sample_chain_builder import SampleChainBuilder
from audio_processing.chain_exporter import ChainExporter
from utils.config import ConfigManager


def create_test_audio_files():
    """Create some test audio files for demonstration."""
    test_dir = Path('tests/audio_samples')
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a simple sine wave
    sample_rate = 44100
    duration = 1.0  # 1 second
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create different frequencies for variety
    frequencies = [440, 880, 1320, 1760]  # A4, A5, E6, A6
    
    for i, freq in enumerate(frequencies):
        # Generate sine wave
        audio_data = 0.3 * np.sin(2 * np.pi * freq * t)
        
        # Save as WAV file
        filename = test_dir / f'test_sine_{freq}hz_{i+1}.wav'
        sf.write(str(filename), audio_data, sample_rate)
        print(f"Created test file: {filename}")
    
    # Create a stereo file
    stereo_audio = np.column_stack([
        0.2 * np.sin(2 * np.pi * 220 * t),  # Left channel: A3
        0.2 * np.sin(2 * np.pi * 330 * t)   # Right channel: E4
    ])
    
    stereo_filename = test_dir / 'test_stereo.wav'
    sf.write(str(stereo_filename), stereo_audio, sample_rate)
    print(f"Created stereo test file: {stereo_filename}")
    
    return test_dir


def demo_audio_processor():
    """Demonstrate the AudioProcessor functionality."""
    print("\n=== Audio Processor Demo ===")
    
    processor = AudioProcessor()
    
    # Test power of two functions
    test_numbers = [3, 7, 15, 31, 63]
    for num in test_numbers:
        is_power = processor.is_power_of_two(num)
        next_power = processor.get_next_power_of_two(num)
        print(f"{num}: is_power_of_two = {is_power}, next_power = {next_power}")
    
    # Test sample count calculation
    max_samples = 32
    for num in test_numbers:
        target_count = processor.get_power_of_two_samples(num, max_samples)
        print(f"Sample count {num} -> {target_count} (max: {max_samples})")


def demo_audio_converter():
    """Demonstrate the AudioConverter functionality."""
    print("\n=== Audio Converter Demo ===")
    
    converter = AudioConverter()
    
    # Test channel conversion
    mono_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    print(f"Original mono data shape: {mono_data.shape}")
    
    # Convert to stereo
    stereo_data = converter.convert_channels(mono_data, 1, 2)
    print(f"Converted to stereo shape: {stereo_data.shape}")
    
    # Convert back to mono
    mono_again = converter.convert_channels(stereo_data, 2, 1)
    print(f"Converted back to mono shape: {mono_again.shape}")
    
    # Test normalization
    low_amplitude = np.array([0.01, 0.02, 0.03])
    normalized = converter.normalize_audio(low_amplitude, target_db=-18.0)
    
    original_rms = np.sqrt(np.mean(low_amplitude ** 2))
    normalized_rms = np.sqrt(np.mean(normalized ** 2))
    target_rms = 10 ** (-18.0 / 20.0)
    
    print(f"Original RMS: {original_rms:.6f}")
    print(f"Normalized RMS: {normalized_rms:.6f}")
    print(f"Target RMS: {target_rms:.6f}")


def demo_sample_chain_builder():
    """Demonstrate the SampleChainBuilder functionality."""
    print("\n=== Sample Chain Builder Demo ===")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config(Path('config.yaml'))
    audio_config = config.get('audio_processing', {})
    
    builder = SampleChainBuilder(audio_config)
    
    # Test power of two sample count calculation
    test_counts = [3, 7, 15, 31, 63]
    for count in test_counts:
        final_count = builder._get_final_sample_count(count)
        print(f"Sample count {count} -> {final_count}")
    
    # Test padding strategy
    test_samples = [
        np.array([1, 2, 3]),
        np.array([4, 5, 6])
    ]
    
    padded = builder._pad_samples_to_power_of_two(test_samples, 4)
    print(f"Padded {len(test_samples)} samples to {len(padded)} samples")
    
    # Show the padding
    for i, sample in enumerate(padded):
        print(f"  Sample {i}: {sample}")


def demo_chain_exporter():
    """Demonstrate the ChainExporter functionality."""
    print("\n=== Chain Exporter Demo ===")
    
    exporter = ChainExporter()
    
    # Test filename generation
    test_chains = [
        {
            'metadata': {
                'group_key': 'drums/kick',
                'sample_count': 16,
                'sample_duration': 1.5
            }
        },
        {
            'metadata': {
                'group_key': 'hihat',
                'sample_count': 8,
                'sample_duration': 0.5
            }
        },
        {
            'metadata': {
                'group_key': 'instruments/piano',
                'sample_count': 32,
                'sample_duration': 2.0
            }
        }
    ]
    
    for chain in test_chains:
        filename = exporter._generate_filename(chain)
        print(f"Group: {chain['metadata']['group_key']} -> {filename}")


def main():
    """Main demo function."""
    print("NI Sample Chainer - Audio Processing Demo")
    print("=" * 50)
    
    # Check if test audio files exist
    test_dir = Path('tests/audio_samples')
    if not test_dir.exists() or not list(test_dir.glob('*.wav')):
        print("Creating test audio files...")
        create_test_audio_files()
    else:
        print(f"Using existing test audio files in {test_dir}")
    
    # Run demos
    demo_audio_processor()
    demo_audio_converter()
    demo_sample_chain_builder()
    demo_chain_exporter()
    
    print("\n" + "=" * 50)
    print("Demo complete!")
    print(f"\nTest audio files are available in: {test_dir.absolute()}")
    print("You can add your own WAV files there for testing.")


if __name__ == '__main__':
    main()
