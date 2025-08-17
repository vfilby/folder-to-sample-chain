"""
Sample Chain Builder

Creates evenly spaced sample chains from multiple audio files with proper padding and normalization.
"""

import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import logging
from .audio_processor import AudioProcessor
from .audio_converter import AudioConverter

logger = logging.getLogger(__name__)


class SampleChainBuilder:
    """
    Builds evenly spaced sample chains from multiple audio files.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the sample chain builder.
        
        Args:
            config: Configuration dictionary with audio processing settings
        """
        self.config = config or {}
        self.audio_processor = AudioProcessor(config)
        self.audio_converter = AudioConverter(config)
        
        # Audio processing settings
        self.target_sample_rate = self.config.get('output_sample_rate', 48000)
        self.target_bit_depth = self.config.get('output_bit_depth', 16)
        self.target_channels = self.config.get('output_channels', 2)
        self.enforce_power_of_two = self.config.get('enforce_power_of_two', True)
        self.pad_strategy = self.config.get('pad_strategy', 'repeat-last')
        self.max_samples = self.config.get('max_samples_per_chain', 32)
        
    def build_sample_chain(self, file_paths: List[Path], group_key: str) -> Dict[str, Any]:
        """
        Build a sample chain from a list of audio files.
        
        IMPORTANT: This method NEVER modifies the source audio files. All processing
        is done on copies of the audio data in memory. The original files remain
        completely unchanged.
        
        Args:
            file_paths: List of audio file paths to combine
            group_key: Group identifier for the chain
            
        Returns:
            Dictionary containing the chain data and metadata
        """
        if not file_paths:
            raise ValueError("No file paths provided")
            
        logger.info(f"Building sample chain for {group_key} with {len(file_paths)} files")
        
        # Step 1: Load and analyze all audio files
        # SAFETY: All source files remain completely unchanged
        audio_files = self._load_audio_files(file_paths)
        
        # Step 2: Determine target sample length (longest sample)
        target_length = self._get_target_sample_length(audio_files)
        
        # Step 3: Normalize all samples to the same length
        normalized_samples = self._normalize_sample_lengths(audio_files, target_length)
        
        # Step 4: Determine final sample count (power of 2)
        final_sample_count = self._get_final_sample_count(len(normalized_samples))
        
        # Step 5: Pad samples to reach power of 2
        padded_samples = self._pad_samples_to_power_of_two(normalized_samples, final_sample_count)
        
        # Step 6: Convert all samples to target format
        converted_samples = self._convert_samples_to_target_format(padded_samples)
        
        # Step 7: Concatenate samples into single chain
        # SAFETY: All source files remain completely unchanged
        chain_audio = self._concatenate_samples(converted_samples)
        
        # Step 8: Create metadata
        metadata = self._create_chain_metadata(
            group_key, file_paths, final_sample_count, target_length, chain_audio
        )
        
        return {
            'audio_data': chain_audio,
            'metadata': metadata,
            'sample_count': final_sample_count,
            'sample_length': target_length,
            'total_duration': len(chain_audio) / self.target_sample_rate
        }
    
    def _load_audio_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Load all audio files and return their data and metadata.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of dictionaries with audio data and metadata
        """
        audio_files = []
        
        for file_path in file_paths:
            try:
                audio_data, sample_rate, bit_depth, channels = self.audio_processor.load_audio_file(file_path)
                
                audio_files.append({
                    'file_path': file_path,
                    'audio_data': audio_data,
                    'sample_rate': sample_rate,
                    'bit_depth': bit_depth,
                    'channels': channels,
                    'original_length': len(audio_data),
                    'duration': len(audio_data) / sample_rate
                })
                
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue
        
        if not audio_files:
            raise RuntimeError("No audio files could be loaded")
            
        return audio_files
    
    def _get_target_sample_length(self, audio_files: List[Dict[str, Any]]) -> int:
        """
        Determine the target sample length (longest sample).
        
        Args:
            audio_files: List of loaded audio files
            
        Returns:
            Target sample length in samples
        """
        # Find the longest sample
        max_length = max(audio['original_length'] for audio in audio_files)
        
        # Convert to target sample rate if needed
        for audio in audio_files:
            if audio['sample_rate'] != self.target_sample_rate:
                ratio = self.target_sample_rate / audio['sample_rate']
                converted_length = int(audio['original_length'] * ratio)
                max_length = max(max_length, converted_length)
        
        logger.info(f"Target sample length: {max_length} samples ({max_length/self.target_sample_rate:.3f}s)")
        return max_length
    
    def _normalize_sample_lengths(self, audio_files: List[Dict[str, Any]], target_length: int) -> List[np.ndarray]:
        """
        Normalize all samples to the same length.
        
        Args:
            audio_files: List of loaded audio files
            target_length: Target length in samples
            
        Returns:
            List of normalized audio arrays
        """
        normalized_samples = []
        
        for audio in audio_files:
            # Convert to target sample rate first
            if audio['sample_rate'] != self.target_sample_rate:
                audio_data = self.audio_converter.convert_sample_rate(
                    audio['audio_data'], audio['sample_rate'], self.target_sample_rate
                )
            else:
                audio_data = audio['audio_data']
            
            # Pad or truncate to target length
            if len(audio_data) < target_length:
                # Pad with silence
                padding_length = target_length - len(audio_data)
                if audio_data.ndim == 1:
                    padding = np.zeros(padding_length)
                    padded_data = np.concatenate([audio_data, padding])
                else:
                    padding = np.zeros((padding_length, audio_data.shape[1]))
                    padded_data = np.vstack([audio_data, padding])
                    
                normalized_samples.append(padded_data)
                
            elif len(audio_data) > target_length:
                # Truncate
                normalized_samples.append(audio_data[:target_length])
                
            else:
                # Already correct length
                normalized_samples.append(audio_data)
        
        return normalized_samples
    
    def _get_final_sample_count(self, current_count: int) -> int:
        """
        Get the final sample count (power of 2).
        
        Args:
            current_count: Current number of samples
            
        Returns:
            Final sample count (power of 2)
        """
        if not self.enforce_power_of_two:
            return current_count
            
        # Get next power of 2
        target_count = self.audio_processor.get_next_power_of_two(current_count)
        
        # Ensure we don't exceed max_samples
        if target_count > self.max_samples:
            target_count = self.max_samples
            
        logger.info(f"Sample count: {current_count} -> {target_count} (power of 2)")
        return target_count
    
    def _pad_samples_to_power_of_two(self, samples: List[np.ndarray], target_count: int) -> List[np.ndarray]:
        """
        Pad samples to reach the target count.
        
        Args:
            samples: List of normalized samples
            target_count: Target number of samples
            
        Returns:
            List of samples padded to target count
        """
        if len(samples) >= target_count:
            return samples[:target_count]
            
        # Need to pad
        padding_needed = target_count - len(samples)
        
        if self.pad_strategy == 'repeat-last':
            # Repeat the last sample
            last_sample = samples[-1]
            for _ in range(padding_needed):
                samples.append(last_sample.copy())
                
        elif self.pad_strategy == 'silence':
            # Pad with silence
            sample_shape = samples[0].shape
            for _ in range(padding_needed):
                if len(sample_shape) == 1:
                    silence = np.zeros(sample_shape[0])
                else:
                    silence = np.zeros(sample_shape)
                samples.append(silence)
                
        elif self.pad_strategy == 'none':
            # Don't pad, just return what we have
            pass
            
        logger.info(f"Padded samples from {len(samples) - padding_needed} to {len(samples)}")
        return samples
    
    def _convert_samples_to_target_format(self, samples: List[np.ndarray]) -> List[np.ndarray]:
        """
        Convert all samples to the target format.
        
        Args:
            samples: List of audio samples
            
        Returns:
            List of converted samples
        """
        converted_samples = []
        
        for i, sample in enumerate(samples):
            # Convert to target format
            # Note: soundfile returns float64 data, so we need to handle this correctly
            current_bits = 32 if sample.dtype in [np.float32, np.float64] else 16
            
            converted = self.audio_converter.convert_audio(
                sample, 
                self.target_sample_rate,  # Already converted
                current_bits,  # Detect actual bit depth from data type
                sample.shape[1] if sample.ndim > 1 else 1,
                self.target_sample_rate,
                self.target_bit_depth,
                self.target_channels
            )
            
            converted_samples.append(converted)
            
        return converted_samples
    
    def _concatenate_samples(self, samples: List[np.ndarray]) -> np.ndarray:
        """
        Concatenate all samples into a single audio chain.
        
        Args:
            samples: List of audio samples
            
        Returns:
            Concatenated audio data
        """
        # Concatenate along the time axis
        if samples[0].ndim == 1:
            # Mono
            chain_audio = np.concatenate(samples)
        else:
            # Stereo or multi-channel
            chain_audio = np.vstack(samples)
            
        logger.info(f"Created chain with {len(samples)} samples, total length: {len(chain_audio)} samples")
        return chain_audio
    
    def _create_chain_metadata(self, group_key: str, file_paths: List[Path], 
                              sample_count: int, sample_length: int, 
                              chain_audio: np.ndarray) -> Dict[str, Any]:
        """
        Create metadata for the sample chain.
        
        Args:
            group_key: Group identifier
            file_paths: Original file paths
            sample_count: Number of samples in chain
            sample_length: Length of each sample
            chain_audio: Final audio data
            
        Returns:
            Metadata dictionary
        """
        total_duration = len(chain_audio) / self.target_sample_rate
        sample_duration = sample_length / self.target_sample_rate
        
        return {
            'group_key': group_key,
            'sample_count': sample_count,
            'sample_length': sample_length,
            'sample_duration': sample_duration,
            'total_duration': total_duration,
            'sample_rate': self.target_sample_rate,
            'bit_depth': self.target_bit_depth,
            'channels': self.target_channels,
            'original_files': [str(fp) for fp in file_paths],
            'power_of_two': self.audio_processor.is_power_of_two(sample_count),
            'pad_strategy': self.pad_strategy,
            'created_at': str(np.datetime64('now'))
        }
