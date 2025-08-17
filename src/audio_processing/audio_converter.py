"""
Audio Converter

Handles audio format conversion including sample rate, bit depth, and channel conversion.
"""

import numpy as np
import soundfile as sf
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AudioConverter:
    """
    Audio format converter for sample rate, bit depth, and channel conversion.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the audio converter.
        
        Args:
            config: Configuration dictionary with conversion settings
        """
        self.config = config or {}
        self.default_sample_rate = self.config.get('output_sample_rate', 48000)
        self.default_bit_depth = self.config.get('output_bit_depth', 16)
        self.default_channels = self.config.get('output_channels', 2)
        self.resampling_algorithm = self.config.get('resampling_algorithm', 'kaiser_best')
        self.dithering = self.config.get('dithering', True)
        
    def convert_sample_rate(self, audio_data: np.ndarray, current_rate: int, target_rate: int) -> np.ndarray:
        """
        Convert audio data to a different sample rate.
        
        Args:
            audio_data: Input audio data
            current_rate: Current sample rate
            target_rate: Target sample rate
            
        Returns:
            Audio data at the target sample rate
        """
        if current_rate == target_rate:
            return audio_data
            
        # Calculate the ratio
        ratio = target_rate / current_rate
        
        # Calculate new length
        new_length = int(len(audio_data) * ratio)
        
        # Use scipy's resampling for better control
        try:
            from scipy import signal
            
            # Resample using scipy
            if audio_data.ndim == 1:
                resampled_data = signal.resample(audio_data, new_length)
            else:
                # For stereo/multi-channel, resample each channel
                resampled_data = np.zeros((new_length, audio_data.shape[1]))
                for ch in range(audio_data.shape[1]):
                    resampled_data[:, ch] = signal.resample(audio_data[:, ch], new_length)
                    
        except ImportError:
            # Fallback to simple interpolation if scipy is not available
            logger.warning("scipy not available, using simple interpolation")
            
            if audio_data.ndim == 1:
                # Simple linear interpolation
                old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
                new_indices = np.linspace(0, len(audio_data) - 1, new_length)
                resampled_data = np.interp(new_indices, old_indices, audio_data)
            else:
                # For stereo/multi-channel
                resampled_data = np.zeros((new_length, audio_data.shape[1]))
                for ch in range(audio_data.shape[1]):
                    old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
                    new_indices = np.linspace(0, len(audio_data) - 1, new_length)
                    resampled_data[:, ch] = np.interp(new_indices, old_indices, audio_data[:, ch])
        
        logger.info(f"Resampled from {current_rate}Hz to {target_rate}Hz")
        return resampled_data
    
    def convert_bit_depth(self, audio_data: np.ndarray, current_bits: int, target_bits: int) -> np.ndarray:
        """
        Convert audio data to a different bit depth.
        
        Args:
            audio_data: Input audio data
            current_bits: Current bit depth
            target_bits: Target bit depth
            
        Returns:
            Audio data at the target bit depth
        """
        if current_bits == target_bits:
            return audio_data
            
        # Normalize to [-1, 1] range
        if audio_data.dtype in [np.float32, np.float64]:
            # Data is already normalized to [-1, 1] range
            audio_data = audio_data.astype(np.float32)
        elif current_bits == 16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        elif current_bits == 24:
            audio_data = audio_data.astype(np.float32) / 8388608.0
        elif current_bits == 32:
            audio_data = audio_data.astype(np.float32) / 2147483648.0
        else:
            # Assume already normalized
            audio_data = audio_data.astype(np.float32)
        
        # Apply dithering if enabled
        if self.dithering and target_bits < current_bits:
            # Simple triangular dithering
            dither = np.random.triangular(-1, 0, 1, size=audio_data.shape) * (2 ** (-target_bits))
            audio_data = audio_data + dither
        
        # Convert to target bit depth
        if target_bits == 16:
            # Clip to [-1, 1] and convert to 16-bit
            audio_data = np.clip(audio_data, -1.0, 1.0)
            return (audio_data * 32767.0).astype(np.int16)
        elif target_bits == 24:
            # Clip to [-1, 1] and convert to 24-bit
            audio_data = np.clip(audio_data, -1.0, 1.0)
            return (audio_data * 8388607.0).astype(np.int32)
        elif target_bits == 32:
            # Return as float32
            return np.clip(audio_data, -1.0, 1.0).astype(np.float32)
        else:
            raise ValueError(f"Unsupported target bit depth: {target_bits}")
    
    def convert_channels(self, audio_data: np.ndarray, current_channels: int, target_channels: int) -> np.ndarray:
        """
        Convert audio data to a different channel count.
        
        Args:
            audio_data: Input audio data
            current_channels: Current channel count
            target_channels: Target channel count
            
        Returns:
            Audio data with target channel count
        """
        if current_channels == target_channels:
            return audio_data
            
        if target_channels == 1:
            # Convert to mono by averaging channels
            if current_channels == 2:
                return np.mean(audio_data, axis=1, keepdims=True)
            else:
                # Take first channel
                return audio_data[:, 0:1]
                
        elif target_channels == 2:
            # Convert to stereo
            if current_channels == 1:
                # Duplicate mono channel to stereo
                if audio_data.ndim == 1:
                    return np.column_stack([audio_data, audio_data])
                else:
                    return np.column_stack([audio_data[:, 0], audio_data[:, 0]])
            else:
                # Take first two channels
                return audio_data[:, :2]
                
        else:
            raise ValueError(f"Unsupported target channel count: {target_channels}")
    
    def convert_audio(self, audio_data: np.ndarray, current_rate: int, current_bits: int, 
                     current_channels: int, target_rate: Optional[int] = None, 
                     target_bits: Optional[int] = None, target_channels: Optional[int] = None) -> np.ndarray:
        """
        Convert audio data to target format.
        
        IMPORTANT: This method NEVER modifies the source audio data. It creates a copy
        and returns the converted copy, leaving the original data unchanged.
        
        Args:
            audio_data: Input audio data
            current_rate: Current sample rate
            current_bits: Current bit depth
            current_channels: Current channel count
            target_rate: Target sample rate (uses default if None)
            target_bits: Target bit depth (uses default if None)
            target_channels: Target channel count (uses default if None)
            
        Returns:
            Converted audio data (copy, original unchanged)
        """
        target_rate = target_rate or self.default_sample_rate
        target_bits = target_bits or self.default_bit_depth
        target_channels = target_channels or self.default_channels
        
        logger.info(f"Converting audio: {current_rate}Hz/{current_bits}bit/{current_channels}ch -> {target_rate}Hz/{target_bits}bit/{target_channels}ch")
        
        # Apply conversions in order: sample rate -> channels -> bit depth
        converted_data = audio_data.copy()
        
        # 1. Sample rate conversion
        if current_rate != target_rate:
            converted_data = self.convert_sample_rate(converted_data, current_rate, target_rate)
            
        # 2. Channel conversion
        if current_channels != target_channels:
            converted_data = self.convert_channels(converted_data, current_channels, target_channels)
            
        # 3. Bit depth conversion
        if current_bits != target_bits:
            converted_data = self.convert_bit_depth(converted_data, current_bits, target_bits)
            
        return converted_data
    
    def normalize_audio(self, audio_data: np.ndarray, target_db: float = -18.0) -> np.ndarray:
        """
        Normalize audio to a target dB level.
        
        Args:
            audio_data: Input audio data
            target_db: Target dB level
            
        Returns:
            Normalized audio data
        """
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        if rms == 0:
            return audio_data
            
        # Convert target dB to linear scale
        target_linear = 10 ** (target_db / 20.0)
        
        # Calculate gain
        gain = target_linear / rms
        
        # Apply gain
        normalized = audio_data * gain
        
        # Clip to prevent clipping
        normalized = np.clip(normalized, -1.0, 1.0)
        
        return normalized
