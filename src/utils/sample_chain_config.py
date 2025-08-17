"""
Sample Chain Configuration

Manages configuration for sample chain generation rules, including hi-hat detection
and base name extraction.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import soundfile as sf
import numpy as np

class SampleChainConfig:
    """
    Configuration for sample chain generation rules.
    """
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.
        
        Args:
            config_dict: Optional configuration dictionary
        """
        # Default configuration
        self.max_samples_per_chain = 16  # Changed from 32 to 16 per user request
        
        # Hi-hat detection patterns
        self.hihat_patterns = {
            'closed': ['closedhh', 'clsdhh', 'closed', 'clsd'],
            'open': ['openhh', 'opennhh', 'open', 'opn']  # Added "opennhh" for typo
        }
        
        # Audio output settings
        self.audio_config = {
            'sample_rate': 48000,
            'bit_depth': 16,
            'channels': 2,  # Stereo
            'output_format': 'wav'
        }
        
        # Override with provided config
        if config_dict:
            self._update_from_dict(config_dict)
    
    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if 'max_samples_per_chain' in config_dict:
            self.max_samples_per_chain = config_dict['max_samples_per_chain']
        
        if 'audio_config' in config_dict:
            self.audio_config.update(config_dict['audio_config'])
    
    def is_hihat_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Check if a file is a hi-hat sample.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (is_hihat, hihat_type) where hihat_type is 'closed', 'open', or None
        """
        # Check both parent directory and filename for hi-hat markers
        path_str = str(file_path).lower()
        parent_dir = file_path.parent.name.lower()
        filename = file_path.name.lower()
        
        # Check parent directory first
        for hihat_type, patterns in self.hihat_patterns.items():
            for pattern in patterns:
                if pattern in parent_dir:
                    return True, hihat_type
        
        # Check filename if parent directory doesn't match
        for hihat_type, patterns in self.hihat_patterns.items():
            for pattern in patterns:
                if pattern in filename:
                    return True, hihat_type
        
        return False, None
    
    def extract_base_name(self, file_path: Path) -> str:
        """
        Extract the base name from a hi-hat file path.
        
        Args:
            file_path: Path to the hi-hat file
            
        Returns:
            Base name for grouping hi-hats
        """
        filename = file_path.stem  # Remove extension
        
        # Remove hi-hat type indicators to get the base name
        skip_words = ['closedhh', 'clsdhh', 'openhh', 'opennhh', 'closed', 'clsd', 'open', 'opn']
        
        # Split filename and filter out skip words
        words = re.split(r'[\s_-]+', filename)
        filtered_words = [word for word in words if word.lower() not in skip_words]
        
        if filtered_words:
            return ' '.join(filtered_words)
        else:
            # Fallback to filename if all words were filtered
            return filename
    
    def analyze_sample_durations(self, audio_files: List[Path]) -> Dict[str, Dict[str, float]]:
        """
        Analyze the duration of audio files.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Dictionary mapping file paths to audio info (duration, sample_rate, bit_depth)
        """
        audio_info = {}
        
        for file_path in audio_files:
            try:
                # Use soundfile to get audio info
                with sf.SoundFile(str(file_path)) as sf_file:
                    duration = len(sf_file) / sf_file.samplerate
                    sample_rate = sf_file.samplerate
                    
                    # Infer bit depth from subtype
                    subtype = sf_file.subtype
                    if 'PCM_16' in subtype:
                        bit_depth = 16
                    elif 'PCM_24' in subtype:
                        bit_depth = 24
                    elif 'PCM_32' in subtype:
                        bit_depth = 32
                    else:
                        bit_depth = 16  # Default
                    
                    audio_info[str(file_path)] = {
                        'duration': duration,
                        'sample_rate': sample_rate,
                        'bit_depth': bit_depth
                    }
                    
            except Exception as e:
                print(f"Warning: Could not analyze {file_path}: {e}")
                # Use default values
                audio_info[str(file_path)] = {
                    'duration': 1.0,
                    'sample_rate': 44100,
                    'bit_depth': 16
                }
        
        return audio_info
    
    def get_actual_chain_duration(self, audio_info: Dict[str, Dict[str, float]]) -> float:
        """
        Get the actual duration of the longest sample in a chain.
        
        Args:
            audio_info: Dictionary of audio file info
            
        Returns:
            Duration of the longest sample in seconds
        """
        if not audio_info:
            return 0.0
        
        max_duration = max(info['duration'] for info in audio_info.values())
        return max_duration
    
    def estimate_chain_file_size(self, sample_count: int, longest_sample_duration: float) -> float:
        """
        Estimate the file size of a sample chain in MB.
        
        Args:
            sample_count: Number of samples in the chain
            longest_sample_duration: Duration of the longest sample in seconds
            
        Returns:
            Estimated file size in MB
        """
        # Calculate based on output settings (48kHz, 16-bit, stereo)
        sample_rate = self.audio_config['sample_rate']
        bit_depth = self.audio_config['bit_depth']
        channels = self.audio_config['channels']
        
        # Calculate bytes per sample
        bytes_per_sample = (bit_depth // 8) * channels
        
        # Calculate total samples
        total_samples = int(longest_sample_duration * sample_rate) * sample_count
        
        # Calculate total bytes
        total_bytes = total_samples * bytes_per_sample
        
        # Convert to MB
        size_mb = total_bytes / (1024 * 1024)
        
        return size_mb
    
    def get_estimated_file_size_mb_from_audio_info(self, audio_info: Dict[str, Dict[str, float]]) -> float:
        """
        Get estimated file size from audio info dictionary.
        
        Args:
            audio_info: Dictionary of audio file info
            
        Returns:
            Estimated file size in MB
        """
        if not audio_info:
            return 0.0
        
        # Get the longest sample duration
        longest_duration = self.get_actual_chain_duration(audio_info)
        
        # Count samples
        sample_count = len(audio_info)
        
        # Estimate file size
        return self.estimate_chain_file_size(sample_count, longest_duration) 
