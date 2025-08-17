"""
File Utilities for NI Sample Chainer

Basic file handling and utility functions.
"""

from pathlib import Path
from typing import List, Optional

class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure a directory exists, creating it if necessary."""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_extension(file_path: Path) -> str:
        """Get the file extension from a path."""
        return file_path.suffix.lower()
    
    @staticmethod
    def is_audio_file(file_path: Path) -> bool:
        """Check if a file is an audio file."""
        audio_extensions = {'.wav', '.flac', '.aiff', '.mp3', '.ogg'}
        return file_path.suffix.lower() in audio_extensions



