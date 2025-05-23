# Time MCP Server

A comprehensive Model Context Protocol (MCP) server that provides time-related utilities and timezone conversions, with a focus on Melbourne, Australia as the default timezone.

## Features

- Get current time in any timezone
- Convert times between timezones
- Get detailed timezone information
- List available timezones by country or region
- Special utilities for Melbourne, Australia time
- Resources accessible via `time://` URI scheme
- Prompts for meeting scheduling, travel planning, and team coordination

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

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

## Usage

### Running the Server

To start the Time MCP Server:

```bash
python -m server.main
```

Optional arguments:
- `--config`: Path to a custom configuration file
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Path to log file

### VS Code Integration

1. Open the `examples` directory in VS Code
2. Install the MCP extension for VS Code
3. Use the MCP extension to start the server

### Using the Client Example

The `examples/client_example.py` script demonstrates how to interact with the Time MCP Server:

```bash
# Get current time in Melbourne (default)
python examples/client_example.py --action current

# Get current time in a specific timezone
python examples/client_example.py --action current --timezone "America/New_York"

# Convert time between timezones
python examples/client_example.py --action convert --time "14:30" --source "Australia/Melbourne" --target "America/New_York"

# Get timezone information
python examples/client_example.py --action timezone --timezone "Australia/Melbourne"

# List timezones for a country
python examples/client_example.py --action list --country "AU"

# Access a resource directly
python examples/client_example.py --action resource --resource "time://melbourne"
```

## Available Tools

The Time MCP Server provides the following tools:

### `time.current`

Get the current time in a specific timezone.

**Parameters:**
- `timezone` (optional): The timezone to get the current time for (defaults to Australia/Melbourne)

**Example:**
```python
result = await client.run_tool("time.current", {"timezone": "America/New_York"})
```

### `time.convert`

Convert a time from one timezone to another.

**Parameters:**
- `time_str`: The time string to convert (formats: "HH:MM", "HH:MM:SS", "YYYY-MM-DD HH:MM:SS")
- `source_timezone` (optional): The source timezone (defaults to Australia/Melbourne)
- `target_timezone` (optional): The target timezone (defaults to Australia/Melbourne)

**Example:**
```python
result = await client.run_tool("time.convert", {
    "time_str": "14:30",
    "source_timezone": "Australia/Melbourne",
    "target_timezone": "America/New_York"
})
```

### `time.timezone_info`

Get detailed information about a timezone.

**Parameters:**
- `timezone` (optional): The timezone to get information for (defaults to Australia/Melbourne)

**Example:**
```python
result = await client.run_tool("time.timezone_info", {"timezone": "Australia/Melbourne"})
```

### `time.list_timezones`

List available timezones, optionally filtered by country or region.

**Parameters:**
- `country_code` (optional): ISO country code to filter by (e.g., "AU" for Australia)
- `region` (optional): Region string to filter by (e.g., "Australia", "Europe")

**Example:**
```python
result = await client.run_tool("time.list_timezones", {"country_code": "AU"})
```

### `time.melbourne`

Get the current time in Melbourne, Australia.

**Parameters:** None

**Example:**
```python
result = await client.run_tool("time.melbourne", {})
```

## Resource URI Scheme

The Time MCP Server supports the following `time://` URIs:

- `time://current?timezone=Australia/Melbourne`: Current time in specified timezone
- `time://melbourne`: Current time in Melbourne, Australia
- `time://timezone/Australia/Melbourne`: Timezone information for specified timezone
- `time://timezones?country=AU`: List of timezones for specified country
- `time://convert?time=14:30&from=Australia/Melbourne&to=America/New_York`: Convert time between timezones

## Prompts

The Time MCP Server provides the following prompts:

- `time.meeting_scheduler`: Help schedule meetings across different timezones
- `time.travel_planner`: Assist with travel planning across timezones
- `time.team_coordination`: Help coordinate teams working across different timezones

## Configuration

The server can be configured via a JSON configuration file:

```json
{
    "default_timezone": "Australia/Melbourne",
    "date_format": "%Y-%m-%d",
    "time_format": "%H:%M:%S",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
    "max_timezones": 100,
    "cache_ttl": 300,
    "enable_dst_warnings": true
}
```

## License

[MIT License](LICENSE)

## Acknowledgements

This project is built using the [Model Context Protocol](https://modelcontextprotocol.io/) and the [FastMCP](https://github.com/modelcontextprotocol/python-sdk) Python SDK.
