"""Resolución de IP real de cliente validada contra TRUSTED_PROXIES
(SEC-T005). Compartida entre la auditoría (`notificaciones.adapters.signals`)
y el throttling de login (SEC-T002, `authentication.adapters.throttling`) —
antes de esto, cada uno habría tenido su propia lógica de confianza en
`X-Forwarded-For`, con el riesgo real de que difirieran entre sí."""

import ipaddress

from django.conf import settings


def resolver_ip_cliente(request) -> str | None:
    """Solo confía en `X-Forwarded-For` si `REMOTE_ADDR` (quien habló
    directamente con Django) está dentro de `TRUSTED_PROXIES`; de lo
    contrario, usa `REMOTE_ADDR`. Sin `TRUSTED_PROXIES` configurado
    (dev/test), nunca confía en la cabecera."""
    if request is None:
        return None

    remote_addr = request.META.get("REMOTE_ADDR")
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    trusted_proxies = getattr(settings, "TRUSTED_PROXIES", [])

    if x_forwarded_for and remote_addr and trusted_proxies:
        try:
            direccion_remota = ipaddress.ip_address(remote_addr)
        except ValueError:
            return remote_addr
        for proxy_cidr in trusted_proxies:
            try:
                if direccion_remota in ipaddress.ip_network(proxy_cidr):
                    return x_forwarded_for.split(",")[0].strip()
            except ValueError:
                continue

    return remote_addr
