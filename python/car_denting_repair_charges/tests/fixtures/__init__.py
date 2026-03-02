"""Initialize test fixtures"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_test_images import generate_test_images
from tests.mocks.utils import save_mock_image

if __name__ == "__main__":
    print("Initializing test fixtures...")
    
    # Generate test images
    test_images_dir = "tests/fixtures/images"
    generate_test_images(test_images_dir)
    
    print(f"\n✓ Test fixtures initialized in {test_images_dir}")
    print(f"✓ Generated 5 sample car damage images")
    print("\nYou can now run tests with: pytest")
