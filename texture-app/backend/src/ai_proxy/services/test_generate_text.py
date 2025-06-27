#!/usr/bin/env python
import requests
import json
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_generate_text(base_url="localhost", port="8000", message="Can you help me generate a wood texture?"):
    """
    Test the generate_text endpoint
    
    Args:
        base_url (str): Base URL of the backend server
        port (str): Port of the backend server
        message (str): Message to send to the LLM
    
    Returns:
        bool: True if the test was successful, False otherwise
    """
    url = f"http://{base_url}:{port}/api/ai_proxy/llm/generate/"
    
    logger.info(f"Testing generate_text endpoint at {url}")
    # Prepare the request payload
    payload = {
        "message": message,
        "system_prompt": "You are a helpful assistant specializing in texture generation."
    }
    
    try:
        logger.info(f"URL: {url}")
        logger.info(f"Payload: {payload}")
        
        response = requests.post(
            url, 
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Get the raw response text first
                raw_text = response.text
                print("\nRaw response text:")
                print(raw_text)
                print("\nResponse type:", type(raw_text))
                
                # Try to parse the JSON
                result = response.json()
                print("\nParsed JSON result:")
                print(result)
                print("\nResult type:", type(result))
                
                # If result is a string that looks like JSON, try to parse it again
                if isinstance(result, str) and (result.startswith('{') or result.startswith('[')):
                    try:
                        print("\nResult appears to be a JSON string, trying to parse it:")
                        result = json.loads(result)
                        print("After second parsing:", type(result))
                        print(result)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON string: {e}")
                
                # Now try to extract the answer
                try:
                    if isinstance(result, dict):
                        if "received_data" in result and isinstance(result["received_data"], dict):
                            answer = result["received_data"].get("answer", "")
                            print("\nExtracted Answer:")
                            print(answer)
                        else:
                            print("\nCouldn't find received_data in the result dictionary")
                            print("Available keys:", result.keys())
                    else:
                        print("\nResult is not a dictionary, cannot extract answer")
                except Exception as e:
                    print(f"Error extracting answer: {e}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse response as JSON: {response.text}")
                return False
        else:
            logger.error(f"Generate text request failed with status code {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    # Get command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = sys.argv[2] if len(sys.argv) > 2 else "8000"
    message = sys.argv[3] if len(sys.argv) > 3 else "Can you help me generate a wood texture?"
    
    # Run the test
    test_generate_text(base_url, port, message)
