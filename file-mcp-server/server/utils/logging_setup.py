import os
import sys
import logging
from typing import Optional
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up logging for the MCP server.
    
    Args:
        log_level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to a log file
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create logs directory if using log file and parent directory doesn't exist
    if log_file:
        log_path = Path(log_file)
        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            *([] if not log_file else [logging.FileHandler(log_file)])
        ]
    )
    
    # Reduce verbosity of some libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('watchdog').setLevel(logging.WARNING)
