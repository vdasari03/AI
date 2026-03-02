"""Pytest configuration and fixtures"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.logger import configure_logging


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Configure logging for tests"""
    configure_logging(log_level="DEBUG")


@pytest.fixture
def test_data_dir():
    """Get path to test data directory"""
    return Path(__file__).parent / "fixtures"
