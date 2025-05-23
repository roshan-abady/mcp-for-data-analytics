"""
Tests for the configuration utilities.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path

from server.utils.config import Config, load_config


def test_config_defaults():
    """Test Config class defaults."""
    # Create config with only required parameters
    config = Config(root_dir=Path("/tmp"))
    
    # Check defaults are applied
    assert config.root_dir == Path("/tmp")
    assert len(config.exclude_patterns) == 0
    assert config.max_file_size == 10 * 1024 * 1024  # 10MB
    assert config.default_mime_type == "application/octet-stream"
    assert config.max_files_per_directory == 1000
    assert config.max_search_results == 100
    assert config.respect_gitignore is True
    assert config.server_name == "File MCP Server"
    assert config.server_version == "0.1.0"


def test_load_config_from_file():
    """Test loading configuration from a file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        # Create a temporary config file
        config_data = {
            "rootDir": "/test/root",
            "excludePatterns": ["*.tmp", "**/.git/**"],
            "maxFileSize": 5242880,  # 5MB
            "serverName": "Test Server"
        }
        json.dump(config_data, tmp)
        tmp_path = tmp.name
    
    try:
        # Load config from file
        config = load_config(tmp_path)
        
        # Check values from file are applied
        assert config.root_dir == Path("/test/root").resolve()
        assert "*.tmp" in config.exclude_patterns
        assert "**/.git/**" in config.exclude_patterns
        assert config.max_file_size == 5242880
        assert config.server_name == "Test Server"
        
        # Check defaults for fields not in file
        assert config.default_mime_type == "application/octet-stream"
        assert config.max_files_per_directory == 1000
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_load_config_with_relative_paths():
    """Test loading configuration with relative paths."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_dir = Path(tmp_dir) / "config"
        config_dir.mkdir()
        
        # Create a config file with a relative path
        config_path = config_dir / "config.json"
        config_data = {
            "rootDir": "../data"  # Relative to config file location
        }
        
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        # Create the data directory
        data_dir = Path(tmp_dir) / "data"
        data_dir.mkdir()
        
        # Load config
        config = load_config(str(config_path))
        
        # Check relative path is resolved correctly
        expected_path = (Path(tmp_dir) / "data").resolve()
        assert config.root_dir == expected_path


def test_load_config_errors():
    """Test error handling in config loading."""
    # Test with non-existent directory
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        config_data = {
            "rootDir": "/this/path/does/not/exist"
        }
        json.dump(config_data, tmp)
        tmp_path = tmp.name
    
    try:
        # Should raise ValueError for non-existent directory
        with pytest.raises(ValueError):
            load_config(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
