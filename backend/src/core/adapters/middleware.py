"""Middleware thread-local para exponer el request actual fuera del ciclo
vista/serializer (SEC-T005). Usado por la auditoría (`notificaciones.adapters.signals`)
para capturar la IP real del cliente en señales que no reciben el request
directamente."""

import threading

_thread_local = threading.local()


class ThreadLocalRequestMiddleware:
    """Debe ser el PRIMERO en MIDDLEWARE para capturar el request lo antes
    posible y limpiarlo lo último (evita fugas entre requests en el mismo
    hilo, p. ej. en servidores de desarrollo single-thread o en tests)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_local.request = request
        try:
            return self.get_response(request)
        finally:
            _thread_local.request = None


def get_current_request():
    return getattr(_thread_local, "request", None)
