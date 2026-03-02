"""Script to generate sample test images"""
import os
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np


def create_sample_car_image(width: int = 800, height: int = 600, image_num: int = 1) -> Image.Image:
    """Create a sample car damage image
    
    Args:
        width: Image width
        height: Image height
        image_num: Image number for variation
        
    Returns:
        PIL Image object
    """
    # Create base image with colors
    img = Image.new("RGB", (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    
    # Draw car shape
    if image_num == 1:
        # Front bumper damage
        draw.rectangle([100, 300, 300, 350], fill=(100, 100, 100), outline=(0, 0, 0))
        draw.rectangle([105, 305, 295, 345], fill=(150, 0, 0), outline=(0, 0, 0), width=2)
        draw.text((250, 200), "Front Bumper Damage", fill=(0, 0, 0))
    
    elif image_num == 2:
        # Door panel damage
        draw.rectangle([400, 200, 500, 400], fill=(100, 100, 100), outline=(0, 0, 0), width=2)
        draw.polygon([(420, 250), (480, 260), (470, 330), (410, 320)], fill=(150, 0, 0))
        draw.text((350, 100), "Door Panel Damage", fill=(0, 0, 0))
    
    elif image_num == 3:
        # Fender damage
        draw.ellipse([600, 300, 750, 400], fill=(100, 100, 100), outline=(0, 0, 0), width=2)
        draw.ellipse([630, 330, 700, 360], fill=(150, 0, 0), outline=(0, 0, 0), width=2)
        draw.text((550, 200), "Fender Damage", fill=(0, 0, 0))
    
    elif image_num == 4:
        # Hood damage
        draw.rectangle([200, 150, 600, 250], fill=(100, 100, 100), outline=(0, 0, 0), width=2)
        draw.polygon([(250, 180), (350, 170), (370, 220), (280, 230)], fill=(150, 0, 0))
        draw.polygon([(400, 190), (500, 175), (520, 230), (420, 240)], fill=(200, 50, 50))
        draw.text((250, 280), "Hood with Multiple Dents", fill=(0, 0, 0))
    
    elif image_num == 5:
        # Roof damage
        draw.polygon([(200, 100), (600, 80), (650, 200), (200, 220)], fill=(100, 100, 100), outline=(0, 0, 0))
        draw.polygon([(300, 130), (550, 120), (570, 180), (310, 190)], fill=(150, 0, 0), outline=(200, 0, 0), width=3)
        draw.text((250, 300), "Severe Roof Damage", fill=(0, 0, 0))
    
    # Add damage intensity gradient noise
    arr = np.array(img)
    noise = np.random.randint(-20, 20, arr.shape)
    arr = np.clip(arr.astype(int) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    
    return img


def generate_test_images(output_dir: str = "tests/fixtures/images"):
    """Generate sample test images
    
    Args:
        output_dir: Directory to save images
    """
    # Create directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate 5 sample images
    for i in range(1, 6):
        image = create_sample_car_image(800, 600, i)
        image_path = os.path.join(output_dir, f"car_damage_{i}.jpg")
        image.save(image_path, "JPEG", quality=90)
        print(f"Created: {image_path}")


if __name__ == "__main__":
    generate_test_images()
    print("\nTest images generated successfully!")
