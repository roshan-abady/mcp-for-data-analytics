# Quick Start Guide

This guide will help you get started with the Time MCP Server quickly.

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd time-mcp-server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or use the setup script:

```bash
python setup_server.py
```

## Running the Server

To start the Time MCP Server:

```bash
python -m server.main
```

This will start the server with the default configuration, using Australia/Melbourne as the default timezone.

## Quick Examples

### Using the Client Example

The `examples/client_example.py` script is provided to demonstrate the server functionality:

```bash
# Get current time in Melbourne
python examples/client_example.py --action current

# Get current time in New York
python examples/client_example.py --action current --timezone "America/New_York"

# Convert time from Melbourne to New York
python examples/client_example.py --action convert --time "14:30" --source "Australia/Melbourne" --target "America/New_York"

# Get detailed information about the Melbourne timezone
python examples/client_example.py --action timezone --timezone "Australia/Melbourne"

# List all Australian timezones
python examples/client_example.py --action list --country "AU"

# Access the Melbourne time resource directly
python examples/client_example.py --action resource --resource "time://melbourne"
```

### Using VS Code Extension

If you have the MCP VS Code extension installed:

1. Open the `examples` directory in VS Code
2. Use the MCP extension to start the server
3. Access server tools and resources through the extension

## Next Steps

- Check out the [README.md](../README.md) for detailed documentation
- Explore the available [tools](../README.md#available-tools) and [resources](../README.md#resource-uri-scheme)
- Try the available [prompts](../README.md#prompts) for meeting scheduling, travel planning, and team coordination
- Configure the server with a custom [configuration file](../README.md#configuration)
