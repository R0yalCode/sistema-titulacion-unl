"""Middleware de cabeceras de seguridad adicionales (SEC-T001, DEC-010).

No depende de ninguna librería externa: solo añade las cabeceras CSP que
Django no gestiona de forma nativa (a diferencia de
`django.middleware.security.SecurityMiddleware`, que ya cubre HSTS,
X-Content-Type-Options y el redirect HTTPS).
"""

from django.conf import settings


class ContentSecurityPolicyMiddleware:
    """Aplica `Content-Security-Policy` (bloqueante, directivas mínimas) y
    `Content-Security-Policy-Report-Only` (resto de directivas, sin
    bloquear) según los valores definidos en settings."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        blocking = getattr(settings, "CSP_BLOCKING_POLICY", None)
        if blocking:
            response["Content-Security-Policy"] = blocking

        report_only = getattr(settings, "CSP_REPORT_ONLY_POLICY", None)
        if report_only:
            response["Content-Security-Policy-Report-Only"] = report_only

        return response
