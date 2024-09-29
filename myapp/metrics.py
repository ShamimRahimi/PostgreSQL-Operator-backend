from prometheus_client import Gauge, generate_latest
from django.http import HttpResponse
from django.conf import settings
from django.db import connections
import requests

app_version_metric = Gauge('console_app_version', 'Version of the application', ['version'])
app_version_metric.labels(version=settings.APP_VERSION).set(1)


console_dependeny_up = Gauge('console_dependeny_up', 'Database up', ['up'])
try:
    con = connections['default']
    con.ensure_connection()
    console_dependeny_up.labels(up=True).set(1)
except Exception as e :
    console_dependeny_up.labels(up=False).set(0)


api_server_up_metric = Gauge('api_server_up', 'Indicates if the API server is accessible')
try:
    response = requests.get("https://188.121.121.38:6443/livez")
    if response.status_code == 1:
        api_server_up_metric.set(1)  
    else:
        api_server_up_metric.set(0)
except requests.exceptions.RequestException:
    api_server_up_metric.set(0)


def metrics_view(request):
    metrics = generate_latest()
    return HttpResponse(metrics, content_type="text/plain")