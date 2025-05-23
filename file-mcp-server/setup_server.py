#!/usr/bin/env python3
"""
Setup script for the File MCP Server.

This script helps with installing and configuring the File MCP Server,
including creating a VS Code configuration.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path


def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    print("Dependencies installed successfully.")


def create_vscode_config(target_dir, root_dir=None):
    """Create VSCode configuration files."""
    print("Creating VS Code configuration...")
    
    # Create .vscode directory if it doesn't exist
    vscode_dir = Path(target_dir) / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    # Create mcp.json
    mcp_config = {
        "name": "File MCP Server",
        "rootDir": root_dir or "${workspaceFolder}",
        "excludePatterns": [
            "**/.git/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.venv/**",
            "**/.vscode/**",
            "**/dist/**",
            "**/build/**"
        ],
        "maxFileSize": 10485760,
        "maxFilesPerDirectory": 1000,
        "maxSearchResults": 100,
        "respectGitignore": True,
        "serverName": "File MCP Server",
        "serverVersion": "0.1.0",
        "serverDescription": "Secure, read-only access to files"
    }
    
    with open(vscode_dir / "mcp.json", "w") as f:
        json.dump(mcp_config, f, indent=4)
    
    # Copy launch.json if it exists in examples
    example_launch = Path(__file__).parent / "examples" / ".vscode" / "launch.json"
    if example_launch.exists():
        with open(example_launch, "r") as src, open(vscode_dir / "launch.json", "w") as dst:
            dst.write(src.read())
    
    print(f"VS Code configuration created in {vscode_dir}")


def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(description="Setup File MCP Server")
    parser.add_argument("--target-dir", type=str, default=".",
                       help="Directory to create VS Code configuration in")
    parser.add_argument("--root-dir", type=str,
                       help="Root directory to serve files from (defaults to target dir)")
    parser.add_argument("--skip-install", action="store_true",
                       help="Skip installing dependencies")
    args = parser.parse_args()
    
    target_dir = Path(args.target_dir).resolve()
    root_dir = Path(args.root_dir).resolve() if args.root_dir else None
    
    print(f"Setting up File MCP Server")
    print(f"Target directory: {target_dir}")
    if root_dir:
        print(f"Root directory: {root_dir}")
    
    # Install dependencies
    if not args.skip_install:
        install_dependencies()
    
    # Create VS Code config
    create_vscode_config(target_dir, str(root_dir) if root_dir else None)
    
    print("\nSetup complete!")
    print("\nTo start the server:")
    print("  file-mcp-server")
    print("\nOr configure your MCP client/extension to use this server.")


if __name__ == "__main__":
    main()
