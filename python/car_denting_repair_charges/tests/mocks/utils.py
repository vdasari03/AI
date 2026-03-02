"""Mock utilities for testing"""
from unittest.mock import Mock, MagicMock
from PIL import Image
import numpy as np
from io import BytesIO


def create_mock_image(width: int = 800, height: int = 600) -> Image.Image:
    """Create a mock PIL image for testing
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        PIL Image object
    """
    # Create a simple image with random pixel data
    img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(img_array, "RGB")


def save_mock_image(file_path: str, width: int = 800, height: int = 600) -> str:
    """Create and save a mock image
    
    Args:
        file_path: Path to save the image
        width: Image width
        height: Image height
        
    Returns:
        Path to saved image
    """
    image = create_mock_image(width, height)
    image.save(file_path)
    return file_path


def create_mock_llm_provider():
    """Create a mock LLM provider
    
    Returns:
        Mock provider object
    """
    provider = Mock()
    provider.analyze_image = MagicMock(return_value={
        "damages": [
            {
                "location": "bumper",
                "severity": "moderate",
                "estimated_size_inches": 2.0,
                "description": "Test damage",
                "repair_type": "repairable",
                "repair_complexity": "medium",
            }
        ]
    })
    return provider
