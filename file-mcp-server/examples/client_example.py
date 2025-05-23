"""
Example client for the File MCP Server.

This script demonstrates how to use the File MCP Server tools and resources
from a client application.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any

from fastmcp import Client


async def list_directory(client: Client, path: str) -> None:
    """List a directory using the file.list_directory tool."""
    print(f"\n=== Listing directory: {path} ===\n")
    
    result = await client.run_tool("file.list_directory", {"path": path})
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print directory contents
    print(f"Found {result['count']} items in {result['path']}:\n")
    
    for item in result['items']:
        item_type = "📁" if item['is_directory'] else "📄"
        print(f"{item_type} {item['name']} ({item['size_human']})")


async def read_file(client: Client, path: str) -> None:
    """Read a file using the file.read_content tool."""
    print(f"\n=== Reading file: {path} ===\n")
    
    result = await client.run_tool("file.read_content", {"path": path})
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print file metadata
    meta = result['metadata']
    print(f"File: {meta['name']}")
    print(f"Size: {meta['size_human']}")
    print(f"MIME type: {meta['mime_type']}")
    print(f"Modified: {meta['modified']}")
    print("\n=== Content ===\n")
    
    # Truncate content if too long
    content = result['content']
    if len(content) > 1000:
        print(content[:1000] + "\n...(truncated)...")
    else:
        print(content)


async def search_files(client: Client, pattern: str, path: str) -> None:
    """Search for files using the file.search tool."""
    print(f"\n=== Searching for {pattern} in {path} ===\n")
    
    result = await client.run_tool("file.search", {
        "pattern": pattern,
        "path": path,
        "recursive": True
    })
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print search results
    print(f"Found {result['count']} matching items:\n")
    
    for item in result['results']:
        item_type = "📁" if item['is_directory'] else "📄"
        print(f"{item_type} {item['path']}")


async def get_file_resource(client: Client, path: str) -> None:
    """Get a file resource using the file:// URI scheme."""
    # Convert to absolute path for file:// URI
    if not path.startswith("/"):
        path = str(Path(path).resolve())
    
    uri = f"file://{path}"
    print(f"\n=== Getting resource: {uri} ===\n")
    
    resource = await client.get_resource(uri)
    
    if resource is None:
        print(f"Error: Resource not found or not accessible")
        return
    
    # Print resource metadata
    print(f"Resource URI: {resource.uri}")
    print(f"Resource name: {resource.name}")
    
    if hasattr(resource.metadata, "get"):
        mime_type = resource.metadata.get("mime_type", "Unknown")
        print(f"MIME type: {mime_type}")
    
    print("\n=== Content ===\n")
    
    # Truncate content if too long
    content = resource.content
    if isinstance(content, dict):
        # Format JSON-like content
        import json
        content_str = json.dumps(content, indent=2)
    elif isinstance(content, str):
        content_str = content
    else:
        content_str = str(content)
    
    if len(content_str) > 1000:
        print(content_str[:1000] + "\n...(truncated)...")
    else:
        print(content_str)


async def use_prompt(client: Client, prompt_type: str, params: Dict[str, Any]) -> None:
    """Use a prompt from the server."""
    print(f"\n=== Using prompt: {prompt_type} ===\n")
    
    prompts = await client.get_prompt(f"file.{prompt_type}", params)
    
    if not prompts:
        print("No prompts returned")
        return
    
    # Print the system and user prompts
    print("=== System Prompt ===\n")
    print(prompts.system)
    print("\n=== User Prompt ===\n")
    print(prompts.user)


async def main():
    """Main entry point for the example client."""
    parser = argparse.ArgumentParser(description="File MCP Server Example Client")
    parser.add_argument("--action", type=str, required=True,
                        choices=[
                            "list", "read", "search", "resource", 
                            "code-review", "summarize", "project-structure"
                        ],
                        help="Action to perform")
    parser.add_argument("--path", type=str, default=".",
                        help="Path to file or directory")
    parser.add_argument("--pattern", type=str,
                        help="Pattern for search action")
    args = parser.parse_args()
    
    # Create MCP client
    client = Client()
    
    try:
        # Perform the requested action
        if args.action == "list":
            await list_directory(client, args.path)
        elif args.action == "read":
            await read_file(client, args.path)
        elif args.action == "search":
            if not args.pattern:
                print("Error: Pattern required for search action")
                return
            await search_files(client, args.pattern, args.path)
        elif args.action == "resource":
            await get_file_resource(client, args.path)
        elif args.action == "code-review":
            await use_prompt(client, "code_review", {"file_uri": f"file://{args.path}"})
        elif args.action == "summarize":
            await use_prompt(client, "summarize", {"file_uri": f"file://{args.path}"})
        elif args.action == "project-structure":
            await use_prompt(client, "project_structure", {"directory_uri": f"file://{args.path}"})
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
