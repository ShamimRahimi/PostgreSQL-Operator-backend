from django.shortcuts import render
from .models import App, Token
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, User

MAX_DATA_SIZE = 1024 
VALID_STATES = {"starting", "running", "error", "offline"}
@csrf_exempt

# Create your views here.
def create(request):
    if request.method == 'POST':
        if len(request.body) > MAX_DATA_SIZE:
            return JsonResponse({"error": "Payload too large"}, status=400)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        name = data.get("name")
        if not name or not isinstance(name, str) or len(name.strip()) == 0:
            return JsonResponse({"error": "Invalid 'name' field"}, status=400)
        
        state = data.get("state", "offline")
        if state not in VALID_STATES:
            return JsonResponse({"error": "Invalid 'name' field"}, status=400)
        
        size = data.get("size")
        if size is None or not isinstance(size, int) or size <= 0:
            return JsonResponse({"error": "Invalid 'size' field. Must be a positive integer."}, status=400)

        app = App(name=name, size=size, state=state)
        app.save()

        response_data = {
                'id': app.id,
                'name': app.name,
                'size': app.size,
                'state': app.state,
                'creation_time': app.creation_time
            }

        
        print(response_data)
        return JsonResponse(response_data, status=200)
    return JsonResponse({"error": "Invalid method"}, status=405)


def dispatcher(request, app_id):
    if request.method == 'GET':
        try:
            app = App.objects.get(id=app_id)
        except App.DoesNotExist:
            return JsonResponse({"error": "App not found"}, status=404)
        
        response_data = {
            'id': app.id,
            'name': app.name,
            'size': app.size,
            'state': app.state,
            'creation_time': app.creation_time
        }

        return JsonResponse(response_data, status=200)
    
    elif request.method == 'PUT':
        app = App.objects.get(id=app_id)
        data = json.loads(request.body)
        if data.get("size") is None or not isinstance(data.get("size"), int) or data.get("size") <= 0:
            return JsonResponse({"error": "Invalid 'size' field. Must be a positive integer."}, status=400)
        
        app.size = data.get("size")
        app.save()

        response_data = {
            'id': app.id,
            'name': app.name,
            'size': app.size,
            'state': app.state,
            'creation_time': app.creation_time,
        }

        return JsonResponse(response_data, status=200)

    elif request.method == 'DELETE':
        app = App.objects.get(id=app_id)
        app.delete()
        return JsonResponse({})

    else: return JsonResponse({"error": "Invalid method"}, status=405)


def list(request):
    if request.method == 'GET':
        apps = App.objects.all()

        results = [
            {
                'id': app.id,
                'name': app.name,
                'size': app.size,
                'state': app.state,
                'creation_time': app.creation_time,
            }
            for app in apps
        ]

        return JsonResponse({"results": results})
    return JsonResponse({"error": "Invalid method"}, status=405)


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
    