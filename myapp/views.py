from django.shortcuts import render
from kubernetes import client, config
from myapp import kube_client, Utilities, models
from .models import App
from django.http import JsonResponse
from kubernetes.client.exceptions import ApiException

MAX_DATA_SIZE = 1024 * 1024

config.load_kube_config(config_file="~/cluster-config.yaml")
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

def create(request):
    if (error_response := Utilities.validate_request(request, 'POST')):
        return error_response
        
    if len(request.body) > MAX_DATA_SIZE:
        return JsonResponse({"error": "Payload too large"}, status=400)
    
    data = Utilities.parse_json_request(request)
    if isinstance(data, JsonResponse):
        return data

    name = data.get("name")
    state = data.get("state", "offline")
    size = data.get("size")

    if not name or not isinstance(size, int) or size <= 0:
        return JsonResponse({"error": "Invalid input fields"}, status=400)

    app = App(name=name, size=size, state=state, user=request.user)
    app.save()
    kube_client.create_pod(app)

    return JsonResponse(Utilities.build_response_data(app), status=200)


def dispatcher(request, app_id):
    if (error_response := Utilities.validate_request(request, request.method)):
        return error_response

    app = Utilities.get_app_or_404(app_id, request.user)
    if isinstance(app, JsonResponse):
        return app
    
    if request.method == 'GET':
        pod_status = Utilities.read_pod_status(app, v1)
        if isinstance(pod_status, JsonResponse):
            return pod_status
            
        return JsonResponse(Utilities.build_response_data(app, pod_status), status=200)
    
    elif request.method == 'PUT':
        data = Utilities.parse_json_request(request)
        if isinstance(data, JsonResponse):
            return data
        
        pvc_name = f"{app.name}-{app.id}-pvc"
        pvc = v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace="django-app")
        pvc.spec.resources.requests['storage'] = f'{data.get("size")}Gi'
        v1.patch_namespaced_persistent_volume_claim(name=pvc_name, namespace="django-app", body=pvc)

        app.size = data.get("size")
        app.save()

        return JsonResponse(Utilities.build_response_data(app), status=200)


    elif request.method == 'DELETE':
        try:
            apps_v1.delete_namespaced_stateful_set(namespace="django-app", name=f"{app.name}-{app.id}")
            v1.delete_namespaced_persistent_volume_claim(namespace="django-app", name=f"{app.name}-{app.id}-pvc")
        except ApiException as e:
            if e.status == 404:
                return JsonResponse({"error": "Pod or PVC does not exist."}, status=400)

        app.delete()
        return JsonResponse({}, status=204)

    return JsonResponse({"error": "Invalid method"}, status=405)


def list(request):
    if (error_response := Utilities.validate_request(request, 'GET')):
        return error_response
        
    apps = App.objects.filter(user=request.user)
    results = []
    for app in apps:
        pod_status = Utilities.read_pod_status(app, v1)
        if isinstance(pod_status, JsonResponse):
            continue
        results.append(Utilities.build_response_data(app, pod_status))

    
    return JsonResponse({"results": results}, status=200)