import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastmcp import Server
from fastmcp.schemas import ResourceInfo

from server.utils.config import Config
from server.utils.filesystem import FileSystemHelper

logger = logging.getLogger(__name__)

def register_resources(server: Server, config: Config) -> None:
    """Register file resources with the MCP server."""
    fs_helper = FileSystemHelper(config)
    
    @server.resource_provider("file://")
    async def file_resource_provider(uri: str) -> Optional[ResourceInfo]:
        """
        Provide file resources using the file:// URI scheme.
        
        This handler processes file:// URIs and returns the content and metadata
        for the requested file if it's accessible.
        
        Args:
            uri: The file:// URI to resolve
            
        Returns:
            ResourceInfo if the file is accessible, None otherwise
        """
        logger.info(f"Resource request for: {uri}")
        
        # Extract path from URI
        if not uri.startswith("file://"):
            return None
        
        path_str = uri[7:]
        
        # Normalize and validate path
        file_path, is_valid = fs_helper.normalize_path(path_str)
        if not is_valid:
            logger.warning(f"Invalid or inaccessible resource path: {path_str}")
            return None
        
        # Check if path exists
        if not file_path.exists():
            logger.warning(f"Resource path does not exist: {path_str}")
            return None
        
        try:
            # Get file metadata
            metadata = fs_helper.get_file_metadata(file_path)
            
            # Determine resource type
            if file_path.is_dir():
                # For directories, return a structured representation
                items = fs_helper.list_directory(file_path)
                
                # Format directory listing as structured content
                content = {
                    "type": "directory",
                    "path": str(file_path.relative_to(config.root_dir)),
                    "name": file_path.name,
                    "items": items,
                    "count": len(items)
                }
                
                return ResourceInfo(
                    uri=uri,
                    name=f"Directory: {file_path.name}",
                    content=content,
                    metadata={
                        "mime_type": "application/json",
                        "file_metadata": metadata
                    }
                )
            else:
                # For files, check size limits
                if file_path.stat().st_size > config.max_file_size:
                    logger.warning(f"File too large for resource: {path_str}")
                    return ResourceInfo(
                        uri=uri,
                        name=f"File: {file_path.name}",
                        content=f"[File too large: {metadata['size_human']}]",
                        metadata={
                            "mime_type": "text/plain",
                            "file_metadata": metadata,
                            "error": "File too large to read"
                        }
                    )
                
                # Read file content
                content = fs_helper.read_file(file_path)
                if content is None:
                    logger.warning(f"Failed to read file content: {path_str}")
                    return ResourceInfo(
                        uri=uri,
                        name=f"File: {file_path.name}",
                        content="[Failed to read file content]",
                        metadata={
                            "mime_type": "text/plain",
                            "file_metadata": metadata,
                            "error": "Failed to read file content"
                        }
                    )
                
                return ResourceInfo(
                    uri=uri,
                    name=f"File: {file_path.name}",
                    content=content,
                    metadata={
                        "mime_type": metadata["mime_type"],
                        "file_metadata": metadata
                    }
                )
        except Exception as e:
            logger.error(f"Error processing resource {uri}: {e}")
            return None