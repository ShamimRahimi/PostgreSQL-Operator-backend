from django.shortcuts import render
from django.http import JsonResponse
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from .models import App
from myapp import kube_client
import json

def validate_request(request, method):
    if request.method != method:
        return JsonResponse({"error": "Invalid method"}, status=405)
    if not request.user:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    return None

def parse_json_request(request):
    if len(request.body) > 1024 * 1024:
        return JsonResponse({"error": "Payload too large"}, status=400)
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
def build_response_data(app, pod_status=None):
    return {
        'id': app.id,
        'name': app.name,
        'size': app.size,
        'state': pod_status or app.state,
        'user': app.user.username,
        'creation_time': app.creation_time,
        'pod_name': f"{app.name}-{app.id}-0"
    }

def get_app_or_404(app_id, user):
    try:
        return App.objects.get(id=app_id, user=user)
    except App.DoesNotExist:
        return JsonResponse({"error": "App not found"}, status=404)
    
def read_pod_status(app, v1):
    pod_name = f"{app.name}-{app.id}-0"
    print(pod_name)
    try:
        pod = v1.read_namespaced_pod(name=pod_name, namespace="django-app")
        return pod.status.phase
    except ApiException as e:
        if e.status == 404:
            return "Deleted"