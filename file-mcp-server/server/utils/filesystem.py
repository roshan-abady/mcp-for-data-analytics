import os
import re
import magic
import logging
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

import pathspec
from gitignore_parser import parse_gitignore

from server.utils.config import Config

logger = logging.getLogger(__name__)

class FileSystemHelper:
    """Helper class for safely interacting with the file system."""
    
    def __init__(self, config: Config):
        """
        Initialize the file system helper.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.root_dir = config.root_dir
        
        # Initialize MIME type detection
        self.magic = magic.Magic(mime=True)
        mimetypes.init()
        
        # Compile exclude patterns
        self.exclude_spec = self._compile_exclude_patterns()
        
        # Parse .gitignore files if enabled
        self.gitignore_matchers = {}
        if config.respect_gitignore:
            self._load_gitignore_matchers()
    
    def _compile_exclude_patterns(self) -> pathspec.PathSpec:
        """Compile exclude patterns into a pathspec."""
        return pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, 
            self.config.exclude_patterns
        )
    
    def _load_gitignore_matchers(self) -> None:
        """Load .gitignore files from the root directory and its subdirectories."""
        for dirpath, _, filenames in os.walk(self.root_dir):
            if '.gitignore' in filenames:
                gitignore_path = Path(dirpath) / '.gitignore'
                try:
                    matcher = parse_gitignore(gitignore_path)
                    self.gitignore_matchers[dirpath] = matcher
                except Exception as e:
                    logger.warning(f"Failed to parse .gitignore at {gitignore_path}: {e}")
    
    def is_path_excluded(self, path: Path) -> bool:
        """
        Check if a path should be excluded based on exclude patterns and .gitignore.
        
        Args:
            path: The path to check
            
        Returns:
            bool: True if the path should be excluded, False otherwise
        """
        # Get relative path from root
        try:
            rel_path = path.relative_to(self.root_dir)
        except ValueError:
            # Path is not within root_dir
            return True
        
        # Check exclude patterns
        if self.exclude_spec.match_file(str(rel_path)):
            return True
        
        # Check .gitignore patterns if enabled
        if self.config.respect_gitignore:
            # Check each parent directory for .gitignore rules
            check_path = path
            while check_path != self.root_dir:
                parent_dir = str(check_path.parent)
                if parent_dir in self.gitignore_matchers:
                    if self.gitignore_matchers[parent_dir](str(path)):
                        return True
                check_path = check_path.parent
            
            # Check root directory
            root_dir_str = str(self.root_dir)
            if root_dir_str in self.gitignore_matchers:
                if self.gitignore_matchers[root_dir_str](str(path)):
                    return True
        
        return False
    
    def normalize_path(self, path_str: str) -> Tuple[Path, bool]:
        """
        Normalize and validate a path to prevent path traversal attacks.
        
        Args:
            path_str: The path string to normalize
            
        Returns:
            Tuple[Path, bool]: The normalized path and a boolean indicating if it's valid
        """
        # Handle file:// URIs
        if path_str.startswith("file://"):
            path_str = path_str[7:]
        
        # Convert to Path object
        path = Path(path_str)
        
        # If path is absolute, ensure it's within root_dir
        if path.is_absolute():
            try:
                path.relative_to(self.root_dir)
            except ValueError:
                logger.warning(f"Attempt to access path outside root directory: {path}")
                return path, False
        else:
            # For relative paths, resolve against root_dir
            path = (self.root_dir / path).resolve()
        
        # Final check that the path is within root_dir
        try:
            path.relative_to(self.root_dir)
        except ValueError:
            logger.warning(f"Path traversal attempt detected: {path}")
            return path, False
        
        # Check if path is excluded
        if self.is_path_excluded(path):
            logger.info(f"Path is excluded by patterns: {path}")
            return path, False
        
        return path, True
    
    def get_file_metadata(self, path: Path) -> Dict[str, Any]:
        """
        Get metadata for a file.
        
        Args:
            path: The path to the file
            
        Returns:
            Dict[str, Any]: Metadata including size, modification time, MIME type, etc.
        """
        stat = path.stat()
        
        # Detect MIME type
        try:
            mime_type = self.magic.from_file(str(path))
        except Exception as e:
            logger.warning(f"Error detecting MIME type for {path}: {e}")
            # Fallback to extension-based detection
            mime_type, _ = mimetypes.guess_type(path.name)
            if not mime_type:
                mime_type = self.config.default_mime_type
        
        # Calculate hash for small files
        file_hash = None
        if stat.st_size <= 1024 * 1024:  # Only hash files <= 1MB
            try:
                with open(path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                logger.warning(f"Error calculating hash for {path}: {e}")
        
        return {
            "name": path.name,
            "path": str(path.relative_to(self.root_dir)),
            "uri": f"file://{path}",
            "size": stat.st_size,
            "size_human": self._format_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "is_directory": path.is_dir(),
            "mime_type": mime_type if not path.is_dir() else "inode/directory",
            "extension": path.suffix.lstrip('.') if path.suffix else None,
            "hash": file_hash,
        }
    
    def list_directory(self, dir_path: Path, recursive: bool = False, 
                      max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        List contents of a directory, respecting exclude patterns.
        
        Args:
            dir_path: The directory path
            recursive: Whether to list recursively
            max_depth: Maximum recursion depth when recursive=True
            
        Returns:
            List[Dict[str, Any]]: List of file and directory metadata
        """
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")
        
        results = []
        count = 0
        
        if recursive:
            # Use os.walk for recursive listing with depth limit
            for current_depth, (dirpath, dirnames, filenames) in enumerate(os.walk(dir_path)):
                # Check depth limit
                if current_depth > max_depth:
                    continue
                
                current_dir = Path(dirpath)
                
                # Process directories
                for dirname in dirnames:
                    dir_full_path = current_dir / dirname
                    if not self.is_path_excluded(dir_full_path):
                        results.append(self.get_file_metadata(dir_full_path))
                        count += 1
                
                # Process files
                for filename in filenames:
                    file_full_path = current_dir / filename
                    if not self.is_path_excluded(file_full_path):
                        results.append(self.get_file_metadata(file_full_path))
                        count += 1
                
                # Check limit
                if count >= self.config.max_files_per_directory:
                    logger.warning(f"Directory listing limit reached: {count} items")
                    break
        else:
            # Non-recursive listing
            for item in dir_path.iterdir():
                if not self.is_path_excluded(item):
                    results.append(self.get_file_metadata(item))
                    count += 1
                    
                    # Check limit
                    if count >= self.config.max_files_per_directory:
                        logger.warning(f"Directory listing limit reached: {count} items")
                        break
        
        return results
    
    def search_files(self, search_pattern: str, search_dir: Path, 
                    recursive: bool = True, include_content: bool = False) -> List[Dict[str, Any]]:
        """
        Search for files matching a pattern.
        
        Args:
            search_pattern: Glob pattern or regex (if starts with 'r/')
            search_dir: Directory to search in
            recursive: Whether to search recursively
            include_content: Whether to include file content in results
            
        Returns:
            List[Dict[str, Any]]: List of matching file metadata
        """
        results = []
        count = 0
        
        # Determine if pattern is regex
        is_regex = search_pattern.startswith('r/')
        if is_regex:
            pattern = re.compile(search_pattern[2:])
        
        # Define a pattern matcher function
        def matches_pattern(path: Path) -> bool:
            if is_regex:
                return bool(pattern.search(path.name))
            else:
                return path.match(search_pattern)
        
        # Walk directory
        for dirpath, dirnames, filenames in os.walk(search_dir):
            # Skip excluded directories
            dirnames[:] = [d for d in dirnames if not self.is_path_excluded(Path(dirpath) / d)]
            
            # If not recursive, don't go deeper
            if not recursive and dirpath != str(search_dir):
                dirnames.clear()
                continue
            
            # Check files
            for filename in filenames:
                file_path = Path(dirpath) / filename
                
                # Skip excluded files
                if self.is_path_excluded(file_path):
                    continue
                
                # Check pattern match
                if matches_pattern(file_path):
                    result = self.get_file_metadata(file_path)
                    
                    # Include content if requested and file is not too large
                    if include_content and not file_path.is_dir():
                        try:
                            if file_path.stat().st_size <= self.config.max_file_size:
                                result["content"] = self.read_file(file_path)
                        except Exception as e:
                            logger.warning(f"Error reading file content for {file_path}: {e}")
                    
                    results.append(result)
                    count += 1
                    
                    # Check limit
                    if count >= self.config.max_search_results:
                        logger.warning(f"Search results limit reached: {count} items")
                        return results
        
        return results
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """
        Safely read a file's content, respecting size limits.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[str]: File content as string, or None if file is too large/unreadable
        """
        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        # Check file size
        if file_path.stat().st_size > self.config.max_file_size:
            logger.warning(f"File too large to read: {file_path} ({file_path.stat().st_size} bytes)")
            return None
        
        # Detect file encoding and read
        try:
            # Try to detect text encoding
            encoding = 'utf-8'  # Default encoding
            
            # Read the file
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                return f.read()
                
        except UnicodeDecodeError:
            # If text encoding fails, try binary mode
            try:
                with open(file_path, 'rb') as f:
                    binary_data = f.read()
                
                # Check if it's a binary file
                # A simple heuristic: if there are too many non-printable characters, it's binary
                if sum(1 for b in binary_data if b < 9 or (b > 13 and b < 32)) > len(binary_data) * 0.3:
                    return f"[Binary file: {self._format_size(len(binary_data))}]"
                
                # Try different encodings
                for enc in ['latin-1', 'utf-16', 'cp1252']:
                    try:
                        return binary_data.decode(enc, errors='replace')
                    except UnicodeDecodeError:
                        continue
                
                # Fallback to replacing errors
                return binary_data.decode('utf-8', errors='replace')
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in a human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
