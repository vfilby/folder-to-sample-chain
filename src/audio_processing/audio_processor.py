"""
Audio Processor

Core audio processing functionality for loading, validating, and manipulating audio files.
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import logging

# Try to import librosa for MP3 support
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Core audio processor for handling audio files and basic operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the audio processor.
        
        Args:
            config: Configuration dictionary with audio processing settings
        """
        self.config = config or {}
        self.supported_formats = ['.wav', '.aiff', '.flac', '.mp3']
        
        if not LIBROSA_AVAILABLE and '.mp3' in self.supported_formats:
            logger.warning("MP3 support requested but librosa not available. Install with: pip install librosa")
            # Remove MP3 from supported formats if librosa is not available
            self.supported_formats = ['.wav', '.aiff', '.flac']
        
    def load_audio_file(self, file_path: Path) -> Tuple[np.ndarray, int, int, int]:
        """
        Load an audio file and return its data and metadata.
        
        IMPORTANT: This method NEVER modifies the source file. It only reads the file
        and returns a copy of the audio data in memory.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (audio_data, sample_rate, bit_depth, channels)
            
        Raises:
            ValueError: If file format is not supported
            RuntimeError: If file cannot be loaded
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {file_path.suffix}")
        
        try:
            # Handle MP3 files with librosa
            if file_path.suffix.lower() == '.mp3':
                if not LIBROSA_AVAILABLE:
                    raise RuntimeError("MP3 support not available. Install librosa: pip install librosa")
                
                # Load MP3 with librosa
                audio_data, sample_rate = librosa.load(str(file_path), sr=None, mono=False) # mono=False to preserve stereo
                
                # librosa returns (channels, samples) format, transpose to (samples, channels)
                if audio_data.ndim > 1:
                    audio_data = audio_data.T  # Transpose to get (samples, channels)
                
                # MP3 files are typically 16-bit
                bit_depth = 16
                
                # Get channel count
                if audio_data.ndim == 1:
                    channels = 1
                    # Ensure 2D array for consistent processing
                    audio_data = audio_data.reshape(-1, 1)
                else:
                    channels = audio_data.shape[1]
                
                logger.info(f"Loaded MP3 {file_path.name}: {sample_rate}Hz, {bit_depth}bit, {channels}ch")
                return audio_data, sample_rate, bit_depth, channels
            
            # Handle other formats with soundfile
            # Load audio file
            audio_data, sample_rate = sf.read(str(file_path))
            
            # Get bit depth from the file
            info = sf.info(str(file_path))
            # soundfile.info doesn't have a 'bits' attribute, we need to infer it
            if hasattr(info, 'bits'):
                bit_depth = info.bits
            else:
                # Infer bit depth from subtype
                subtype = info.subtype
                if 'PCM_16' in subtype:
                    bit_depth = 16
                elif 'PCM_24' in subtype:
                    bit_depth = 24
                elif 'PCM_32' in subtype:
                    bit_depth = 32
                elif 'FLOAT' in subtype:
                    bit_depth = 32
                else:
                    bit_depth = 16  # Default
            
            # Get channel count
            if audio_data.ndim == 1:
                channels = 1
                # Ensure 2D array for consistent processing
                audio_data = audio_data.reshape(-1, 1)
            else:
                channels = audio_data.shape[1]
            
            logger.info(f"Loaded {file_path.name}: {sample_rate}Hz, {bit_depth}bit, {channels}ch")
            return audio_data, sample_rate, bit_depth, channels
            
        except Exception as e:
            raise RuntimeError(f"Failed to load audio file {file_path}: {e}")
    
    def validate_audio_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate an audio file and return its properties.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with file properties and validation results
        """
        try:
            audio_data, sample_rate, bit_depth, channels = self.load_audio_file(file_path)
            
            # Calculate duration
            duration = len(audio_data) / sample_rate
            
            # Check for common issues
            validation = {
                'file_path': str(file_path),
                'sample_rate': sample_rate,
                'bit_depth': bit_depth,
                'channels': channels,
                'duration': duration,
                'samples': len(audio_data),
                'is_valid': True,
                'warnings': [],
                'errors': []
            }
            
            # Check for potential issues
            if duration < 0.01:  # Less than 10ms
                validation['warnings'].append("Very short audio file (< 10ms)")
                
            if duration > 300:  # More than 5 minutes
                validation['warnings'].append("Very long audio file (> 5 minutes)")
                
            if np.any(np.isnan(audio_data)):
                validation['errors'].append("Audio data contains NaN values")
                validation['is_valid'] = False
                
            if np.any(np.isinf(audio_data)):
                validation['errors'].append("Audio data contains infinite values")
                validation['is_valid'] = False
            
            return validation
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'is_valid': False,
                'errors': [str(e)]
            }
    
    def get_audio_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get basic information about an audio file without loading the full data.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with file information
        """
        try:
            info = sf.info(str(file_path))
            return {
                'file_path': str(file_path),
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'duration': info.duration,
                'samples': info.frames,
                'format': info.format,
                'subtype': info.subtype
            }
        except Exception as e:
            logger.error(f"Failed to get audio info for {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'error': str(e)
            }
    
    def is_power_of_two(self, n: int) -> bool:
        """
        Check if a number is a power of 2.
        
        Args:
            n: Number to check
            
        Returns:
            True if n is a power of 2, False otherwise
        """
        return n > 0 and (n & (n - 1)) == 0
    
    def get_next_power_of_two(self, n: int) -> int:
        """
        Get the next power of 2 greater than or equal to n.
        
        Args:
            n: Input number
            
        Returns:
            Next power of 2
        """
        if n <= 0:
            return 1
        
        # Find the next power of 2
        power = 1
        while power < n:
            power *= 2
        return power
    
    def get_power_of_two_samples(self, sample_count: int, max_samples: int = 32) -> int:
        """
        Get the appropriate power of 2 sample count for a chain.
        
        Args:
            sample_count: Current number of samples
            max_samples: Maximum allowed samples per chain
            
        Returns:
            Power of 2 sample count
        """
        if sample_count <= 0:
            return 1
            
        # Find the next power of 2
        target_samples = self.get_next_power_of_two(sample_count)
        
        # Ensure we don't exceed max_samples
        if target_samples > max_samples:
            target_samples = max_samples
            
        return target_samples
