"""
Pytest configuration for Time MCP Server tests.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.utils.config import Config
from server.utils.timezone_utils import TimezoneUtils


@pytest.fixture
def config():
    """Return a default configuration for tests."""
    return Config()


@pytest.fixture
def timezone_utils(config):
    """Return a TimezoneUtils instance for tests."""
    return TimezoneUtils(default_timezone=config.default_timezone)
