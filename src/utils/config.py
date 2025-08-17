"""
Configuration Management for NI Sample Chainer

Basic configuration handling utilities.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Configuration management utility."""
    
    @staticmethod
    def load_config(config_path: Path) -> Dict[str, Any]:
        """Load configuration from a YAML file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def save_config(config_data: Dict[str, Any], config_path: Path) -> None:
        """Save configuration to a YAML file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)



