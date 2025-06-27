import json
import requests
import base64
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union
import os

logger = logging.getLogger(__name__)

@dataclass
class ImageGenerationParameters:
    image: str  # Base64 encoded image

## clas mask 
class ImageGenerationService:
    """Service for handling image generation requests to the image generation API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or "http://localhost:11245"
        
    def generate_image(self, params: ImageGenerationParameters) -> Dict[str, Any]:
        """Generate an image using the provided parameters
        
        Args:
            params: The parameters for image generation
            
        Returns:
            The response from the image generation API
        """
        try:
            # Prepare the request payload
            payload = {
                "image": params.image,
            }
            
            # Send the request to the image generation API
            response = requests.post(
                f"{self.base_url}/process_image",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=80,
                verify=False  # verify=False to ignore SSL certificate validation

            )
            
            # Raise an exception if the request failed
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with image generation API: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing response from image generation API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in image generation: {str(e)}")
            raise
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode an image file to base64
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            logger.error(f"Error encoding image to base64: {str(e)}")
            raise
    
    def save_base64_image(self, base64_string: str, output_path: str) -> str:
        """Save a base64 encoded image to a file
        
        Args:
            base64_string: The base64 encoded image string
            output_path: Path where the image should be saved
            
        Returns:
            The path to the saved image
        """
        try:
            image_data = base64.b64decode(base64_string)
            with open(output_path, 'wb') as f:
                f.write(image_data)
            return output_path
        except Exception as e:
            logger.error(f"Error saving base64 image: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage for testing with image.json
    service = ImageGenerationService()
    
    # Test with the image from image.json
    try:
        # Load the Base64 encoded image from image.json
        json_file_path = os.path.join(os.path.dirname(__file__), 'resources', 'images', 'image.json')
        print(f"Loading image from: {json_file_path}")
        
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            base64_image = data.get('image', '')
            if not base64_image:
                print("Error: No image found in image.json")
                exit(1)
        
        print("Successfully loaded image from image.json")
        
        # Create a simple white mask for testing
        # In a real scenario, you would create a proper mask
        
        # Create parameters
        params = ImageGenerationParameters(
            image=base64_image
        )
        
        print("Sending request to image generation service...")
        # Generate image
        result = service.generate_image(params)
        print("Generation successful!")
        
        # Save the result if it contains a base64 image
        if "image" in result:
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the generated image
            output_path = os.path.join(output_dir, 'generated_image.png')
            service.save_base64_image(result["image"], output_path)
            print(f"Image saved to: {output_path}")
        else:
            print("Error: No image in the response")
            print(f"Response: {result}")
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")
