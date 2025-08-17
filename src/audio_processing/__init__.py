"""
Audio Processing Module

This module handles all audio processing operations including:
- Audio file loading and validation
- Sample rate and bit depth conversion
- Channel conversion (mono/stereo)
- Sample chain creation and concatenation
- Audio format export

IMPORTANT: This module NEVER modifies source audio files. All processing is done
on copies of the audio data in memory. Original files remain completely unchanged.
"""

from .audio_processor import AudioProcessor
from .sample_chain_builder import SampleChainBuilder
from .audio_converter import AudioConverter
from .chain_exporter import ChainExporter

__all__ = [
    'AudioProcessor',
    'SampleChainBuilder', 
    'AudioConverter',
    'ChainExporter'
]



