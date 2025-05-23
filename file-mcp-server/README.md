# File MCP Server

A secure, read-only Model Context Protocol (MCP) server for accessing files and directories using the Python FastMCP SDK.

## Features

- 🔒 **Secure, read-only access** to files in a specified directory
- 📄 **File resource provider** using the `file://` URI scheme
- 🔍 **File search and browsing tools** for navigating directory structures
- 🛡️ **Security features** including path traversal protection
- 📋 **MIME type detection** for different file types
- 🔧 **Optimized for VSCode integration** with proper configuration support
- 🧰 **Comprehensive tools** for listing directories, reading files, and more
- 💬 **Specialized prompts** for code review, file summarization, and project structure analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/file-mcp-server.git
cd file-mcp-server

# Install the package
pip install -e .
```

## Usage

### Command Line

Run the server with default settings (serving the current directory):

```bash
file-mcp-server
```

Specify a custom root directory:

```bash
file-mcp-server --root-dir /path/to/serve
```

Use a configuration file:

```bash
file-mcp-server --config path/to/config.json
```

Set logging level:

```bash
file-mcp-server --log-level DEBUG
```

### VSCode Integration

1. Copy the example configuration from `examples/.vscode/mcp.json` to your project's `.vscode/mcp.json`
2. Customize the settings as needed
3. Configure your VSCode MCP extension to use this server

## Configuration

The server can be configured using a JSON file or command-line arguments:

```json
{
    "rootDir": "/path/to/serve",
    "excludePatterns": [
        "**/.git/**",
        "**/node_modules/**"
    ],
    "maxFileSize": 10485760,
    "respectGitignore": true
}
```

### Configuration Options

| Option                 | Description                                   | Default                  |
| ---------------------- | --------------------------------------------- | ------------------------ |
| `rootDir`              | Root directory to serve files from            | Current directory        |
| `excludePatterns`      | Patterns of files/directories to exclude      | Common system dirs       |
| `maxFileSize`          | Maximum file size to read in bytes            | 10MB                     |
| `defaultMimeType`      | Default MIME type when detection fails        | application/octet-stream |
| `maxFilesPerDirectory` | Maximum number of files in directory listings | 1000                     |
| `maxSearchResults`     | Maximum number of search results              | 100                      |
| `respectGitignore`     | Whether to respect .gitignore files           | true                     |

## MCP Components

### Tools

The server provides the following MCP tools:

| Tool Name             | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `file.list_directory` | List files and directories in the specified directory |
| `file.read_content`   | Read the content of a file safely                     |
| `file.search`         | Search for files matching a pattern                   |
| `file.get_metadata`   | Get metadata for a file or directory                  |
| `file.analyze_path`   | Analyze a file path for safety and validity           |

### Resources

| Resource Scheme | Description                          |
| --------------- | ------------------------------------ |
| `file://`       | Access files and directories by path |

### Prompts

| Prompt Name              | Description                                       |
| ------------------------ | ------------------------------------------------- |
| `file.code_review`       | Generate prompts for code review of a file        |
| `file.summarize`         | Generate prompts for summarizing a file's content |
| `file.project_structure` | Generate prompts for analyzing project structure  |

## Security Features

- ✅ Path traversal protection
- ✅ Respect for .gitignore patterns
- ✅ File size limits
- ✅ Read-only access
- ✅ Excluded system directories and files
- ✅ Safe path normalization and validation

## Example Client Usage

```python
from fastmcp import Client

# Connect to the server
client = Client()

# List files in a directory
directory_listing = await client.run_tool("file.list_directory", {"path": "."})

# Read a file
file_content = await client.run_tool("file.read_content", {"path": "README.md"})

# Search for Python files
search_results = await client.run_tool("file.search", {
    "pattern": "*.py",
    "path": "server",
    "recursive": True
})

# Get file metadata
metadata = await client.run_tool("file.get_metadata", {"path": "setup.py"})

# Access a file resource
resource = await client.get_resource("file:///absolute/path/to/file.txt")
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/file-mcp-server.git
cd file-mcp-server

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run the server in debug mode
file-mcp-server --log-level DEBUG
```

## License

MIT License

## Credits

This project is built using the [Model Context Protocol](https://modelcontextprotocol.io/) and the [FastMCP](https://github.com/modelcontextprotocol/python-sdk) Python SDK.
