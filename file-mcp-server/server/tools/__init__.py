import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastmcp import Server
from fastmcp.schemas import Tool, Function, FunctionCall

from server.utils.config import Config
from server.utils.filesystem import FileSystemHelper

logger = logging.getLogger(__name__)

def register_tools(server: Server, config: Config) -> None:
    """Register all tools with the MCP server."""
    fs_helper = FileSystemHelper(config)
    
    # Register directory listing tool
    @server.tool("file.list_directory")
    async def list_directory(path: str, recursive: bool = False, max_depth: int = 3) -> Dict[str, Any]:
        """
        List files and directories in the specified directory.
        
        Args:
            path: Path to directory (relative to root or absolute)
            recursive: Whether to list subdirectories recursively
            max_depth: Maximum recursion depth when recursive=True
            
        Returns:
            Dict containing directory contents and metadata
        """
        logger.info(f"Listing directory: {path} (recursive={recursive})")
        
        # Normalize and validate path
        dir_path, is_valid = fs_helper.normalize_path(path)
        if not is_valid:
            return {"error": f"Invalid or inaccessible path: {path}"}
        
        if not dir_path.exists():
            return {"error": f"Path does not exist: {path}"}
        
        if not dir_path.is_dir():
            return {"error": f"Path is not a directory: {path}"}
        
        try:
            # Get directory contents
            items = fs_helper.list_directory(dir_path, recursive, max_depth)
            
            # Get metadata for the directory itself
            dir_metadata = fs_helper.get_file_metadata(dir_path)
            
            return {
                "path": str(dir_path.relative_to(config.root_dir)),
                "absolutePath": str(dir_path),
                "metadata": dir_metadata,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return {"error": f"Error listing directory: {str(e)}"}
    
    # Register file reading tool
    @server.tool("file.read_content")
    async def read_file_content(path: str) -> Dict[str, Any]:
        """
        Read the content of a file safely.
        
        Args:
            path: Path to file (relative to root or absolute)
            
        Returns:
            Dict containing file content and metadata
        """
        logger.info(f"Reading file: {path}")
        
        # Normalize and validate path
        file_path, is_valid = fs_helper.normalize_path(path)
        if not is_valid:
            return {"error": f"Invalid or inaccessible path: {path}"}
        
        if not file_path.exists():
            return {"error": f"File does not exist: {path}"}
        
        if not file_path.is_file():
            return {"error": f"Path is not a file: {path}"}
        
        try:
            # Get file metadata
            metadata = fs_helper.get_file_metadata(file_path)
            
            # Check file size
            if file_path.stat().st_size > config.max_file_size:
                return {
                    "error": f"File too large to read ({metadata['size_human']})",
                    "metadata": metadata
                }
            
            # Read file content
            content = fs_helper.read_file(file_path)
            
            return {
                "path": str(file_path.relative_to(config.root_dir)),
                "absolutePath": str(file_path),
                "metadata": metadata,
                "content": content
            }
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {"error": f"Error reading file: {str(e)}"}
    
    # Register file search tool
    @server.tool("file.search")
    async def search_files(pattern: str, path: str = ".", recursive: bool = True, 
                        include_content: bool = False) -> Dict[str, Any]:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: Search pattern (glob pattern or regex if it starts with r/)
            path: Directory to search in (relative to root or absolute)
            recursive: Whether to search subdirectories recursively
            include_content: Whether to include file content in results
            
        Returns:
            Dict containing search results
        """
        logger.info(f"Searching for files matching pattern '{pattern}' in {path}")
        
        # Normalize and validate path
        search_dir, is_valid = fs_helper.normalize_path(path)
        if not is_valid:
            return {"error": f"Invalid or inaccessible path: {path}"}
        
        if not search_dir.exists():
            return {"error": f"Path does not exist: {path}"}
        
        if not search_dir.is_dir():
            return {"error": f"Path is not a directory: {path}"}
        
        try:
            # Search for files
            results = fs_helper.search_files(
                pattern, search_dir, recursive, include_content
            )
            
            return {
                "pattern": pattern,
                "path": str(search_dir.relative_to(config.root_dir)),
                "absolutePath": str(search_dir),
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Error searching for files with pattern '{pattern}': {e}")
            return {"error": f"Error searching for files: {str(e)}"}
    
    # Register file metadata tool
    @server.tool("file.get_metadata")
    async def get_file_metadata(path: str) -> Dict[str, Any]:
        """
        Get metadata for a file or directory.
        
        Args:
            path: Path to file/directory (relative to root or absolute)
            
        Returns:
            Dict containing file/directory metadata
        """
        logger.info(f"Getting metadata for: {path}")
        
        # Normalize and validate path
        file_path, is_valid = fs_helper.normalize_path(path)
        if not is_valid:
            return {"error": f"Invalid or inaccessible path: {path}"}
        
        if not file_path.exists():
            return {"error": f"Path does not exist: {path}"}
        
        try:
            # Get metadata
            metadata = fs_helper.get_file_metadata(file_path)
            
            return {
                "path": str(file_path.relative_to(config.root_dir)),
                "absolutePath": str(file_path),
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error getting metadata for {path}: {e}")
            return {"error": f"Error getting metadata: {str(e)}"}
    
    # Register file path analysis tool
    @server.tool("file.analyze_path")
    async def analyze_path(path: str) -> Dict[str, Any]:
        """
        Analyze a file path for safety and validity.
        
        Args:
            path: Path to analyze (relative to root or absolute)
            
        Returns:
            Dict containing path analysis results
        """
        logger.info(f"Analyzing path: {path}")
        
        # Normalize path
        norm_path, is_valid = fs_helper.normalize_path(path)
        
        # Check if path exists
        exists = norm_path.exists()
        
        # Check path type if it exists
        path_type = None
        if exists:
            if norm_path.is_dir():
                path_type = "directory"
            elif norm_path.is_file():
                path_type = "file"
            elif norm_path.is_symlink():
                path_type = "symlink"
            else:
                path_type = "other"
        
        # Check if path is excluded by patterns
        is_excluded = fs_helper.is_path_excluded(norm_path)
        
        # Get path components
        try:
            relative_path = norm_path.relative_to(config.root_dir)
            components = list(relative_path.parts)
        except ValueError:
            components = []
        
        return {
            "originalPath": path,
            "normalizedPath": str(norm_path),
            "relativePath": str(relative_path) if is_valid else None,
            "isValid": is_valid,
            "exists": exists,
            "type": path_type,
            "isExcluded": is_excluded,
            "components": components,
            "security": {
                "isWithinRoot": is_valid,
                "isAccessible": is_valid and exists and not is_excluded,
                "isExcluded": is_excluded
            }
        }