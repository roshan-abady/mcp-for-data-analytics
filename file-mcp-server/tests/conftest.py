"""
Test configuration and fixtures for the File MCP Server tests.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

from server.utils.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration with a temporary root directory."""
    return Config(
        root_dir=temp_dir,
        exclude_patterns=["**/excluded/**", "*.exclude"],
        max_file_size=1024 * 1024,  # 1MB
        default_mime_type="application/octet-stream",
        max_files_per_directory=100,
        max_search_results=50,
        respect_gitignore=True,
        server_name="Test File MCP Server",
        server_version="0.1.0",
        server_description="Test server"
    )


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files and directories for testing."""
    # Create directories
    (temp_dir / "docs").mkdir()
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "excluded").mkdir()
    
    # Create sample files
    (temp_dir / "README.md").write_text("# Test Project\n\nThis is a test project.")
    (temp_dir / "docs" / "index.md").write_text("# Documentation\n\nTest documentation.")
    (temp_dir / "src" / "main.py").write_text("print('Hello, world!')")
    (temp_dir / "src" / "utils.py").write_text("def add(a, b):\n    return a + b")
    (temp_dir / "tests" / "test_utils.py").write_text(
        "import unittest\n\nclass TestUtils(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(1, 2), 3)"
    )
    (temp_dir / "excluded" / "secret.txt").write_text("This should be excluded")
    (temp_dir / "large.bin").write_bytes(os.urandom(1024 * 1024 * 2))  # 2MB file
    (temp_dir / "test.exclude").write_text("This should be excluded by pattern")
    
    # Create .gitignore
    (temp_dir / ".gitignore").write_text("*.log\ntemp/\n")
    (temp_dir / "ignored.log").write_text("This should be ignored by .gitignore")
    (temp_dir / "temp").mkdir()
    (temp_dir / "temp" / "cache.txt").write_text("This should be ignored by .gitignore")
    
    return temp_dir
