"""
Logging setup for Time MCP Server.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Union

def setup_logging(level: int = logging.INFO, log_file: Optional[Union[str, Path]] = None) -> None:
    """
    Set up logging for the Time MCP Server.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Suppress excessive logging from libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
