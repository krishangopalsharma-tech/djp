# Path: backend/core/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"status": "ok"})
