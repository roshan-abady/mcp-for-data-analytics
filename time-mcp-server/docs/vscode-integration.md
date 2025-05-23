# VS Code Integration Guide

This guide explains how to integrate the Time MCP Server with Visual Studio Code.

## Prerequisites

- Visual Studio Code
- Python extension for VS Code
- MCP extension for VS Code

## Setup

1. Open the `examples` directory in VS Code:

```bash
code time-mcp-server/examples
```

2. The `.vscode/mcp.json` file has already been configured with the server settings:

```json
{
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
}
```

## Starting the Server

1. Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P on macOS)
2. Type "MCP: Start Server" and select the command
3. Choose "Time MCP Server" from the list
4. The server will start in a terminal window

## Using the Server in VS Code

Once the server is running, you can interact with it in several ways:

### MCP Explorer

1. Open the MCP Explorer view in the Activity Bar
2. Expand the "Time MCP Server" node to see available tools, resources, and prompts
3. Click on a tool or resource to use it

### MCP Commands

1. Open the Command Palette
2. Type "MCP: Run Tool" and select the command
3. Choose a tool from the Time MCP Server
4. Enter the required parameters

### Code Completions (with appropriate extensions)

If you have AI code completion extensions that support MCP, you can use the Time MCP Server for completions related to time and timezone operations.

## Example Workflow

Here's an example workflow for using the Time MCP Server in VS Code:

1. Start the Time MCP Server using the MCP extension
2. Open the MCP Explorer view
3. Click on the "time.current" tool
4. Enter a timezone (e.g., "America/New_York") or leave blank for Melbourne time
5. View the results in the output panel

## Troubleshooting

If you encounter issues with the VS Code integration:

1. Check that the server is running (a terminal should be open with server logs)
2. Verify that the `.vscode/mcp.json` file exists and contains the correct configuration
3. Make sure the server dependencies are installed (`pip install -r requirements.txt`)
4. Check the MCP extension settings in VS Code

## Manual Server Start

If you prefer to start the server manually:

1. Open a terminal in VS Code (Terminal > New Terminal)
2. Navigate to the parent directory of the examples folder
3. Run the server:

```bash
python -m server.main
```

4. Configure the MCP extension to connect to the running server
