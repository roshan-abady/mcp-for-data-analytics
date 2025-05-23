#!/usr/bin/env python3
"""
Time MCP Server main entry point.

This is a Model Context Protocol server that provides time-related utilities
with a focus on Melbourne, Australia as the default timezone.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastmcp import Server, StdioTransport
from fastmcp.errors import MCPError

# Add the parent directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.utils.config import load_config, Config
from server.utils.logging_setup import setup_logging
from server.tools import register_tools
from server.resources import register_resources
from server.prompts import register_prompts

# Configure logging
logger = logging.getLogger(__name__)

def create_server(config: Config) -> Server:
    """Create and configure the MCP server with tools, resources, and prompts."""
    transport = StdioTransport()
    server = Server(transport, name="Time MCP Server")
    
    # Register components
    register_tools(server, config)
    register_resources(server, config)
    register_prompts(server, config)
    
    return server

def main():
    """Main entry point for the Time MCP Server."""
    parser = argparse.ArgumentParser(description="Time MCP Server")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--log-level", type=str, default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help="Logging level")
    parser.add_argument("--log-file", type=str, help="Log file path")
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    log_file = args.log_file
    setup_logging(log_level, log_file)
    
    # Load configuration
    config_path = None
    if args.config:
        config_path = Path(args.config)
    
    try:
        config = load_config(config_path)
        logger.info(f"Loaded configuration: {config}")
        
        # Create and start the server
        server = create_server(config)
        logger.info("Starting Time MCP Server...")
        server.start()
        
    except MCPError as e:
        logger.error(f"MCP error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
