"""
Configuration utilities for the Time MCP Server.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for the Time MCP Server."""
    
    # Default timezone (Australia/Melbourne)
    default_timezone: str = "Australia/Melbourne"
    
    # Date and time format settings
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Maximum number of timezones to return in listings
    max_timezones: int = 100
    
    # Cache settings
    cache_ttl: int = 300  # Time-to-live for cached data in seconds
    
    # Feature flags
    enable_dst_warnings: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create a Config instance from a dictionary."""
        return cls(
            default_timezone=data.get("default_timezone", "Australia/Melbourne"),
            date_format=data.get("date_format", "%Y-%m-%d"),
            time_format=data.get("time_format", "%H:%M:%S"),
            datetime_format=data.get("datetime_format", "%Y-%m-%d %H:%M:%S"),
            max_timezones=data.get("max_timezones", 100),
            cache_ttl=data.get("cache_ttl", 300),
            enable_dst_warnings=data.get("enable_dst_warnings", True),
        )

def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from a JSON file or use defaults.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Config object
    """
    # Default configuration
    config_data = {}
    
    # Check for configuration file in various locations
    if not config_path:
        # Check in current directory
        local_config = Path("config.json")
        if local_config.exists():
            config_path = local_config
        
        # Check in parent directory of this script
        script_dir = Path(__file__).resolve().parent.parent.parent
        parent_config = script_dir / "config.json"
        if parent_config.exists():
            config_path = parent_config
    
    # Load configuration file if it exists
    if config_path and config_path.exists():
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Error loading configuration from {config_path}: {e}")
            logger.warning("Using default configuration")
    else:
        logger.info("No configuration file found, using default configuration")
    
    # Create and return Config object
    return Config.from_dict(config_data)
