"""Image processing module for car damage assessment"""
import os
from pathlib import Path
from typing import Optional, Tuple
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handle image loading, validation, and preprocessing"""
    
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    MAX_IMAGE_SIZE = 5242880  # 5MB
    
    def __init__(self, max_image_size: int = MAX_IMAGE_SIZE):
        """Initialize image processor
        
        Args:
            max_image_size: Maximum allowed image size in bytes
        """
        self.max_image_size = max_image_size
    
    def validate_image_path(self, image_path: str) -> bool:
        """Validate if image path exists and is supported
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(image_path):
            logger.warning(f"Image path does not exist: {image_path}")
            return False
        
        # Check file extension
        file_extension = Path(image_path).suffix.lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            logger.warning(f"Unsupported image format: {file_extension}")
            return False
        
        # Check file size
        file_size = os.path.getsize(image_path)
        if file_size > self.max_image_size:
            logger.warning(f"Image size exceeds limit: {file_size} > {self.max_image_size}")
            return False
        
        return True
    
    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from file
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image object or None if loading fails
        """
        if not self.validate_image_path(image_path):
            return None
        
        try:
            image = Image.open(image_path)
            logger.info(f"Successfully loaded image: {image_path}")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {str(e)}")
            return None
    
    def get_image_metadata(self, image: Image.Image) -> dict:
        """Extract metadata from image
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary containing image metadata
        """
        return {
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
        }
    
    def resize_image(self, image: Image.Image, max_width: int = 800) -> Image.Image:
        """Resize image if needed
        
        Args:
            image: PIL Image object
            max_width: Maximum width in pixels
            
        Returns:
            Resized image
        """
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            return image.resize((max_width, new_height), Image.Resampling.LANCZOS)
        return image
    
    def get_image_array(self, image: Image.Image) -> np.ndarray:
        """Convert image to numpy array
        
        Args:
            image: PIL Image object
            
        Returns:
            Numpy array representation of image
        """
        return np.array(image)
