from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.



@api_view(['GET'])
def api_root(request):
    """
    Root endpoint
    """

    return Response({
        'hello': reverse('hello_world', request=request)
    })


@api_view(['GET'])
def hello_world(request):
    """
    A simple test endpoint to verify the API is working
    """
    return Response({"message": "Hello, world!"})
