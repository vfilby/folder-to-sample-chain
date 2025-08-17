"""
Test Data Generator for NI Sample Chainer

This module provides utilities for generating test data,
including mock audio files and test configurations.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import yaml

class TestDataGenerator:
    """Generate test data for the NI Sample Chainer tests."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize the test data generator."""
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent / 'tests' / 'fixtures'
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.base_dir / 'audio').mkdir(exist_ok=True)
        (self.base_dir / 'configs').mkdir(exist_ok=True)
        (self.base_dir / 'outputs').mkdir(exist_ok=True)
        (self.base_dir / 'temp').mkdir(exist_ok=True)
    
    def create_mock_wav_file(self, filename: str, duration_seconds: float = 1.0) -> Path:
        """
        Create a mock WAV file for testing.
        
        Args:
            filename: Name of the file to create
            duration_seconds: Duration of the mock audio in seconds
            
        Returns:
            Path to the created mock WAV file
        """
        # This is a placeholder - in a real implementation, you'd create actual WAV data
        # For now, we'll create a file with a .wav extension
        wav_file = self.base_dir / 'audio' / filename
        
        # Create a simple text file that simulates WAV data
        # In real tests, you'd use a library like scipy.io.wavfile to create actual WAV files
        mock_content = f"""# Mock WAV file: {filename}
# Duration: {duration_seconds} seconds
# Sample Rate: 44100 Hz
# Channels: 2 (stereo)
# Bit Depth: 16-bit

# This is a placeholder file for testing purposes.
# In actual tests, this would contain real WAV audio data.
"""
        
        wav_file.write_text(mock_content)
        return wav_file
    
    def create_test_audio_directory(self, num_files: int = 5) -> Path:
        """
        Create a directory with multiple test audio files.
        
        Args:
            num_files: Number of audio files to create
            
        Returns:
            Path to the created audio directory
        """
        audio_dir = self.base_dir / 'test_audio_input'
        audio_dir.mkdir(exist_ok=True)
        
        # Create test audio files with different durations
        durations = [1.0, 2.0, 3.0, 5.0, 10.0]
        file_names = [
            'test_song_1.wav',
            'test_song_2.wav', 
            'test_song_3.wav',
            'test_song_4.wav',
            'test_song_5.wav'
        ]
        
        for i in range(min(num_files, len(file_names))):
            self.create_mock_wav_file(
                file_names[i], 
                durations[i % len(durations)]
            )
        
        return audio_dir
    
    def create_test_config(self, config_name: str, **kwargs) -> Path:
        """
        Create a test configuration file.
        
        Args:
            config_name: Name of the configuration file
            **kwargs: Configuration parameters
            
        Returns:
            Path to the created configuration file
        """
        config_dir = self.base_dir / 'configs'
        config_file = config_dir / config_name
        
        # Default test configuration
        default_config = {
            'defaults': {
                'sample_duration': 1.0,
                'overlap': 0,
                'crossfade': 50,
                'quality': 'standard',
                'parallel_processes': 2
            },
            'audio': {
                'input_formats': ['wav'],
                'output_format': 'wav',
                'sample_rate': 44100,
                'bit_depth': 16,
                'normalize': True
            },
            'digitakt': {
                'naming_convention': '{original_name}_{sample_number:03d}',
                'max_filename_length': 32,
                'folder_structure': True
            }
        }
        
        # Override with provided parameters
        for key, value in kwargs.items():
            if key in default_config:
                if isinstance(value, dict):
                    default_config[key].update(value)
                else:
                    default_config[key] = value
            else:
                default_config[key] = value
        
        # Write configuration file
        if config_name.endswith('.yaml') or config_name.endswith('.yml'):
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
        elif config_name.endswith('.json'):
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
        else:
            # Default to YAML
            config_file = config_file.with_suffix('.yaml')
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
        
        return config_file
    
    def create_test_output_structure(self) -> Path:
        """
        Create a test output directory structure.
        
        Returns:
            Path to the created output directory
        """
        output_dir = self.base_dir / 'outputs' / 'test_samples'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample output files
        sample_files = [
            'test_song_001.wav',
            'test_song_002.wav',
            'test_song_003.wav',
            'test_song_004.wav',
            'test_song_005.wav'
        ]
        
        for sample_file in sample_files:
            sample_path = output_dir / sample_file
            sample_path.write_text(f"# Mock sample file: {sample_file}")
        
        # Create metadata file
        metadata = {
            'input_file': 'test_song.wav',
            'total_samples': len(sample_files),
            'sample_duration': 1.0,
            'overlap': 0,
            'crossfade': 50,
            'quality': 'standard',
            'processing_time': 2.5,
            'samples': [
                {
                    'filename': sample_file,
                    'start_time': i * 1.0,
                    'duration': 1.0,
                    'file_size': 1024
                }
                for i, sample_file in enumerate(sample_files)
            ]
        }
        
        metadata_file = output_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return output_dir
    
    def create_temp_workspace(self) -> Path:
        """
        Create a temporary workspace for testing.
        
        Returns:
            Path to the created temporary workspace
        """
        temp_dir = self.base_dir / 'temp' / f'workspace_{os.getpid()}'
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (temp_dir / 'input').mkdir(exist_ok=True)
        (temp_dir / 'output').mkdir(exist_ok=True)
        (temp_dir / 'cache').mkdir(exist_ok=True)
        
        return temp_dir
    
    def cleanup_temp_files(self):
        """Clean up temporary test files."""
        temp_dir = self.base_dir / 'temp'
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    def get_test_audio_files(self) -> List[Path]:
        """Get a list of all test audio files."""
        audio_dir = self.base_dir / 'audio'
        if not audio_dir.exists():
            return []
        
        return list(audio_dir.glob('*.wav'))
    
    def get_test_configs(self) -> List[Path]:
        """Get a list of all test configuration files."""
        config_dir = self.base_dir / 'configs'
        if not config_dir.exists():
            return []
        
        config_files = []
        for ext in ['.yaml', '.yml', '.json']:
            config_files.extend(config_dir.glob(f'*{ext}'))
        
        return config_files

def create_basic_test_data():
    """Create basic test data for the project."""
    generator = TestDataGenerator()
    
    print("🔧 Creating basic test data...")
    
    # Create test audio files
    audio_dir = generator.create_test_audio_directory(5)
    print(f"✅ Created test audio directory: {audio_dir}")
    
    # Create test configurations
    configs = [
        ('test_config.yaml', {}),
        ('test_config_fast.yaml', {'defaults': {'quality': 'fast', 'parallel_processes': 4}}),
        ('test_config_high.yaml', {'defaults': {'quality': 'high', 'parallel_processes': 1}})
    ]
    
    for config_name, config_params in configs:
        config_file = generator.create_test_config(config_name, **config_params)
        print(f"✅ Created test config: {config_file}")
    
    # Create test output structure
    output_dir = generator.create_test_output_structure()
    print(f"✅ Created test output structure: {output_dir}")
    
    print(f"🎉 Test data created in: {generator.base_dir}")
    return generator

if __name__ == "__main__":
    create_basic_test_data()



