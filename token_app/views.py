from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Token
import json
from django.http import HttpResponse, JsonResponse

# Create your views here.
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            token = Token.generate_token(user)

            return JsonResponse({"token": token.key}, status=200)
        
        return JsonResponse({"error": "Invalid user"}, status=401)
    
    return JsonResponse({"error": "Invalid method"}, status=405)


def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "User already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        user.save()
        return JsonResponse({"message": "User created successfully"}, status=201)
    
    return JsonResponse({"error": "Invalid method"}, status=405)