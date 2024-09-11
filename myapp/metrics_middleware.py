from prometheus_client import Counter
from prometheus_client import start_http_server
import time

REQUEST_COUNT = Counter('django_http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint'])

class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        method = request.method
        endpoint = request.path
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

        response = self.get_response(request)
        return response