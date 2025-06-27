#!/usr/bin/env python3
import requests
import logging
import json
import os
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_kaan_endpoint(base_url="localhost", port="8187", use_https=False):
    """
    Test the /kaan endpoint of the LLM service.
    
    Args:
        base_url (str): Base URL of the LLM service
        port (str): Port of the LLM service
        use_https (bool): Whether to use HTTPS instead of HTTP
    
    Returns:
        bool: True if the test was successful, False otherwise
    """
    protocol = "https" if use_https else "http"
    url = f"{protocol}://{base_url}:{port}/kaan"
    
    logger.info(f"Testing connection to {url}")
    
    try:
        response = requests.get(url, timeout=10, verify=False)  # verify=False to ignore SSL certificate validation
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info(f"Connection successful! Response: {response.text}")
            return True
        else:
            logger.error(f"Connection failed with status code {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error: {str(e)}")
        return False

def test_llm_chat_completion(base_url="localhost", port="8187", use_https=False):
    """
    Test the chat completion functionality of the LLM service.
    
    Args:
        base_url (str): Base URL of the LLM service
        port (str): Port of the LLM service
        use_https (bool): Whether to use HTTPS instead of HTTP
    
    Returns:
        bool: True if the test was successful, False otherwise
    """
    protocol = "https" if use_https else "http"
    url = f"{protocol}://{base_url}:{port}/generate_answer"
    
    logger.info(f"Testing chat completion at {url}")
    
    # Prepare the request payload
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, can you test if this connection is working?"}
        ]
    }

    # payload = {'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'},
    #  {'role': 'user', 'content': 'Can you help me generate a wood texture?'}]
    #  }
    
    try:
        print(f"{url=}")
        print(f"{payload=}")
        response = requests.post(
            url, 
            json=payload,
            timeout=30,
            verify=False  # verify=False to ignore SSL certificate validation
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info("Chat completion successful!")
                logger.info(f"Response: {json.dumps(result, indent=2)}")
                return True
            except json.JSONDecodeError:
                logger.error(f"Failed to parse response as JSON: {response.text}")
                return False
        else:
            logger.error(f"Chat completion failed with status code {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    # Get environment variables or use defaults
    base_url = os.environ.get("LLM_SERVICE_URL", "localhost")
    port = os.environ.get("LLM_SERVICE_PORT", "8187")
    
    # Remove 'http://' or 'https://' prefix if present
    if base_url.startswith("http://"):
        base_url = base_url[7:]
    elif base_url.startswith("https://"):
        base_url = base_url[8:]
    
    # Parse command line arguments
    use_https = "--https" in sys.argv
    test_kaan = "--kaan" in sys.argv or len(sys.argv) == 1
    test_chat = "--chat" in sys.argv or len(sys.argv) == 1
    
    print(f"{'='*50}")
    print(f"LLM Service Test")
    print(f"{'='*50}")
    print(f"Base URL: {base_url}")
    print(f"Port: {port}")
    print(f"Protocol: {'HTTPS' if use_https else 'HTTP'}")
    print(f"{'='*50}\n")
    
    # Run the tests
    results = []
    
    if test_kaan:
        print("\nTesting /kaan endpoint...")
        kaan_result = test_kaan_endpoint(base_url, port, use_https)
        results.append(("Kaan Endpoint", kaan_result))
    
    if test_chat:
        print("\nTesting chat completion...")
        chat_result = test_llm_chat_completion(base_url, port, use_https)
        results.append(("Chat Completion", chat_result))
    
    # Print summary
    print(f"\n{'='*50}")
    print("Test Results Summary:")
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    print(f"{'='*50}")
    
    # Exit with appropriate status code
    sys.exit(0 if all(result for _, result in results) else 1)