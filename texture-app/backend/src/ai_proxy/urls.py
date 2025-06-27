from django.urls import path
from . import views
from .views import llm_views, chat_views

app_name = 'ai_proxy'

urlpatterns = [
    

    # LLM endpoints
    path('llm/generate/', llm_views.generate_text, name='generate_text'),
  
    
    # Chat endpoints
    path('chat/message/', chat_views.chat_message, name='chat_message'),
    path('chat/history/', chat_views.chat_history, name='chat_history'),
    path('chat/clear/', chat_views.clear_chat, name='clear_chat'),

    # ComfyUI endpoints
    #path('comfy/status/', views.comfy_status, name='comfy_status'),
]