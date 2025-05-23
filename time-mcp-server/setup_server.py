#!/usr/bin/env python3
"""
Setup script for Time MCP Server.
Installs required dependencies and sets up the server environment.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("Setting up Time MCP Server...")
    
    # Get the directory this script is in
    script_dir = Path(__file__).resolve().parent
    
    # Install dependencies
    print("Installing dependencies...")
    requirements_path = script_dir / "requirements.txt"
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
    ])
    
    # Create .vscode directory for examples if it doesn't exist
    examples_vscode_dir = script_dir / "examples" / ".vscode"
    os.makedirs(examples_vscode_dir, exist_ok=True)
    
    # Create the mcp.json file
    mcp_json_path = examples_vscode_dir / "mcp.json"
    if not mcp_json_path.exists():
        with open(mcp_json_path, "w") as f:
            f.write('''{
    "servers": [
        {
            "name": "time-mcp-server",
            "command": [
                "python", "-m", "server.main"
            ],
            "cwd": "${workspaceFolder}/..",
            "title": "Time MCP Server",
            "description": "A server for time utilities and timezone conversions with Melbourne, Australia focus"
        }
    ]
}''')
    
    print("Setup complete!")
    print("\nTo run the Time MCP Server:")
    print("1. Navigate to the time-mcp-server directory")
    print("2. Run: python -m server.main")
    print("\nFor VS Code integration:")
    print("1. Open the 'examples' directory in VS Code")
    print("2. Use the MCP extension to start the server")

if __name__ == "__main__":
    main()
