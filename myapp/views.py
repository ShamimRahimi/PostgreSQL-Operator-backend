from django.shortcuts import render
from .models import App
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt


# Create your views here.
def create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get("name")
        state = data.get("state", "offline")
        size = data.get("size")
        print(name)

        app = App(name=name, size=size, state=state)
        app.save()

        response_data = {
                'id': app.id,
                'name': app.name,
                'size': app.size,
                'state': app.state,
                'creation_time': app.creation_time
            }

        return JsonResponse(response_data, status=200)
    return JsonResponse({"error": "Invalid method"}, status=405)


def dispatcher(request, app_id):
    if request.method == 'GET':
        app = App.objects.get(id=app_id)

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

# def update(request, app_id):
#     if request.method == 'PUT':
       
#     # return JsonResponse({"error": "Invalid method"}, status=405)

# @csrf_exempt
# def delete(request, app_id):
#     if request.method == 'DELETE':
        
#     # return JsonResponse({"error": "Invalid method"}, status=405)

