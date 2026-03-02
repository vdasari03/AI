"""Unit tests for image processing module"""
import pytest
import tempfile
import os
from pathlib import Path
from PIL import Image
import numpy as np

from src.image_processor import ImageProcessor
from tests.mocks.utils import create_mock_image, save_mock_image


@pytest.fixture
def temp_image_dir():
    """Create temporary directory with test images"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test image
        image = create_mock_image(800, 600)
        image.save(os.path.join(tmpdir, "test_image.jpg"))
        
        yield tmpdir


@pytest.fixture
def image_processor():
    """Create ImageProcessor instance"""
    return ImageProcessor()


def test_image_processor_initialization(image_processor):
    """Test ImageProcessor initialization"""
    assert image_processor.max_image_size == ImageProcessor.MAX_IMAGE_SIZE
    assert image_processor.SUPPORTED_FORMATS == {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


def test_validate_image_path_valid(image_processor, temp_image_dir):
    """Test validating a valid image path"""
    image_path = os.path.join(temp_image_dir, "test_image.jpg")
    assert image_processor.validate_image_path(image_path) is True


def test_validate_image_path_nonexistent(image_processor):
    """Test validating a nonexistent path"""
    assert image_processor.validate_image_path("/nonexistent/path/image.jpg") is False


def test_validate_image_path_unsupported_format(image_processor, temp_image_dir):
    """Test validating unsupported file format"""
    unsupported_file = os.path.join(temp_image_dir, "test.bmp")
    Path(unsupported_file).touch()
    
    # BMP is supported, so let's use a different extension
    unsupported_file = os.path.join(temp_image_dir, "test.txt")
    Path(unsupported_file).touch()
    
    assert image_processor.validate_image_path(unsupported_file) is False


def test_load_image(image_processor, temp_image_dir):
    """Test loading an image"""
    image_path = os.path.join(temp_image_dir, "test_image.jpg")
    image = image_processor.load_image(image_path)
    
    assert image is not None
    assert isinstance(image, Image.Image)
    assert image.format == "JPEG"


def test_load_image_invalid_path(image_processor):
    """Test loading image from invalid path"""
    image = image_processor.load_image("/invalid/path/image.jpg")
    assert image is None


def test_get_image_metadata(image_processor):
    """Test extracting image metadata"""
    image = create_mock_image(800, 600)
    metadata = image_processor.get_image_metadata(image)
    
    assert metadata["width"] == 800
    assert metadata["height"] == 600
    assert metadata["size"] == (800, 600)
    assert metadata["mode"] == "RGB"


def test_resize_image(image_processor):
    """Test resizing image"""
    original_image = create_mock_image(1600, 1200)
    resized_image = image_processor.resize_image(original_image, max_width=800)
    
    assert resized_image.width == 800
    assert resized_image.height == 600


def test_resize_image_no_resize_needed(image_processor):
    """Test resizing when image is already small"""
    original_image = create_mock_image(400, 300)
    resized_image = image_processor.resize_image(original_image, max_width=800)
    
    assert resized_image.width == 400
    assert resized_image.height == 300


def test_get_image_array(image_processor):
    """Test getting image as numpy array"""
    image = create_mock_image(100, 100)
    array = image_processor.get_image_array(image)
    
    assert isinstance(array, np.ndarray)
    assert array.shape == (100, 100, 3)
    assert array.dtype == np.uint8
