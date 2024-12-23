from .models import ApiRequestLog

class ApiLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            ApiRequestLog.objects.create(
                user=request.user,
                endpoint=request.path,
                method=request.method,
            )
        return response
