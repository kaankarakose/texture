import os
from typing import List, Optional, Dict, Any, Union
import logging
import json
# Handle imports differently when running as a module vs directly

## Was it for testing!
# if __name__ == "__main__":
#     import sys
#     import django
#     from pathlib import Path
    
#     # Set up Django environment
#     project_path = Path(__file__).resolve().parent.parent.parent.parent
#     sys.path.append(str(project_path))
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texture_app.settings")
#     django.setup()
    
#     # Now import after Django setup
#     from src.ai_proxy.services.llm_service import LLMService, Message as LLMMessage
#     from src.ai_proxy.models import Conversation, Message as DBMessage
# else:
#     # Normal imports when used as a module
#     from .llm_service import LLMService, Message as LLMMessage
#     from ..models import Conversation, Message as DBMessage

from .llm_service import LLMService, Message as LLMMessage
from ..models import Conversation, Message as DBMessage



logger = logging.getLogger(__name__)


class ChatBOT:
    """Chatbot implementation using LLM service with database persistence"""

    def __init__(self,
     conversation_id: Optional[int] = None,
      llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.max_history_length = int(os.environ.get('CHATBOT_MAX_HISTORY', '20'))
        
        # Get or create conversation
        if conversation_id:
            try:
                self.conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                logger.warning(f"Conversation with id {conversation_id} not found, creating new conversation")
                self.conversation = Conversation.objects.create()
        else:
            self.conversation = Conversation.objects.create()
            
            # Add initial system message if provided
            system_prompt = os.environ.get('CHATBOT_SYSTEM_PROMPT')
            if system_prompt:
                DBMessage.objects.create(
                    conversation=self.conversation,
                    role="system",
                    content=system_prompt
                )
            else:
                raise ValueError("CHATBOT_SYSTEM_PROMPT environment variable is not set")
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history
        
        Args:
            role: The role of the message sender ('user' or 'assistant')
            content: The content of the message
        """
        # Validate role
        if role not in ["system", "user", "assistant"]:
            raise ValueError(f"Invalid role: {role}. Must be 'system', 'user', or 'assistant'")
        
        # Safely extract object details if present
        object_details = None
        if "$" in content:
            parts = content.split("$")
            if len(parts) > 1:
                object_details = parts[1]
                content = parts[0]  # Update content to only include the message part


        # Add message to database
        DBMessage.objects.create(
            conversation=self.conversation,
            role=role,
            content=content
        )
        
        # Trim history if it exceeds max length
        messages = self.conversation.messages.all()
        if messages.count() > self.max_history_length:
            # Keep system message if it exists
            system_messages = messages.filter(role="system")

            print(system_messages)
            if system_messages.exists():
                # Delete all but system messages and the most recent messages
                to_keep = list(system_messages.values_list('id', flat=True))
                to_keep.extend(list(messages.exclude(role="system").order_by('-timestamp')[:self.max_history_length-system_messages.count()].values_list('id', flat=True)))
                messages.exclude(id__in=to_keep).delete()
            else:
                # Just keep the most recent messages
                to_delete = messages.order_by('-timestamp')[self.max_history_length:]
                to_delete.delete()
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history in a format suitable for API responses
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        messages = self.conversation.messages.all()
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def clear_history(self, keep_system_prompt: bool = True) -> None:
        """Clear the conversation history
        
        Args:
            keep_system_prompt: Whether to keep the system prompt message
        """
        messages = self.conversation.messages.all()
        if keep_system_prompt:
            # Delete all non-system messages
            messages.exclude(role="system").delete()
        else:
            # Delete all messages
            messages.delete()
    
    def generate_response(self, user_message: str, temperature: Optional[float] = None) -> str:
        """Generate a response to the user message
        
        Args:
            user_message: The user's message
            temperature: Optional temperature override for this specific response
            
        Returns:
            The assistant's response text
        """
        # Safely extract object details if present
        
        
        object_details = None
        message_content = user_message
        
        if "$" in user_message:
            parts = user_message.split("$")
            if len(parts) > 1:
                message_content = parts[0]
                object_details = parts[1]  # Get the objects names
        print(object_details)
        # Add user message to history
        self.add_message("user", message_content)
   
        try:
            # Convert DB messages to LLM messages for the API call
            messages = []
            for msg in self.conversation.messages.all():
                messages.append(LLMMessage(role=msg.role, content=msg.content))
            
            # Get response from LLM service
            response = self.llm_service.create_chat_completion(
                messages=messages,
                temperature=temperature,
                object_details=object_details

            )
            
            # Extract assistant's message from response
            # The response format from the LLM service is:
            # {
            #   "message": "Received JSON data",
            #   "received_data": {
            #     "answer": "Hello! Yes, the connection is working perfectly. How can I assist you today?"
            #   },
            #   "status": "success"
            # }
            
            # Parse the JSON response if it's a string
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse response as JSON, using as-is")
            
            # Extract the answer from the received_data.answer field
            assistant_message = ""
            if isinstance(response, dict):
                received_data = response.get("received_data", {})
                if isinstance(received_data, dict):
                    assistant_message = received_data.get("answer", "")
                
            # Fallback to old extraction method if the new one didn't work # THIS NOT WORKING
            if not assistant_message:
                logger.warning("Using fallback method to extract assistant message")
                assistant_message = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Add assistant message to history
            if assistant_message:
                self.add_message("assistant", assistant_message)
            
            return assistant_message
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise


if __name__ == "__main__":
    import os
    import sys
    import django
    import json
    import time
    from pathlib import Path
    
    # Set up Django environment
    # Add the project directory to the sys.path
    project_path = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.append(str(project_path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "texture_app.settings")
    django.setup()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Test data
    test_messages = [
        "Can you help me generate a wood texture?",
        "I need a seamless brick wall texture. How can I create one?",
        "What parameters should I adjust to make a realistic metal surface?",
        "How do I create a normal map from a diffuse texture?",
        "Can you explain how to use displacement maps for added realism?"
    ]
    
    def run_test(with_db=True):
        """Run a test of the ChatBOT with or without database"""
        print(f"\n{'='*50}")
        print(f"Testing ChatBOT {'with' if with_db else 'without'} database")
        print(f"{'='*50}\n")
        
        try:
            # Create a chatbot instance
            if with_db:
                # Make sure models are imported and Django is set up
                # Models are already imported at the top level when running as __main__
                chatbot = ChatBOT()
                print(f"Created new conversation with ID: {chatbot.conversation.id}")
            else:
                # Mock the database functionality for testing without DB
                # This requires modifying the ChatBOT class or creating a subclass
                print("Database-less testing not implemented yet")
                return
            
            # Process test messages
            for i, message in enumerate(test_messages):
                print(f"\n[User Message {i+1}]: {message}")
                
                start_time = time.time()
                try:
                    response = chatbot.generate_response(user_message = message)
                    elapsed = time.time() - start_time
                    print(f"[Assistant ({elapsed:.2f}s)]: {response}")
                except Exception as e:
                    print(f"Error: {str(e)}")
            
            # Print conversation history
            print("\nConversation History:")
            history = chatbot.get_history()
            for i, msg in enumerate(history):
                print(f"[{i+1}] {msg['role']}: {msg['content'][:50]}..." if len(msg['content']) > 50 else f"[{i+1}] {msg['role']}: {msg['content']}")
            
            # Test clearing history
            if input("\nClear conversation history? (y/n): ").lower() == 'y':
                chatbot.clear_history()
                print("History cleared.")
                print(f"Remaining messages: {len(chatbot.get_history())}")
        
        except Exception as e:
            print(f"Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run the test
    run_test(with_db=True)
    
    # Optional: Run without database
    if input("\nRun test without database? (y/n): ").lower() == 'y':
        run_test(with_db=False)