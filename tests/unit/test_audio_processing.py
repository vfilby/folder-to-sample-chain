"""
Tests for audio processing modules.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import os

from src.audio_processing.audio_processor import AudioProcessor
from src.audio_processing.audio_converter import AudioConverter
from src.audio_processing.sample_chain_builder import SampleChainBuilder
from src.audio_processing.chain_exporter import ChainExporter


class TestAudioProcessor:
    """Test the AudioProcessor class."""
    
    def test_is_power_of_two(self):
        """Test power of two detection."""
        processor = AudioProcessor()
        
        assert processor.is_power_of_two(1) == True
        assert processor.is_power_of_two(2) == True
        assert processor.is_power_of_two(4) == True
        assert processor.is_power_of_two(8) == True
        assert processor.is_power_of_two(16) == True
        assert processor.is_power_of_two(32) == True
        
        assert processor.is_power_of_two(3) == False
        assert processor.is_power_of_two(5) == False
        assert processor.is_power_of_two(7) == False
        assert processor.is_power_of_two(15) == False
        
    def test_get_next_power_of_two(self):
        """Test getting next power of two."""
        processor = AudioProcessor()
        
        assert processor.get_next_power_of_two(1) == 1
        assert processor.get_next_power_of_two(2) == 2
        assert processor.get_next_power_of_two(3) == 4
        assert processor.get_next_power_of_two(5) == 8
        assert processor.get_next_power_of_two(7) == 8
        assert processor.get_next_power_of_two(15) == 16
        
    def test_get_power_of_two_samples(self):
        """Test getting appropriate power of two sample count."""
        processor = AudioProcessor()
        
        assert processor.get_power_of_two_samples(1, 32) == 1
        assert processor.get_power_of_two_samples(3, 32) == 4
        assert processor.get_power_of_two_samples(7, 32) == 8
        assert processor.get_power_of_two_samples(15, 32) == 16
        assert processor.get_power_of_two_samples(31, 32) == 32
        assert processor.get_power_of_two_samples(64, 32) == 32  # Limited by max


class TestAudioConverter:
    """Test the AudioConverter class."""
    
    def test_convert_channels_mono_to_stereo(self):
        """Test converting mono to stereo."""
        converter = AudioConverter()
        
        # Create mono audio data
        mono_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        # Convert to stereo
        stereo_data = converter.convert_channels(mono_data, 1, 2)
        
        assert stereo_data.shape == (5, 2)
        assert np.array_equal(stereo_data[:, 0], mono_data)
        assert np.array_equal(stereo_data[:, 1], mono_data)
        
    def test_convert_channels_stereo_to_mono(self):
        """Test converting stereo to mono."""
        converter = AudioConverter()
        
        # Create stereo audio data
        stereo_data = np.array([
            [0.1, 0.2],
            [0.3, 0.4],
            [0.5, 0.6]
        ])
        
        # Convert to mono
        mono_data = converter.convert_channels(stereo_data, 2, 1)
        
        assert mono_data.shape == (3, 1)
        # Should be average of left and right channels
        expected = np.mean(stereo_data, axis=1, keepdims=True)
        assert np.allclose(mono_data, expected)
        
    def test_normalize_audio(self):
        """Test audio normalization."""
        converter = AudioConverter()
        
        # Create audio data with low amplitude
        low_amplitude = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        
        # Normalize to -18dB
        normalized = converter.normalize_audio(low_amplitude, target_db=-18.0)
        
        # Check that it's not clipped
        assert np.max(np.abs(normalized)) <= 1.0
        
        # Check that RMS is approximately at target level
        rms = np.sqrt(np.mean(normalized ** 2))
        target_linear = 10 ** (-18.0 / 20.0)
        assert abs(rms - target_linear) < 0.1


class TestSampleChainBuilder:
    """Test the SampleChainBuilder class."""
    
    def test_get_final_sample_count(self):
        """Test getting final sample count."""
        config = {
            'enforce_power_of_two': True,
            'max_samples_per_chain': 32
        }
        builder = SampleChainBuilder(config)
        
        assert builder._get_final_sample_count(1) == 1
        assert builder._get_final_sample_count(3) == 4
        assert builder._get_final_sample_count(7) == 8
        assert builder._get_final_sample_count(15) == 16
        assert builder._get_final_sample_count(31) == 32
        assert builder._get_final_sample_count(64) == 32  # Limited by max
        
    def test_pad_samples_to_power_of_two(self):
        """Test padding samples to power of two."""
        config = {
            'pad_strategy': 'repeat-last'
        }
        builder = SampleChainBuilder(config)
        
        # Create sample data
        samples = [
            np.array([1, 2, 3]),
            np.array([4, 5, 6])
        ]
        
        # Pad to 4 samples
        padded = builder._pad_samples_to_power_of_two(samples, 4)
        
        assert len(padded) == 4
        assert np.array_equal(padded[0], np.array([1, 2, 3]))
        assert np.array_equal(padded[1], np.array([4, 5, 6]))
        assert np.array_equal(padded[2], np.array([4, 5, 6]))  # Repeated
        assert np.array_equal(padded[3], np.array([4, 5, 6]))  # Repeated


class TestChainExporter:
    """Test the ChainExporter class."""
    
    def test_generate_filename(self):
        """Test filename generation."""
        exporter = ChainExporter()
        
        # Mock chain data
        chain_data = {
            'metadata': {
                'group_key': 'drums/kick',
                'sample_count': 16,
                'sample_duration': 1.5
            }
        }
        
        filename = exporter._generate_filename(chain_data)
        expected = 'drums-kick-16-1.500s'
        assert filename == expected
        
    def test_generate_filename_simple(self):
        """Test filename generation for simple group key."""
        exporter = ChainExporter()
        
        # Mock chain data
        chain_data = {
            'metadata': {
                'group_key': 'hihat',
                'sample_count': 8,
                'sample_duration': 0.5
            }
        }
        
        filename = exporter._generate_filename(chain_data)
        expected = 'hihat-8-0.500s'
        assert filename == expected


class TestStereoOutput:
    """Test that output chains are properly stereo."""
    
    def test_sample_chain_builder_stereo_output(self):
        """Test that SampleChainBuilder produces stereo output."""
        config = {
            'output_channels': 2,  # Stereo
            'output_sample_rate': 48000,
            'output_bit_depth': 16
        }
        builder = SampleChainBuilder(config)
        
        # Create test audio data (mono)
        mono_audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        # Mock file paths
        test_file = Path('test_file.wav')
        
        # Mock the audio processor to return our test data
        builder.audio_processor.load_audio_file = lambda x: (mono_audio, 48000, 16, 1)
        
        # Build a chain
        chain_data = builder.build_sample_chain([test_file], "test_stereo")
        
        # Verify output is stereo
        assert chain_data['audio_data'].ndim == 2  # Should be 2D array
        assert chain_data['audio_data'].shape[1] == 2  # Should have 2 channels
        assert chain_data['metadata']['channels'] == 2  # Metadata should show stereo
        
        # Verify both channels have audio data
        left_channel = chain_data['audio_data'][:, 0]
        right_channel = chain_data['audio_data'][:, 1]
        
        # Both channels should have the same audio (mono converted to stereo)
        # Allow small tolerance for bit depth conversion differences
        assert np.allclose(left_channel, right_channel, atol=1), "Channels should be nearly identical"
        
        # Audio should not be silent
        assert np.max(np.abs(left_channel)) > 0
        assert np.max(np.abs(right_channel)) > 0
    
    def test_audio_converter_stereo_preservation(self):
        """Test that AudioConverter preserves stereo when converting."""
        converter = AudioConverter({'output_channels': 2})
        
        # Create stereo input data
        stereo_input = np.array([
            [0.1, 0.2],  # Left, Right
            [0.3, 0.4],
            [0.5, 0.6]
        ])
        
        # Convert (should preserve stereo)
        converted = converter.convert_audio(
            stereo_input, 
            current_rate=48000, 
            current_bits=16, 
            current_channels=2,
            target_channels=2
        )
        
        # Should still be stereo
        assert converted.ndim == 2
        assert converted.shape[1] == 2
        assert converted.shape[0] == 3  # Same length
        
        # Values should be preserved (with possible bit depth changes)
        assert np.allclose(converted[:, 0], stereo_input[:, 0], atol=0.1)
        assert np.allclose(converted[:, 1], stereo_input[:, 1], atol=0.1)
    
    def test_real_output_files_stereo(self):
        """Test that actual output files are stereo."""
        import soundfile as sf
        
        # Check if we have real output files to test
        output_dir = Path('sample_data/output')
        if not output_dir.exists():
            pytest.skip("No output files available for testing")
        
        # Test a few output files
        test_files = [
            'samples 2-kick-2-0.462s.wav',
            'samples 2-closedhh-4-0.253s.wav',
            'samples 2-clap-2-0.520s.wav'
        ]
        
        for filename in test_files:
            file_path = output_dir / filename
            if file_path.exists():
                # Load the file and check it's stereo
                audio_data, sample_rate = sf.read(str(file_path))
                
                print(f"Testing {filename}:")
                print(f"  - Shape: {audio_data.shape}")
                print(f"  - Sample rate: {sample_rate}Hz")
                print(f"  - Channels: {audio_data.shape[1] if audio_data.ndim > 1 else 1}")
                
                # Should be stereo (2 channels)
                assert audio_data.ndim == 2, f"{filename} should be 2D array"
                assert audio_data.shape[1] == 2, f"{filename} should have 2 channels"
                
                # Both channels should have audio (not silent)
                left_channel = audio_data[:, 0]
                right_channel = audio_data[:, 1]
                
                assert np.max(np.abs(left_channel)) > 0.001, f"{filename} left channel is too quiet"
                assert np.max(np.abs(right_channel)) > 0.001, f"{filename} right channel is too quiet"
                
                # Channels should be similar (mono source converted to stereo)
                # Allow some tolerance for bit depth conversion
                assert np.allclose(left_channel, right_channel, atol=0.01), f"{filename} channels differ significantly"
                
                print(f"  ✅ {filename} is properly stereo with audio in both channels")


if __name__ == '__main__':
    pytest.main([__file__])
