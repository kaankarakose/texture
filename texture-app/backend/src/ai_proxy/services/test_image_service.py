#!/usr/bin/env python3
import os
import json
import base64
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the image_service module
sys.path.append(str(Path(__file__).parent.parent))

from services.image_service import ImageGenerationService, ImageGenerationParameters

def main():
    """
    Test the ImageGenerationService using the Base64 encoded image from image.json
    """
    print("Testing ImageGenerationService...")
    
    # Load the Base64 encoded image from image.json
    json_file_path = os.path.join(os.path.dirname(__file__), 'resources', 'images', 'image.json')
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            base64_image = data.get('image', '')
            if not base64_image:
                print("Error: No image found in image.json")
                return
    except Exception as e:
        print(f"Error loading image.json: {e}")
        return
    
    # Create a simple mask (empty for testing)
    # In a real scenario, you would create a proper mask
    # For testing, we'll create a simple white mask of the same size
    try:
        # Extract the image data from the base64 string
        image_data = base64_image.split(',')[1] if ',' in base64_image else base64_image
        decoded_image = base64.b64decode(image_data)
        
        # Create a simple white mask (all white pixels)
        # For simplicity, we'll create a small white square mask
        width, height = 100, 100  # Small mask for testing
        white_mask = bytearray([255] * (width * height * 4))  # RGBA format
        mask_base64 = base64.b64encode(white_mask).decode('utf-8')
        mask_with_header = f"data:image/png;base64,{mask_base64}"
    except Exception as e:
        print(f"Error creating mask: {e}")
        return
    
    # Initialize the ImageGenerationService
    service = ImageGenerationService(base_url="http://localhost:8187")
    
    # Create parameters for image generation
    params = ImageGenerationParameters(
        image=base64_image,
        mask=mask_with_header,
        positive_prompt="A beautiful landscape with mountains and a lake",
        negative_prompt="blurry, distorted"
    )
    
    # Make the request to the image generation service
    try:
        print("Sending request to image generation service...")
        result = service.generate_image(params)
        
        # Check if the result contains the generated image
        if result and 'image' in result:
            print("Image generation successful!")
            
            # Save the generated image
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'generated_image.png')
            
            service.save_base64_image(result['image'], output_path)
            print(f"Generated image saved to: {output_path}")
        else:
            print("Error: No image in the response")
            print(f"Response: {result}")
    except Exception as e:
        print(f"Error generating image: {e}")

if __name__ == "__main__":
    main()
