"""Endpoint de healthcheck (SEC-T001). Sin autenticación: solo confirma
que el proceso Django responde; no expone información del sistema."""

from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})
