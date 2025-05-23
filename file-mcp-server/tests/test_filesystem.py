"""
Tests for the filesystem utility.
"""

import os
import pytest
from pathlib import Path

from server.utils.filesystem import FileSystemHelper


def test_file_system_helper_initialization(test_config, sample_files):
    """Test FileSystemHelper initialization."""
    fs_helper = FileSystemHelper(test_config)
    assert fs_helper.root_dir == test_config.root_dir
    assert fs_helper.config == test_config


def test_normalize_path(test_config, sample_files):
    """Test path normalization and validation."""
    fs_helper = FileSystemHelper(test_config)
    
    # Test valid paths
    valid_path, is_valid = fs_helper.normalize_path("README.md")
    assert is_valid
    assert valid_path == sample_files / "README.md"
    
    # Test with file:// URI
    uri_path, is_valid = fs_helper.normalize_path(f"file://{sample_files}/README.md")
    assert is_valid
    assert uri_path == sample_files / "README.md"
    
    # Test absolute path within root
    abs_path, is_valid = fs_helper.normalize_path(str(sample_files / "docs" / "index.md"))
    assert is_valid
    assert abs_path == sample_files / "docs" / "index.md"
    
    # Test path traversal attempt
    traversal_path, is_valid = fs_helper.normalize_path("../../../etc/passwd")
    assert not is_valid
    
    # Test path outside root
    outside_path, is_valid = fs_helper.normalize_path("/etc/passwd")
    assert not is_valid


def test_exclude_patterns(test_config, sample_files):
    """Test exclude patterns functionality."""
    fs_helper = FileSystemHelper(test_config)
    
    # Test excluded directory
    excluded_dir = sample_files / "excluded"
    assert fs_helper.is_path_excluded(excluded_dir)
    
    # Test excluded file by pattern
    excluded_file = sample_files / "test.exclude"
    assert fs_helper.is_path_excluded(excluded_file)
    
    # Test non-excluded file
    normal_file = sample_files / "README.md"
    assert not fs_helper.is_path_excluded(normal_file)


def test_gitignore_respect(test_config, sample_files):
    """Test .gitignore pattern respect."""
    fs_helper = FileSystemHelper(test_config)
    
    # Test file ignored by .gitignore
    ignored_file = sample_files / "ignored.log"
    assert fs_helper.is_path_excluded(ignored_file)
    
    # Test directory ignored by .gitignore
    ignored_dir = sample_files / "temp"
    assert fs_helper.is_path_excluded(ignored_dir)
    
    # Test file in ignored directory
    ignored_nested = sample_files / "temp" / "cache.txt"
    assert fs_helper.is_path_excluded(ignored_nested)


def test_file_metadata(test_config, sample_files):
    """Test file metadata retrieval."""
    fs_helper = FileSystemHelper(test_config)
    
    # Test metadata for a text file
    readme_path = sample_files / "README.md"
    metadata = fs_helper.get_file_metadata(readme_path)
    
    assert metadata["name"] == "README.md"
    assert metadata["path"] == "README.md"
    assert metadata["uri"] == f"file://{readme_path}"
    assert metadata["size"] > 0
    assert metadata["is_directory"] is False
    assert "text/" in metadata["mime_type"]
    assert metadata["extension"] == "md"
    assert metadata["hash"] is not None
    
    # Test metadata for a directory
    docs_path = sample_files / "docs"
    dir_metadata = fs_helper.get_file_metadata(docs_path)
    
    assert dir_metadata["name"] == "docs"
    assert dir_metadata["path"] == "docs"
    assert dir_metadata["is_directory"] is True
    assert dir_metadata["mime_type"] == "inode/directory"


def test_list_directory(test_config, sample_files):
    """Test directory listing."""
    fs_helper = FileSystemHelper(test_config)
    
    # Test non-recursive listing
    root_listing = fs_helper.list_directory(sample_files)
    
    # Should include visible dirs and files, exclude hidden and patterns
    assert any(item["name"] == "README.md" for item in root_listing)
    assert any(item["name"] == "docs" for item in root_listing)
    assert any(item["name"] == "src" for item in root_listing)
    assert any(item["name"] == "tests" for item in root_listing)
    
    # Should not include excluded or ignored items
    assert not any(item["name"] == "excluded" for item in root_listing)
    assert not any(item["name"] == "test.exclude" for item in root_listing)
    assert not any(item["name"] == "ignored.log" for item in root_listing)
    assert not any(item["name"] == "temp" for item in root_listing)
    
    # Test recursive listing
    recursive_listing = fs_helper.list_directory(sample_files, recursive=True)
    
    # Should include nested files
    assert any(item["name"] == "index.md" for item in recursive_listing)
    assert any(item["name"] == "main.py" for item in recursive_listing)
    assert any(item["name"] == "utils.py" for item in recursive_listing)
    assert any(item["name"] == "test_utils.py" for item in recursive_listing)


def test_search_files(test_config, sample_files):
    """Test file searching."""
    fs_helper = FileSystemHelper(test_config)
    
    # Test glob pattern search
    py_files = fs_helper.search_files("*.py", sample_files)
    assert len(py_files) == 3  # main.py, utils.py, test_utils.py
    assert any(item["name"] == "main.py" for item in py_files)
    assert any(item["name"] == "utils.py" for item in py_files)
    assert any(item["name"] == "test_utils.py" for item in py_files)
    
    # Test regex pattern search
    md_files = fs_helper.search_files("r/.*\\.md$", sample_files)
    assert len(md_files) == 2  # README.md, index.md
    assert any(item["name"] == "README.md" for item in md_files)
    assert any(item["name"] == "index.md" for item in md_files)
    
    # Test search with content
    hello_files = fs_helper.search_files("r/Hello", sample_files, include_content=True)
    assert len(hello_files) == 1  # main.py
    assert hello_files[0]["name"] == "main.py"
    assert "content" in hello_files[0]


def test_read_file(test_config, sample_files):
    """Test file reading."""
    fs_helper = FileSystemHelper(test_config)
    
    # Test reading a text file
    readme_content = fs_helper.read_file(sample_files / "README.md")
    assert readme_content.startswith("# Test Project")
    
    # Test reading a Python file
    python_content = fs_helper.read_file(sample_files / "src" / "main.py")
    assert "print('Hello, world!')" in python_content
    
    # Test reading a large file (should return None if too large)
    large_content = fs_helper.read_file(sample_files / "large.bin")
    assert large_content is None
    
    # Test reading an excluded file (should fail with ValueError)
    with pytest.raises(ValueError):
        fs_helper.read_file(sample_files / "excluded" / "secret.txt")
