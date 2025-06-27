import requests
import logging
import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from django.conf import settings
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

@dataclass
class Message:
    """Data class for chat messages."""
    role: str  # 'system', 'user', or 'assistant'
    content: str

class LLMService:

    """
    A service class for interacting with a language model. 

    """

    def __init__(self, default_system_prompt = None, temperature = 0.7, use_https = False):
        # Use localhost without http:// or https:// prefix to avoid duplication
        self.base_url = os.environ.get('LLM_SERVICE_URL', 'localhost')
        self.port = os.environ.get('LLM_SERVICE_PORT', '8187')
        self.url = f"{self.base_url}:{self.port}"
        #LLM CONFIG
        if default_system_prompt is None:
            self.default_system_prompt = os.environ.get('LLM_DEFAULT_SYSTEM_PROMPT', 'You are a helpful assistant.') #
        else:
            self.default_system_prompt = default_system_prompt
        self.temperature = temperature # change this later when having the request.
        self.max_tokens = int(os.environ.get('LLM_MAX_TOKENS', '1024'))

        logger.info(f"LLM Service initialized with URL: {self.url}")

    def create_chat_completion(self, 
                              messages: List[Message], 
                              system_prompt: Optional[str] = None,
                              temperature: Optional[float] = None,
                              max_tokens: Optional[int] = None,
                              object_details: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a chat completion request to the LLM service.
        Args:
            messages: List of message objects with role and content
            system_prompt: Override the default system prompt
            temperature: Override the default temperature
            max_tokens: Override the default max_tokens
            
        Returns:
            Dict containing the LLM response
        """

        # No need for params variable as it's not used
        
        endpoint = f"{self.url}/generate_answer"
    
        ## What we send to the LLM service

        ## Here what to send to LLM service - simplified to match working test implementation
        payload = {
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
                }
  
        # Keep these parameters for debugging/logging purposes only
        debug_info = {
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens
        }

        # Add system prompt if provided or use default
        if system_prompt or self.default_system_prompt:
            system_message = system_prompt or self.default_system_prompt
            # Add to beginning of messages if not already there
            if not messages or messages[0].role != "system":
                system_message = f"{system_message}. These are the objects {object_details}."
            
                payload["messages"].insert(0, {"role": "system", "content": system_message})
                raise ValueError("System prompt not found")
        for msg in messages:
            if msg.role == 'system':
                msg.content = msg.content + f".These are the objects {object_details}. You shouldn't give any exact information about them. Instead, as a part of the game, you may give hints. Some descriptive words. Whenever,ever, you get one of this object in the User prompt, you should congratulate the user. ALways give the riddle one by one"
                payload["messages"].insert(0, {"role": "system", "content": msg.content})

        try:
            logger.debug("Sending request to {endpoint} with payload: {payload}")

            ## Here I need to send the request to the LLM service

            response = requests.post(
                endpoint, 
                json=payload,
                timeout=80,
                verify=False  # verify=False to ignore SSL certificate validation
            )
        # Check if the request was successful
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info("Chat completion successful!")
                    logger.info(f"Response: {json.dumps(result, indent=2)}")
                    return json.dumps(result, indent=2)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse response as JSON: {response.text}")
                    return False
            else:
                logger.error(f"Chat completion failed with status code {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with LLM service: {str(e)}")
            raise Exception(f"Failed to communicate with LLM service: {str(e)}")

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM service response: {str(e)}")
            raise Exception(f"Failed to parse LLM service response: {str(e)}")




if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize the LLM service
    llm_service = LLMService()
    print(f"LLM Service URL: {llm_service.url}")
    
    # Test connection by sending a simple message
    try:
        # Create a test message
        test_messages = [
            Message(role="user", content="Hello, can you test if this connection is working?")
        ]
        
        # Send the request
        print("Sending test request to LLM service...")
        response = llm_service.create_chat_completion(messages=test_messages)
        
        # Print the response
        print("\nConnection test successful!")
        print("Response from LLM service:")
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"\nConnection test failed: {str(e)}")

