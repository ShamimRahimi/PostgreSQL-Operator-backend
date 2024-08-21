from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Token
from myapp import Utilities
from django.http import JsonResponse

def login(request):
    if request.method == 'POST':
        data = Utilities.parse_json_request(request)
        if isinstance(data, JsonResponse):
            return data
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
        data = Utilities.parse_json_request(request)
        if isinstance(data, JsonResponse):
            return data
        
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

def logout(request):
    Utilities.validate_request(request, 'POST')

    token_key = request.headers.get('Authorization')
    if token_key:
        try:
            token = Token.objects.get(key=token_key)
            token.delete()
        except Token.DoesNotExist:
            return JsonResponse({"error": "Invalid token"}, status=401)

    else:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    return JsonResponse({"message": "User loged out successfully"}, status=201)
    
