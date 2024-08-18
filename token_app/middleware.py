from django.http import JsonResponse
from .models import Token

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token_key = request.headers.get('Authorization')
        if token_key:
            try:
                token = Token.objects.get(key=token_key)
                if token.is_expired():
                    return JsonResponse({"error": "Token has expired"}, status=401)
                request.user = token.user
            except Token.DoesNotExist:
                return JsonResponse({"error": "Invalid token"}, status=401)
        else:
            request.user = None

        response = self.get_response(request)
        return response