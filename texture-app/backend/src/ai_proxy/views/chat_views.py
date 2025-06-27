from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services.chat_service import ChatBOT
from ..models import Conversation
import logging
import json

logger = logging.getLogger(__name__)

@api_view(['POST'])
def chat_message(request):
    """
    Endpoint to send a message to the chatbot and get a response
    """
    try:
        data = request.data
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=400)
        
        # Optional parameters
        temperature = data.get('temperature')
        
        # Create or get chatbot instance
        chatbot = ChatBOT(conversation_id=conversation_id)
        
        # Generate response
        assistant_response = chatbot.generate_response(
            user_message=user_message,
            temperature=temperature
        )
        
        return Response({
            "response": assistant_response,
            "history": chatbot.get_history(),
            "conversation_id": chatbot.conversation.id
        })
    
    except Exception as e:
        logger.error(f"Error in chat_message: {str(e)}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def chat_history(request):
    """
    Endpoint to get the current chat history
    """
    try:
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            # Return list of all conversations for a single-user app
            conversations = Conversation.objects.all().order_by('-updated_at')
            
            return Response({
                "conversations": [
                    {
                        "id": conv.id,
                        "title": conv.title,
                        "created_at": conv.created_at,
                        "updated_at": conv.updated_at
                    } for conv in conversations
                ]
            })
        
        # Get specific conversation history
        chatbot = ChatBOT(conversation_id=conversation_id)
        return Response({
            "conversation_id": chatbot.conversation.id,
            "history": chatbot.get_history()
        })
    
    except Exception as e:
        logger.error(f"Error in chat_history: {str(e)}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def clear_chat(request):
    """
    Endpoint to clear the chat history
    """
    try:
        data = request.data
        conversation_id = data.get('conversation_id')
        keep_system_prompt = data.get('keep_system_prompt', True)
        
        if not conversation_id:
            return Response({"error": "conversation_id is required"}, status=400)
        
        chatbot = ChatBOT(conversation_id=conversation_id)
        chatbot.clear_history(keep_system_prompt=keep_system_prompt)
        
        return Response({
            "message": "Chat history cleared",
            "conversation_id": chatbot.conversation.id,
            "history": chatbot.get_history()
        })
    
    except Exception as e:
        logger.error(f"Error in clear_chat: {str(e)}")
        return Response({"error": str(e)}, status=500)
