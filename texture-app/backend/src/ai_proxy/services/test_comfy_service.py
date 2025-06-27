#!/usr/bin/env python3
"""
Test script for ComfyUIAPIWrapper.generate_avatar_with_initial_pose method.
This script tests the generation of multiple poses from a prompt.
"""

import os
import sys
import base64
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the comfy_service module
sys.path.append(str(Path(__file__).parent.parent))

from services.comfy_service import ComfyUIAPIWrapper

def test_generate_avatar_with_initial_pose():
    """
    Test the generate_avatar_with_initial_pose method of ComfyUIAPIWrapper.
    This will generate an initial pose and multiple additional poses.
    """
    # Create a ComfyUIAPIWrapper instance
    wrapper = ComfyUIAPIWrapper()
    
    # Create a test directory for output
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Test parameters - you can modify these as needed
    test_params = {
        'prompt': "attractive 20yo 1girl, anime, cartoon, pink eyes, black hair, shoulder length hair, plain white t-shirt, blue mini skirt"
    }
    
    # Optional: Add a base64 image if you want to use a custom reference image
    # with open('/path/to/reference/image.jpg', 'rb') as f:
    #     test_params['image'] = base64.b64encode(f.read()).decode('utf-8')
    
    logger.info("Starting avatar generation with multiple poses...")
    
    try:
        # Call the generate_avatar_with_initial_pose method
        
        # Check if there was an error
        if 'error' in result:
            logger.error(f"Error in generation: {result['error']}")
            return False
        
        # Save the results to files for inspection
        logger.info("Generation successful! Saving poses to output directory...")
        
        # Save the results as individual image files
        for pose_name, pose_base64 in result.items():
            output_path = os.path.join(output_dir, f"{pose_name}.png")
            
            # Save the base64 image to a file
            with open(output_path, 'wb') as f:
                image_data = base64.b64decode(pose_base64)
                f.write(image_data)
            
            logger.info(f"Saved {pose_name} to {output_path}")
        
        # Also save the entire result dictionary as a JSON file for reference
        json_output_path = os.path.join(output_dir, "poses_result.json")
        with open(json_output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Saved complete result to {json_output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing wrapper: {str(e)}")
        return False

def main():
    """Main function to run the test"""
    logger.info("=== Testing ComfyUIAPIWrapper.generate_avatar_with_initial_pose ===")
    
    success = test_generate_avatar_with_initial_pose()
    
    if success:
        logger.info("Test completed successfully!")
    else:
        logger.error("Test failed!")

if __name__ == "__main__":
    main()
