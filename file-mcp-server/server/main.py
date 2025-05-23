import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastmcp import Server, StdioTransport
from fastmcp.errors import MCPError

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
    server = Server(transport, name="File MCP Server")
    
    # Register components
    register_tools(server, config)
    register_resources(server, config)
    register_prompts(server, config)
    
    return server

def main():
    """Main entry point for the File MCP Server."""
    parser = argparse.ArgumentParser(description="File MCP Server")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--root-dir", type=str, help="Root directory to serve")
    parser.add_argument("--log-level", type=str, default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help="Logging level")
    parser.add_argument("--log-file", type=str, help="Log file path")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level, log_file=args.log_file)
    
    # Load config
    try:
        config = load_config(args.config)
        
        # Override config with command line arguments if provided
        if args.root_dir:
            config.root_dir = Path(args.root_dir).resolve()
            
        logger.info(f"Starting File MCP Server with root directory: {config.root_dir}")
        
        # Create and start server
        server = create_server(config)
        server.start()
        
    except MCPError as e:
        logger.error(f"MCP Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
