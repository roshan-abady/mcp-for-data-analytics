# Quickstart Guide

This guide will help you get started with the File MCP Server, a secure, read-only MCP server for file system access.

## Installation

1. Clone the repository and install the package:

```bash
git clone https://github.com/yourusername/file-mcp-server.git
cd file-mcp-server
pip install -e .
```

2. Run the setup script to create VSCode configuration:

```bash
python setup_server.py --target-dir /path/to/your/project
```

## Running the Server

You can run the server directly using the command-line interface:

```bash
file-mcp-server --root-dir /path/to/serve
```

Or using the Python module:

```bash
python -m server.main --root-dir /path/to/serve
```

## VS Code Integration

If you're using VS Code with the MCP extension:

1. Open your project in VS Code
2. Configure your MCP extension to use the File MCP Server
3. The server will automatically use the configuration from `.vscode/mcp.json`

## Example Usage

### Using MCP Tools

Here are some examples of how to use the MCP tools provided by the server:

#### List Directory

```python
result = await client.run_tool("file.list_directory", {"path": "."})
```

#### Read File Content

```python
result = await client.run_tool("file.read_content", {"path": "README.md"})
```

#### Search Files

```python
result = await client.run_tool("file.search", {
    "pattern": "*.py",
    "path": "src",
    "recursive": True
})
```

#### Get File Metadata

```python
result = await client.run_tool("file.get_metadata", {"path": "setup.py"})
```

### Accessing File Resources

You can access files as resources using the `file://` URI scheme:

```python
resource = await client.get_resource("file:///absolute/path/to/file.txt")
# or 
resource = await client.get_resource("file://./relative/path/to/file.txt")
```

### Using Prompts

The server provides specialized prompts for working with files:

#### Code Review

```python
prompts = await client.get_prompt("file.code_review", {
    "file_uri": "file://path/to/code.py"
})
```

#### File Summarization

```python
prompts = await client.get_prompt("file.summarize", {
    "file_uri": "file://path/to/document.md"
})
```

#### Project Structure Analysis

```python
prompts = await client.get_prompt("file.project_structure", {
    "directory_uri": "file://path/to/project"
})
```

## Running the Example Client

The repository includes an example client to demonstrate the server functionality:

```bash
python examples/client_example.py --action list --path .
python examples/client_example.py --action read --path README.md
python examples/client_example.py --action search --path . --pattern "*.py"
python examples/client_example.py --action resource --path /absolute/path/to/file.txt
python examples/client_example.py --action code-review --path path/to/code.py
```

## Configuration Options

You can configure the server by editing `.vscode/mcp.json` or by providing a custom config file:

```json
{
    "rootDir": "/path/to/serve",
    "excludePatterns": ["**/.git/**", "**/node_modules/**"],
    "maxFileSize": 10485760,
    "respectGitignore": true
}
```

For more details, see the [full documentation](README.md).
