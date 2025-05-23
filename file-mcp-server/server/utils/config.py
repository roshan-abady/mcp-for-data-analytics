import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for the File MCP Server."""
    # Root directory to serve files from
    root_dir: Path
    
    # Exclude patterns (similar to .gitignore format)
    exclude_patterns: List[str] = field(default_factory=list)
    
    # Max file size to read in bytes (default 10MB)
    max_file_size: int = 10 * 1024 * 1024
    
    # Default MIME type when detection fails
    default_mime_type: str = "application/octet-stream"
    
    # Maximum number of files to return in directory listings
    max_files_per_directory: int = 1000
    
    # Maximum number of search results
    max_search_results: int = 100
    
    # Enable .gitignore support
    respect_gitignore: bool = True
    
    # Server metadata
    server_name: str = "File MCP Server"
    server_version: str = "0.1.0"
    server_description: str = "Secure, read-only access to files"

def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from a JSON file.
    
    If config_path is not provided, it will look for:
    1. .vscode/mcp.json in the current directory
    2. fallback to reasonable defaults
    
    Returns:
        Config: The loaded configuration
    """
    config_data = {}
    
    # Try to load from provided path
    if config_path:
        try:
            config_path = Path(config_path).resolve()
            logger.info(f"Loading config from: {config_path}")
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
    
    # Try to load from .vscode/mcp.json if no config provided or loading failed
    if not config_data:
        vscode_config = Path.cwd() / '.vscode' / 'mcp.json'
        if vscode_config.exists():
            try:
                logger.info(f"Loading config from: {vscode_config}")
                with open(vscode_config, 'r') as f:
                    config_data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load .vscode/mcp.json: {e}")
    
    # Set root directory
    root_dir = None
    if 'rootDir' in config_data:
        # Handle both absolute and relative paths
        root_dir_path = Path(config_data['rootDir'])
        if not root_dir_path.is_absolute():
            # If relative, resolve from config file location or current directory
            if config_path:
                root_dir = (Path(config_path).parent / root_dir_path).resolve()
            else:
                root_dir = (Path.cwd() / root_dir_path).resolve()
        else:
            root_dir = root_dir_path.resolve()
    
    # Default to current directory if not specified
    if not root_dir:
        root_dir = Path.cwd().resolve()
        logger.info(f"No root directory specified, using current directory: {root_dir}")
    
    # Validate root directory exists
    if not root_dir.exists() or not root_dir.is_dir():
        raise ValueError(f"Root directory does not exist or is not a directory: {root_dir}")
    
    # Create Config object with defaults and overrides from config file
    return Config(
        root_dir=root_dir,
        exclude_patterns=config_data.get('excludePatterns', []),
        max_file_size=config_data.get('maxFileSize', 10 * 1024 * 1024),
        default_mime_type=config_data.get('defaultMimeType', 'application/octet-stream'),
        max_files_per_directory=config_data.get('maxFilesPerDirectory', 1000),
        max_search_results=config_data.get('maxSearchResults', 100),
        respect_gitignore=config_data.get('respectGitignore', True),
        server_name=config_data.get('serverName', 'File MCP Server'),
        server_version=config_data.get('serverVersion', '0.1.0'),
        server_description=config_data.get('serverDescription', 'Secure, read-only access to files')
    )
