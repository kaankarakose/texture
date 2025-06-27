## GET POST for LLM
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services.llm_service import LLMService, Message
import json
# Initialize the service once
llm_service = LLMService()

@api_view(['POST'])
def generate_text(request):

    """
    Endpoint to generate text from the LLM service
    """
    try:
        # Extract data from request
        data = request.data
        user_message = data.get('message', '')
        
        # Create message object
        messages = [Message(role="user", content=user_message)]
        
        # Optional parameters
        system_prompt = data.get('system_prompt')
        temperature = data.get('temperature')
        max_tokens = data.get('max_tokens')
        
        
        # Call LLM service
        response = llm_service.create_chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return Response(response)
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)