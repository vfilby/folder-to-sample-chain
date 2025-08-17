"""
Logging Management for NI Sample Chainer

Basic logging utilities and configuration.
"""

import logging
from pathlib import Path
from typing import Optional

class LogManager:
    """Logging management utility."""
    
    @staticmethod
    def setup_logging(
        log_level: int = logging.INFO,
        log_file: Optional[Path] = None,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('ni_sample_chainer')
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger



