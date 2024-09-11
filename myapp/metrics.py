from prometheus_client import Gauge, generate_latest
from django.http import HttpResponse
from django.conf import settings

app_version_metric = Gauge('console_app_version', 'Version of the application', ['version'])

app_version_metric.labels(version=settings.APP_VERSION).set(1)

def metrics_view(request):
    metrics = generate_latest()
    return HttpResponse(metrics, content_type="text/plain")