from flask import Flask, request, jsonify
import os
import sys
import logging
from typing import Optional, Dict, Any
from inpaint import Inpainter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import your LLM model
# Replace this with your actual import

app = Flask(__name__)

inpainter = Inpainter()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})


@app.route('/generate_inpaint', methods=['POST'])
def generate_inpaint():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        print(data)

        # Extract parameters from data
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Extract optional parameters
        image = data.get("image")
        mask = data.get("mask")
        
        # Call the inpainting function from the LLM model
        result = inpainter.generate(
            prompt=prompt,
            init_image=image,
            mask_image=mask,
        )
        
        response = {
            "status": "success",
            "message": "Inpainting completed",
            "result": result
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        port = 8186
        logger.info(f"Starting inpainting server on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)