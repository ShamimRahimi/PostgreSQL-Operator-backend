from django.shortcuts import render
from kubernetes import client, config
from myapp import kube_client
from .models import App
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# import kube_client

MAX_DATA_SIZE = 1024 
VALID_STATES = {"starting", "running", "error", "offline"}

# Create your views here.
@csrf_exempt
def create(request):
    if request.method == 'POST':
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
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

        app = App(name=name, size=size, state=state, user=request.user)
        app.save()
        state = kube_client.create_pod(app)
        print(state)

        response_data = {
                'id': app.id,
                'name': app.name,
                'size': app.size,
                'state': app.state,
                'user': request.user.username,
                'creation_time': app.creation_time
            }

        
        print(response_data)
        return JsonResponse(response_data, status=200)
    return JsonResponse({"error": "Invalid method"}, status=405)


def dispatcher(request, app_id):
    if request.method == 'GET':
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        if App.objects.filter(id=app_id, user=request.user).exists():
            app = App.objects.get(id=app_id, user=request.user)
        else:
            return JsonResponse({"error": "App not found"}, status=404)
        
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=f"{app.name}-{app.id}", namespace="django-app")

        response_data = {
            'id': app.id,
            'name': app.name,
            'size': app.size,
            'state': pod.status.phase,
            'user': app.user.username,
            'creation_time': app.creation_time,
            'pod name': f"{app.name}-{app.id}"
        }

        return JsonResponse(response_data, status=200)
    
    elif request.method == 'PUT':
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        if App.objects.filter(id=app_id, user=request.user).exists():
            app = App.objects.get(id=app_id, user=request.user)
        else:
            return JsonResponse({"error": "App not found"}, status=404)
        
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
            'user': app.user.username,
            'creation_time': app.creation_time,
        }

        return JsonResponse(response_data, status=200)

    elif request.method == 'DELETE':
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        if App.objects.filter(id=app_id, user=request.user).exists():
            app = App.objects.get(id=app_id, user=request.user)
        else:
            return JsonResponse({"error": "App not found"}, status=404)
        
        app.delete()
        return JsonResponse({})

    return JsonResponse({"error": "Invalid method"}, status=405)


def list(request):
    if request.method == 'GET':
        if not request.user:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        apps = App.objects.filter(user=request.user)
        results = [
            {
                'id': app.id,
                'name': app.name,
                'size': app.size,
                'state': app.state,
                'user': app.user.username,
                'creation_time': app.creation_time,
            }
            for app in apps
        ]

        return JsonResponse({"results": results})
    return JsonResponse({"error": "Invalid method"}, status=405)